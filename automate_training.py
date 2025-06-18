#!/usr/bin/env python3
"""
Script pentru automatizarea antrenării modelului LightFM
Rulează acest script periodic pentru a menține modelul actualizat
"""

import os
import sys
import subprocess
import logging
from datetime import datetime

# Configurare logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training_automation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def run_django_command(command, args=None):
    """Rulează o comandă Django"""
    try:
        cmd = ['python', 'manage.py', command]
        if args:
            cmd.extend(args)
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            logger.info(f"Comanda '{command}' executată cu succes")
            return True
        else:
            logger.error(f"Eroare la executarea comenzii '{command}': {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Excepție la executarea comenzii '{command}': {e}")
        return False

def check_model_status():
    """Verifică statusul modelului"""
    logger.info("Verificare status model...")
    return run_django_command('schedule_model_training', ['--check-only'])

def force_model_training():
    """Forțează antrenarea modelului"""
    logger.info("Forțare antrenare model...")
    return run_django_command('schedule_model_training', ['--force'])

def improve_preferences():
    """Îmbunătățește preferințele"""
    logger.info("Îmbunătățire preferințe...")
    return run_django_command('improve_preferences')

def export_data():
    """Exportă datele pentru Colab"""
    logger.info("Export date pentru Colab...")
    return run_django_command('export_colab_data_improved')

def main():
    """Funcția principală"""
    logger.info("=== ÎNCEPE AUTOMATIZAREA ANTENĂRII ===")
    
    # 1. Verifică statusul modelului
    if not check_model_status():
        logger.error("Nu s-a putut verifica statusul modelului")
        return False
    
    # 2. Îmbunătățește preferințele
    if not improve_preferences():
        logger.error("Nu s-au putut îmbunătăți preferințele")
        return False
    
    # 3. Exportă datele
    if not export_data():
        logger.error("Nu s-au putut exporta datele")
        return False
    
    # 4. Forțează antrenarea (opțional)
    # Uncomment pentru a forța antrenarea automat
    # if not force_model_training():
    #     logger.error("Nu s-a putut forța antrenarea")
    #     return False
    
    logger.info("=== AUTOMATIZAREA COMPLETĂ ===")
    logger.info("Următorii pași manuali:")
    logger.info("1. Upload colab_data_IMPROVED.json în Google Colab")
    logger.info("2. Rulează codul de antrenare")
    logger.info("3. Descarcă lightfm_model.pkl")
    logger.info("4. Pune-l în directorul rădăcină al proiectului")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 