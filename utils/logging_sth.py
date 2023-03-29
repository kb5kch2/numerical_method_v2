from .logging_custom import *
from .config import Config
import os
from datetime import datetime

current_time = datetime.now()
current_time = current_time.strftime("%y%m%d_%H%M%S")


def pretty_text(text):
    """
    필요해지면 구현하기
    """
    pass

def make_log_folder(_dir):
    try:
        if not os.path.exists(_dir):
            os.makedirs(_dir)
    except OSError:
        print ('Error: Creating directory;', _dir)

def duplicate_config_file(cfg: Config, _dir):
    logger = CustomLogger('duplicate_config_file')
    name = cfg.cfg_dict['calculator']['type']
    make_log_folder(_dir)
    logger.add_file_handler(level='INFO', filename=_dir+f'{name}_{current_time}.py')
    logger = logger.get_logger()
    logger.info(cfg.cfg_text)
