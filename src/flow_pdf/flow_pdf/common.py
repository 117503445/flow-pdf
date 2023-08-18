import logging
from htutil import file
from pathlib import Path


def create_main_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler()

    formatter = logging.Formatter(
        "%(asctime)s,%(msecs)03d [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d:%H:%M:%S",
    )
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    return logger


def create_file_logger(file_output: Path):
    logger = logging.getLogger("main")
    logger.setLevel(logging.DEBUG)


    file_handler = logging.FileHandler(file_output)

    formatter = logging.Formatter(
        "%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d:%H:%M:%S",
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger


file_git = Path(__file__).parent / "git.txt"
if file_git.exists():
    version = file.read_text(file_git)
else:
    version = 'dev'
