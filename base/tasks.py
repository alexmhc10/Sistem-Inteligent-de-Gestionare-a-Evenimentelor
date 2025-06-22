from sistem_inteligent_de_gestionare_a_evenimentelor.celery import app
import logging
from base.management.commands.optimise_events import run_genetic_optimization 
from base.models import *
logger = logging.getLogger(__name__)
from celery import shared_task
from django.core.mail import EmailMultiAlternatives

class DummyOut:
    def write(self, s):
        logger.info(s.strip())
        
class DummyStyle:
    def __getattr__(self, name):
        return lambda x: x

@app.task(bind=True)
def run_optimization_task(self):
    logger.info("Starting optimization task via Celery...")

    dummy_out = DummyOut()
    dummy_style = DummyStyle()

    try:
        run_genetic_optimization(dummy_out, dummy_style)
        logger.info("Optimization task completed successfully.")
        return "Optimization task completed successfully."
    except Exception as e:
        logger.error(f"Optimization task failed: {e}", exc_info=True)
        raise
@app.task(bind=True)
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