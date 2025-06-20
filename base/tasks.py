from sistem_inteligent_de_gestionare_a_evenimentelor.celery import app
import logging
from base.management.commands.optimise_events import run_genetic_optimization 

logger = logging.getLogger(__name__)

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
