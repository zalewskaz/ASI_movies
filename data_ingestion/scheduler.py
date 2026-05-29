import time
import logging
import schedule
from data_ingestion.data_pipeline import run_pipeline

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    logging.info("Uruchomiono Moduł Akwizycji Danych (Data Ingestion Service)...")
    
    logging.info("Pierwsze uruchomienie sekwencyjne przy starcie systemu:")
    run_pipeline()
    
    schedule.every().week.do(run_pipeline)
    
    while True:
        schedule.run_pending()
        time.sleep(1)