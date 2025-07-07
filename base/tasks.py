import logging
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from datetime import timedelta
from django.core.management import call_command
from base.models import *
logger = logging.getLogger(__name__)

class DummyOut:
    def write(self, s):
        logger.info(s.strip())
        
class DummyStyle:
    def __getattr__(self, name):
        return lambda x: x

@shared_task
def run_optimization_task():
    logger.info("Starting optimization task via Celery...")
    try:
        call_command('optimise_events')
        logger.info("Optimization task completed successfully.")
        return "Optimization task completed successfully."
    except Exception as e:
        logger.error(f"Optimization task failed: {e}", exc_info=True)
        raise

@shared_task(bind=True)
def calculate_monthly_profit_task():

    logger.info("Începerea task-ului de calcul al profitului lunar.")

    try:
        budget = Budget.objects.first()

        if not budget:
            logger.warning("Niciun obiect Budget găsit în baza de date. Nu se poate calcula profitul.")
            return

        budget.calc_profit()

        logger.info(f"Task de calcul profit lunar executat cu succes. Profit calculat: {budget.profit}")

    except Exception as e:
        logger.error(f"Eroare critică la executarea task-ului calculate_monthly_profit_task: {e}", exc_info=True)


@shared_task
def send_email_task(subject, text_body, html_body, to):
    msg = EmailMultiAlternatives(subject, text_body, None, [to])
    msg.attach_alternative(html_body, "text/html")
    msg.send()


@shared_task(bind=True)
def prepare_event_face_encodings(self, event_id):
    logger.info(f"[ENCODING] Se pregatesc encodarile faciale pentru evenimentul #{event_id}")
    try:
        from base.utils import get_encoded_faces
        faces = get_encoded_faces(event_id)
        logger.info(f"[ENCODING] Am pregatit {len(faces)} encodari pentru evenimentul #{event_id}.")
        return {
            "status": "success",
            "event_id": event_id,
            "encodings": len(faces)
        }
    except Exception as e:
        logger.error(f"[ENCODING] Eroare la generarea encodariilor pentru evenimentul #{event_id}: {e}", exc_info=True)
        raise


@shared_task(bind=True)
def prepare_encodings_upcoming_events(self):
    logger.info("[ENCODING] Verificare evenimente care incep in curand pentru generarea encodariilor")
    try:
        from base.models import Event
        now = timezone.now()
        window_start = now
        window_end = now + timedelta(minutes=15)
        upcoming_events = Event.objects.filter(event_date=now.date(), event_time__gte=window_start.time(), event_time__lte=window_end.time())
        for event in upcoming_events:
            prepare_event_face_encodings.delay(event.id)
        logger.info(f"[ENCODING] Programate encodaari pentru {upcoming_events.count()} evenimente.")
        return upcoming_events.count()
    except Exception as e:
        logger.error(f"[ENCODING] Eroare la task-ul periodic de encodari: {e}", exc_info=True)
        raise

@shared_task(bind=True)
def train_lightfm_model(self, show_progress=False, threshold=30):
    from base.models import RecommenderStatus, MenuRating

    status = RecommenderStatus.get()
    current_count = MenuRating.objects.count()

    diff = current_count - status.last_rating_count
    if diff < threshold:
        logger.info(
            f"[RECOMMENDER] Doar {diff} ratinguri noi (<{threshold}) – nu se antreneaza."
        )
        return {"status": "skipped", "new_ratings": diff}

    logger.info(
        f"[RECOMMENDER] Gasit {diff} ratinguri noi – re antreneazaLightFM"
    )
    try:
        verbosity = 2 if show_progress else 0
        call_command("train_recommender", verbosity=verbosity, progress=show_progress)

        status.last_trained_at = timezone.now()
        status.last_rating_count = current_count
        status.save(update_fields=["last_trained_at", "last_rating_count"])

        logger.info("[RECOMMENDER] Model LightFM antrenat si salvat cu succes.")
        return {"status": "success", "new_ratings": diff}
    except Exception as e:
        logger.error(
            f"[RECOMMENDER] Eroare la re-antrenarea modelului: {e}", exc_info=True
        )
        raise