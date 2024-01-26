from loguru import logger

logger.add("logs/logfile.log", rotation="50 MB", level="ERROR")
