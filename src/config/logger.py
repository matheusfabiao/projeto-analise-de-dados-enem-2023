import logging


def setup_logging():
    """
    Configura o logger para registrar mensagens com n vel de detalhe
    INFO e formato de data e hora "%Y-%m-%d %H:%M:%S".

    Retorna um objeto logger configurado.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logger = logging.getLogger(__name__)
    return logger


logger = setup_logging()
