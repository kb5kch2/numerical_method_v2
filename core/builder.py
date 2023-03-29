import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utils.storage import Storage
from utils.config import ConfigDict

METHODS = Storage('methods')

def build_operator(cfg: ConfigDict):
    return METHODS.build(cfg)
