import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utils.config import Config
from utils.logging_sth import duplicate_config_file
from core.operate import operate
from datetime import datetime
import argparse

class ArgumentParser_ChangeErrorMessage(argparse.ArgumentParser):
    """
    에러 메시지를 변경하기 위해 class를 상속함.
    """
    def error(self, msg):
        print('============================================================\n'
              '|  config 파일 경로가 입력되지 않았습니다.                 |\n'
              '|      사용 예시;                                          |\n'
              '|      $ python tools/main.py ./configs/newton_raphson.py  |\n'
              '============================================================')
        sys.exit(1)

def parse_args():
    parser = ArgumentParser_ChangeErrorMessage(description='Analyze by numerical method.')
    parser.add_argument('config', help='path of a python file containing the specific method configuration')
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    cfg = Config.fromfile(args.config)

    # set logging directory
    current_time = datetime.now()
    current_time = current_time.strftime("%y%m%d_%H%M%S")
    _dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),f'logs/{cfg.calculator.type}_{current_time}')+'/'
    cfg.calculator._dir = _dir # 이후 logging에 사용
    duplicate_config_file(cfg, _dir)

    # do operate
    operate(cfg)

if __name__ == '__main__':
    main()