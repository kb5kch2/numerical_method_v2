# from mmcv (https://github.com/open-mmlab/mmcv/blob/master/mmcv/utils/config.py)

"""
HOW TO USE

1. config 파일을 생성하여 dict로 작성
    예시)
        [.../configs/config.py]에서
        @ numerical_method_v2/core/methods/newton_raphson.py
        >>> calculator = dict(
        >>>     type = 'newton_raphson',
        >>>     ...            )
    주의)
        - storage.py에서 각 class는 "type" key에 적힌 값을 가져오도록 했으니 
          class 이름은 "type" key에 적기

2. config 파일로부터 Config.fromfile로 ConfigDict 객체 생성하고 main 함수에 전달하기
    예시)
        [커맨드로 실행할 main 파일]에서
        @ numerical_method_v2/tools/main.py
        >>> from utils.config import Config
        >>> from core.operate import operate
        >>> cfg_path = "C:/Users/dohun/Desktop/python/numerical_method_v2/configs/newton_raphson.py"
        >>> cfg = Config.fromfile(cfg_path)
        >>> operate(cfg) # ConfigDict 객체 전달

3. 쿼리 형식으로 사용
    예시)
        [위 예시의 operate가 정의된 파일]에서
        @ numerical_method_v2/core/operate.py
        >>> def operate(cfg):
        >>>     cal = cfg.calculator
        >>>     ...
"""

import ast
import os.path as osp
import tempfile
import platform
import shutil
import sys
import types
from importlib import import_module
from pathlib import Path
from addict import Dict

class ConfigDict(Dict):

    def __missing__(self, name):
        raise KeyError(name)

    def __getattr__(self, name):
        try:
            value = super().__getattr__(name)
        except KeyError: # dict에 해당하는 key가 없을 때 에러 반환
            ex = AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        except Exception as e: # 예외가 발생했을 때 에러 반환
            ex = e
        else:
            return value
        raise ex

class Config:

    @staticmethod
    def _validate_py_syntax(filename):
        with open(filename, encoding='utf-8') as f:
          # Setting encoding explicitly to resolve coding issue on windows
            content = f.read()
        try:
            ast.parse(content)
        except SyntaxError as e:
            raise SyntaxError(f'There are syntax errors in config file {filename}: {e}')

    @staticmethod
    def _file2dict(filename):
        filename = osp.abspath(osp.expanduser(filename)) # 절대경로로 바꿔준다.
        fileExtname = osp.splitext(filename)[1] # split extension. 확장자 알려주는 함수

        with tempfile.TemporaryDirectory() as temp_config_dir:
            temp_config_file = tempfile.NamedTemporaryFile(dir=temp_config_dir, suffix=fileExtname)
            if platform.system() == 'Windows': temp_config_file.close()
            temp_config_name = osp.basename(temp_config_file.name) # 임시파일의 이름 (random name)
            shutil.copyfile(filename, temp_config_file.name) # config 파일 경로인 filename 내용을 임시파일로 복사

            if filename.endswith('.py'):
                temp_module_name = osp.splitext(temp_config_name)[0]
              # 임시파일을 모듈로 import하기
                sys.path.insert(0, temp_config_dir)
                Config._validate_py_syntax(filename)
                mod = import_module(temp_module_name)
                sys.path.pop(0)
                
                cfg_dict = {
                    name: value
                    for name, value in mod.__dict__.items()
                  # 저작권 메시지 출력 삭제 (이 코드가 없을 때 왜 저작권 메시지가 뜨는지는 모르겠다)
                    if not name.startswith('__')
                    and not isinstance(value, types.ModuleType)
                    and not isinstance(value, types.FunctionType)                    
                }

              # delete imported module
                del sys.modules[temp_module_name]
          # close temp file
            temp_config_file.close()

        # cfg_text = filename + '\n\n'
        cfg_text = ''
        with open(filename, encoding='utf-8') as f:
            cfg_text += f.read() # cfg_text에 config 파일 이름과 내용이 들어간다
        return cfg_dict, cfg_text

    @staticmethod
    def fromfile(filename):
        cfg_dict, cfg_text = Config._file2dict(filename)
        return Config(cfg_dict, cfg_text=cfg_text, filename=filename)

    def __init__(self, cfg_dict=None, cfg_text=None, filename=None):

        # To duplicate cfg as a log.
        self.cfg_dict = cfg_dict
        self.cfg_text = cfg_text

        if isinstance(filename, Path):
            filename = str(filename)

        super().__setattr__('_cfg_dict', ConfigDict(cfg_dict))
        """
        Dict를 사용해서 "cfg.model.type"과 같은 형식을 사용할 수 있게 해주는 코드.
        self._cfg_dict = ConfigDict(cfg_dict)와 같은 기능을 하지만 https://alphahackerhan.tistory.com/44 (지연 속성)를 보니 무한 참조 오류가 나올 수도 있을 것 같다.
        """

    # cfg.model.type과 같은 형식을 사용할 수 있게 해주는 코드
    def __getattr__(self, name):
        return getattr(self._cfg_dict, name)
