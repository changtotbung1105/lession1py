import logging
import sys

def setup_logger():
    """Configures logging to both a file and the console."""
    logger = logging.getLogger("ETL_Pipeline")
    logger.setLevel(logging.INFO)

    # Avoid adding duplicate handlers if logger is already initialized
    if not logger.handlers:
        # 1. File Handler (Appends logs to pipeline.log)
        file_handler = logging.FileHandler("pipeline.log", encoding="utf-8")
        file_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(module)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # 2. Console Handler (Outputs to VS Code Terminal)
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter("%(asctime)s [%(levelname)s] - %(message)s", datefmt="%H:%M:%S")
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger

# Create a singleton logger instance
logger = setup_logger()