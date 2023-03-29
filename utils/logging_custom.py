# https://docs.python.org/3/library/logging.html

import logging
from logging import handlers as loghdlrs
from contextlib import contextmanager
import datetime as dt
from datetime import datetime

current_time = datetime.now()
current_time = current_time.strftime("%y%m%d_%H%M%S")

def log_fn_name_n_args(func):
    """
    # https://jh-bk.tistory.com/40
    데코레이터로 사용해 함수의 이름과 args, kwargs를 logging한다.

    Example:
        @log_fn_name_n_args
        def bar(a, b, c=None):
            print("Inside bar")
        bar(1, 2, c=3)
    """    
    def new_func(*args, **kwargs):        
        logger = logging.getLogger('log_fn_name_n_args')
        logger.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        logger.addHandler(stream_handler)
        logger.debug(f'%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n'
                     f' calling   :   {func.__name__}\n'
                     f'    args   :   {args}\n'
                     f'  kwargs   :   {kwargs}\n'
                     f'%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
        return func(*args, **kwargs)
    return new_func

@contextmanager
def change_logging_level_shortly(level):
    """
    TODO
        어떤 logger의 어떤 handler의 level을 바꿀 수 있게 바꾸기
    
    # https://jh-bk.tistory.com/40
    with 구문으로 함수의 logging level을 잠시 바꾼다.

    Example:
        def foo_function():
            logging.debug("Debug info line")
            logging.error("Error info line!")
            logging.debug("Additional debug info line")

        logging.getLogger().setLevel(logging.WARNING)
        foo_function()
        print('---------')
        with change_logging_level_shortly(logging.DEBUG):
            foo_function()
    """
    logger = logging.getLogger()
    old_level = logger.getEffectiveLevel()
    print(old_level)
    logger.setLevel(level) # logging level을 내가 지정한 args "level"로 설정
    try:
        yield              # 실행
    finally:
        logger.setLevel(old_level) # 원상복구

class DisableLogger:
    """
    # https://jh-bk.tistory.com/40
    특정 level 이하의 logging을 무시한다.

    Example:
        def foo_function():
            logging.getLogger().setLevel(logging.NOTSET)
            logging.error("Error")
            logging.warning("Warning")
            logging.info("Info")
            logging.debug("Debug")
        foo_function()
        print('-------------')
        with DisableLogger(logging.CRITICAL):
            foo_function()
        print('-------------')
        with DisableLogger(logging.WARNING):
            foo_function()
        print('-------------')
        with DisableLogger(logging.NOTSET):
            foo_function()
    """
    def __init__(self, level):
        self.level = level
    def __enter__(self):
       logging.disable(self.level)
    def __exit__(self, exit_type, exit_value, exit_traceback):
       logging.disable(logging.NOTSET)

class CustomLogger:
    # https://data-newbie.tistory.com/248   https://hwangheek.github.io/2019/python-logging/
    """
    적절한 logging 사용하는 방법
        - 일반적인 console 출력
            print()
        - 프로그램의 실행 중 발생하는 정상적인 이벤트 알림
            logging.info()
            logging.debug()      (진단 등을 위한) 자세한 수준의 로그인 경우
        - 런타임 중 발생한 이벤트와 관련하여 경고
            warnings.warn()      사용자가 프로그램을 수정해서 문제를 해결할 수 있는 경우 
            logging.warning()    사용자가 처리할 수 있는 문제가 아닌 경우 
        - 런타임 중 발생한 이벤트와 관련한 에러
            raise Exception      예외 처리
        - 발생한 예외를 suppress하고 raise 하지 않은 경우 (e.g. long-running 서버 프로세스에서 에러 발생 시)
            logging.error(), logging.exception(), logging.critical()

    Example:
        from time import sleep

        logger = CustomLogger('logger_practice')
        logger.set_default_formatter()
        logger.add_stream_handler(level='INFO')
        logger.add_file_handler(level='DEBUG')
        cnt = 0
        logger = logger.get_logger()
        while True:
            logger.debug(f'debug {cnt}')
            logger.info(f'info {cnt}')
            logger.warning(f'warning {cnt}')
            logger.error(f'error {cnt}')
            logger.critical(f'critical {cnt}')
            cnt += 1
            sleep(0.5)
            if cnt == 1000:
                break
    """

    def __init__(self, name:str=None, propagate:bool=False) -> None:
        """
        Args:
            name: for hierarchical logging
                for example,
                    logging.getLogger(None) -> root
                    logging.getLogger('A')
                    logging.getLogger('A.B')
                    logging.getLogger('A.B.C')
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel('DEBUG')
          # logger의 level이 높으면 handler의 level이 이보다 낮을 때 내용이 전달되지 않는다.
          # 예를 들어 logger의 level이 WARNING이고 handler의 level을 DEBUG로 설정했으면 handler에서 전달한 내용은 무시된다.
        self.logger.propagate = propagate
          # 하위 로거의 메시지를 상위 로거에도 남긴다.
          # 자식 로거에서 핸들러 설정을 해주고 싶으면 False로.
          # (True로 하면 로거가 부모, 자식 핸들러에서 중복으로 처리된다.)
        self.formatter = None
    
    def get_logger(self) -> logging.Logger:
        return self.logger

    def set_default_formatter(self, fmt="%(asctime)s;[%(levelname)s];%(message)s", datefmt="%Y-%m-%d %H:%M:%S") -> None:
        """
        기본 형식 설정하기.

        Args:
            참고 - https://docs.python.org/ko/3.7/library/logging.html#logging.Formatter

        Example:
            logger = CustomLogger('logger_practice')
            logger.set_default_formatter()
            logger.add_stream_handler(level='INFO') ...
        result example:
            2023-03-23 20:56:36;[INFO];info message
        """
        self.formatter = logging.Formatter(fmt=fmt, datefmt=datefmt) # format 형식을 알고 나서 수정하기

    def _warn_NOTSET(self, level:str, handler_name:str) -> None:
        """
        NOTSET을 입력하면 경고하기

        Args:
            level : self.levels의 keys
            handler_name : handler_dict의 keys
        """
        if level == 'NOTSET':
            self.logger.warning(f'"{handler_name}"의 "level"로 "NOTSET"이 입력되었습니다. 이 경우 원하지 않는대로 동작할 수도 있습니다. 공식 docs를 참고하여 사용하세요.')
    
    def _add_handler_helper(self, handler_name:str, level:str, fmt=None, datefmt=None, **handler_settings):
        """
        Args:
            handler_name : handler_dict의 keys
            level : self.levels의 keys
            handler_settings : 각 handler에 맞는 설정들

        Returns:
            logger with handler
        """
        handler_dict = {
            'StreamHandler' : logging.StreamHandler,
            'FileHandler' : logging.FileHandler,
            'RotatingFileHandler' : loghdlrs.RotatingFileHandler,
            'TimedRotatingFileHandler' : loghdlrs.TimedRotatingFileHandler,
        }
        levels = {
            'NOTSET' : logging.NOTSET,        # 0
            'DEBUG' : logging.DEBUG,          # 10
            'INFO' : logging.INFO,            # 20
            'WARNING' : logging.WARNING,      # 30
            'ERROR' : logging.ERROR,          # 40
            'CRITICAL' : logging.CRITICAL}    # 50
        self._warn_NOTSET(level=level, handler_name=handler_name)
        handler = handler_dict.get(handler_name)(**handler_settings)
        handler.setLevel(levels[level])
        if self.formatter:
            handler.setFormatter(self.formatter)
        if fmt or datefmt:
            self.formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)
            handler.setFormatter(self.formatter)
        self.logger.addHandler(handler)
        return self.logger
    
    def add_stream_handler(self, level:str='WARNING', fmt=None, datefmt=None) -> 'CustomLogger':
        """
        Console에 log 남기기

        Args:
            level : self.levels의 keys
            fmt, datefmt : set_default_formatter 참고

        Returns:
            logger with handler
        """
        self._add_handler_helper(handler_name='StreamHandler', level=level, fmt=fmt, datefmt=datefmt)
    
    def add_file_handler(self, level:str='DEBUG', filename:str=f'./log_{current_time}.txt', mode:str='w', fmt=None, datefmt=None) -> 'CustomLogger':
        """
        파일로 log 남기기

        Args:
            level : self.levels의 keys, 파일로 만들 거라 기본값을 DEBUG로 설정.        
            filename : 확장자는 txt 또는 log. 기본값은 log_년년월월일일_시시분분초초.txt
            mode : 'w', 'a'
            fmt, datefmt : set_default_formatter 참고

        Returns:
            logger with handler            
        """
        # FileHandler(filename=filename, mode=mode, encoding='utf-8')
        self._add_handler_helper(handler_name='FileHandler', level=level, fmt=fmt, datefmt=datefmt,
                                 filename=filename, mode=mode, encoding='utf-8')

    def add_rotating_file_handler(self, level:str='DEBUG', filename:str=f'./log_{current_time}.txt', mode:str='w', maxBytes:int=0, backupCount:int=0, fmt=None, datefmt=None) -> 'CustomLogger':
        """
        파일 용량을 정해서 log를 쌓고 제거할 때

        Args:
            level : self.levels의 keys, 파일로 만들 거라 기본값을 DEBUG로 설정.
            filename : 확장자는 txt 또는 log. 기본값은 log_년년월월일일_시시분분초초.txt
            mode : 'w', 'a'
            maxBytes : 한 파일당 용량 최대. 0일 때 롤오버(꽉 차면 새 파일을 만듦)하지 않는다.
            backupCount : backup할 파일 개수. 0일 때 롤오버하지 않는다.
            fmt, datefmt : set_default_formatter 참고

        Returns:
            logger with handler            
        """
        # RotatingFileHandler(filename=filename, mode=mode, maxBytes=maxBytes, backupCount=backupCount, encoding='utf-8')
        self._add_handler_helper(handler_name='RotatingFileHandler', level=level, fmt=fmt, datefmt=datefmt,
                                 filename=filename, mode=mode, maxBytes=maxBytes, backupCount=backupCount, encoding='utf-8')

    def add_timed_rotating_file_handler(self,
                                        level:str = 'DEBUG',                                        
                                        filename:str = f'./log_{current_time}.txt', 
                                        when:str = 'M',
                                        interval:int = 1,
                                        backupCount:int = 0, 
                                        atTime = dt.time(0, 0, 0),
                                        fmt=None, datefmt=None) -> 'CustomLogger':
        """
        시간을 정해서 log를 쌓고 제거할 때

        Args:
            level : self.levels의 keys, 파일로 만들 거라 기본값을 DEBUG로 설정.        
            filename : ~.txt, log
            when : 저장 주기
                'S'        | 초
                'M'        | 분
                'H'        | 시간
                'D'        | 일
                '\0'-'\6'  | 요일. 0이 월요일. atTime이 사용될 때 최초 롤오버 시간을 계산하는 데 사용된다.
                'midnight' | atTime을 지정하지 않으면 자정에, 그렇지 않으면 atTime에 롤오버한다.
            interval : 저장 주기의 간격
            backupCount : backup할 파일 개수
            atTime : datetime.time(0, 0, 0)
            fmt, datefmt : set_default_formatter 참고

        Returns:
            logger with handler
        """
        self._add_handler_helper(handler_name='TimedRotatingFileHandler', level=level, fmt=fmt, datefmt=datefmt,
                                 filename=filename, when=when, interval=interval, backupCount=backupCount, encoding='utf-8', atTime=atTime)
