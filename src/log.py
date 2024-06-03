import logging

FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
ALCHEMY_ECHO = True

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set the logger to the lowest level, it will be filtered by handlers

# Create a file handler for logging WARNING and higher levels
file_handler = logging.FileHandler("bot_errors.log")
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(logging.Formatter(FORMAT))


# Create a stream handler for logging INFO and higher levels
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(logging.Formatter(FORMAT))

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)


