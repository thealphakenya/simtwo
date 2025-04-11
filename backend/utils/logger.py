import logging

def setup_logger(name='app', level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger