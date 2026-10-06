import schedule
import time
from main import run_pipeline
from src.logger_config import logger

def scheduled_job():
    logger.info("Triggering scheduled ETL pipeline run...")
    try:
        run_pipeline()
    except Exception as e:
        logger.error(f"Scheduled job crashed: {e}")

# Schedule settings
# Run every 5 minutes
schedule.every(5).minutes.do(scheduled_job)

# Alternative scheduling examples:
# schedule.every().hour.do(scheduled_job)
# schedule.every().day.at("01:00").do(scheduled_job)

if __name__ == "__main__":
    logger.info("Scheduler service started. Press Ctrl+C to exit.")
    
    # Initial execution on startup
    scheduled_job()

    # Continuous polling loop
    while True:
        schedule.run_pending()
        time.sleep(1)