import logging

FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
ALCHEMY_ECHO = True

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set the logger to the lowest level, it will be filtered by handlers

file_handler = logging.FileHandler("bot_errors.log")
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(logging.Formatter(FORMAT))

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(logging.Formatter(FORMAT))

logger.addHandler(file_handler)
logger.addHandler(stream_handler)
