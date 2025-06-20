# your_app/tasks.py

from celery import shared_task
from django.core.management import call_command # Opțional, dacă vrei să apelezi comanda de management
import io
import sys
import logging

logger = logging.getLogger(__name__) # Obține un logger Django pentru a înregistra mesaje

# Importă funcția principală a algoritmului genetic.
# Vei extrage logica din metoda 'handle' a comenzii de management într-o funcție separată.
# Presupunem că ai mutat logica de bază în 'run_genetic_optimization'.
# Exemplu: din base/management/commands/optimize_events.py
from base.management.commands.optimise_events import run_genetic_optimization 

# Clase dummy pentru a simula stdout și stilul comenzii de management
# deoarece Celery nu are o consolă directă la care să scrie.
class DummyOut:
    def write(self, s):
        # Trimite la logger-ul Django sau pur și simplu ignoră
        logger.info(s.strip()) # Folosește strip() pentru a elimina newline-uri de la self.stdout.write
        
class DummyStyle:
    def __getattr__(self, name):
        return lambda x: x # Funcție care returnează pur și simplu intrarea (nu aplică stil)

@shared_task
def run_optimization_task():
    """
    Sarcina Celery care declanșează algoritmul de optimizare.
    """
    logger.info("Starting optimization task via Celery...")
    
    # Creează instanțe dummy pentru stdout și style
    dummy_out = DummyOut()
    dummy_style = DummyStyle()

    try:
        # Apelează funcția principală a algoritmului tău genetic
        run_genetic_optimization(dummy_out, dummy_style)
        logger.info("Optimization task completed successfully.")
        return "Optimization task completed successfully."
    except Exception as e:
        logger.error(f"Optimization task failed: {e}", exc_info=True)
        # Ridică excepția pentru ca Celery să marcheze sarcina ca eșuată
        raise