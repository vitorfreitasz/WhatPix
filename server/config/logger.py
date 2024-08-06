import logging

def setup_logger(name='LUCIA api', log_file='api.log', level=logging.INFO):
    """
    Configura o logger com o nome e nível especificados.
    """
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    
    return logger

# Chamada para configurar o logger principal
logger = setup_logger()
