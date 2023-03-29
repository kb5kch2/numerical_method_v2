# from mmcv (mmcv\utils\registry.py)

"""
HOW TO USE

1. builder를 만들어 Storage 객체를 생성
    예시)
        [.../builder.py]에서
        @ numerical_method_v2/core/builder.py
        >>> from utils.storage import Storage
        >>> from utils.config import ConfigDict
        >>> METHODS = Storage('methods')
        >>> def build_operator(cfg: ConfigDict):
        >>>     return METHODS.build(cfg)

2. __init__.py의 __all__ 안에 Storage 객체를 명시하고 4번 순서의 파일에서 import
    예시)
        [위 예시와 같은 폴더에서 __init__.py]를 생성
        @ numerical_method_v2/core/__init__.py
        >>> from .methods import *
        >>> from .builder import METHODS, build_operator
        >>> __all__ = ['METHODS', 'build_operator']
        [원하는기능을 수행할 파일]에서
        @ numerical_method_v2/core/operate.py
        >>> from .builder import METHODS, build_operator
                
3. Storage에 저장할 class에 Storage 객체의 데코레이터 삽입
    예시)
        [class를 적어놓은 .py 파일]에서
        @ numerical_method_v2/core/methods/newton_raphson.py
        >>> from ..builder import METHODS
        >>> @METHODS.store_module('newton_raphson')
        >>> class Newton_Raphson(Base_Method_Iteration):
        >>>     pass
                
4. builder에 ConfigDict를 넣어 실행
    예시)
        [원하는기능을 수행할 파일]에서
        @ numerical_method_v2/core/operate.py
        >>> build_operator(cfg)
"""

from .config import ConfigDict
import inspect

def ground_make_from_cfg(cfg: ConfigDict, storage: 'Storage'):
    """
    cfg를 지정한 "type" class에 넣어 그 class의 인스턴스 만들기
    """
    if not isinstance(cfg, dict):
        raise TypeError(f'Your cfg must be a dict, but got {type(cfg)}')
    if 'type' not in cfg:
        raise KeyError('Your cfg must contain the key "type"')
    if not isinstance(storage, Storage):
        raise TypeError(f'"storage" must be an Storage object, but got {type(storage)}')

    _cfg = cfg.copy()
    obj_type = _cfg.pop('type')
    if isinstance(obj_type, str):
        obj_cls = storage.get(obj_type)
        if obj_cls is None:
            raise KeyError(
                f'{obj_type} is not in the {storage.name} Storage')
    elif inspect.isclass(obj_type) or inspect.isfunction(obj_type):
        obj_cls = obj_type
    else:
        raise TypeError(f'"type" must be a str or valid type, but got {type(obj_type)}')

    try:
        return obj_cls(_cfg) # "type"으로 명시된 class의 인스턴스 생성, _cfg는 ConfigDict
    except Exception as e:
        # Normal TypeError does not print class name.
        raise type(e)(f'{obj_cls.__name__}: {e}')

class Storage:

    @staticmethod
    def infer_category():
        """
        저장되는 대상의 가장 상위 카테고리를 반환.

        Example:
            >>> # in mmdet/models/backbone/resnet.py
            >>> MODELS = Storage('models')
            >>> @MODELS.store_module()
            >>> class ResNet:
            >>>     pass
            The category of ``ResNet`` will be ``mmdet``.
        """
        frame = inspect.currentframe()
        # get the frame where `infer_category()` is called
        infer_category_caller = frame.f_back.f_back
        filename = inspect.getmodule(infer_category_caller).__name__
        split_filename = filename.split('.')
        return split_filename[0]

    @property
    def name(self):
        return self._name
    @property
    def category(self):
        return self._category
    @property
    def children(self):
        return self._children
    def _add_children(self, storage):
        """
        부모 storage에 자식 storage를 저장한다.

        Example:
            >>> models = Storage('models')
            >>> mmdet_models = Storage('models', parent=models)
            >>> @mmdet_models.storage_module()
            >>> class ResNet:
            >>>     pass
            >>> resnet = models.build(dict(type='mmdet.ResNet'))
        """

        assert isinstance(storage, Storage)
        assert storage.category is not None
        assert storage.category not in self.children, f'category {storage.category} exists in {self.name} storage'
        self.children[storage.category] = storage

    def __init__(self, name, ground_making=None, parent=None, category=None):
        self._name = name
        self._module_dict = dict()
        self._children = dict()
        self._category = self.infer_category() if category is None else category
        if parent is not None:
            assert isinstance(parent, Storage)
            parent._add_children(self)
            self.parent = parent
        else:
            self.parent = None
        # self.ground_making will be set with the following priority:
        # 1. ground_making
        # 2. parent.ground_making
        # 3. ground_make_from_cfg
        if ground_making is not None:
            self.ground_making = ground_making
        else:
            if parent is not None:
                self.ground_making = parent.ground_making
            else:
                self.ground_making = ground_make_from_cfg

    @staticmethod
    def split_category_key(key: str):
        """
        category와 key를 분리한다.

        Examples:
            >>> Storage.split_category_key('mmdet.ResNet')
            'mmdet', 'ResNet'
            >>> Storage.split_category_key('ResNet')
            None, 'ResNet'

        Return:
            tuple[str | None, str]: The former element is the first category of
            the key, which can be ``None``. The latter is the remaining key.
        """
        split_index = key.find('.')
        if split_index != -1:
            return key[:split_index], key[split_index + 1:]
        else:
            return None, key

    def get(self, key: str):
        """
        key에 대응하는 class를 저장소에서 가져온다.
        """
        category, real_key = self.split_category_key(key)
        if category is None or category == self._category:
            # get from self
            if real_key in self._module_dict:
                return self._module_dict[real_key]
        else:
            # get from self._children
            if category in self._children:
                return self._children[category].get(real_key)
            else:
                # go to root
                parent = self.parent
                while parent.parent is not None:
                    parent = parent.parent
                return parent.get(key)
    
    def build(self, *args: ConfigDict, **kwargs):
        """
        args를 지정한 "type" class에 넣어 그 class의 인스턴스 만들기
        """
        return self.ground_making(*args, **kwargs, storage=self)

    def _storage_module(self, module, module_name=None):
        
        if not inspect.isclass(module) and not inspect.isfunction(module):
            raise TypeError(f'module must be a class or a function, but got {type(module)}')

        if module_name is None:
            module_name = module.__name__
        if isinstance(module_name, str):
            module_name = [module_name]
        for name in module_name:
            if name in self._module_dict:
                raise KeyError(f'{name} is already stored in {self.name}')
            self._module_dict[name] = module

    def store_module(self, name=None, module=None):
        """
        모듈을 self._module_dict에 저장하기. key는 class 이름, value는 그 class.
        데코레이터나 함수로 사용한다.

        Example:
            >>> backbones = Storage('backbone')
            >>> @backbones.store_module()
            >>> class ResNet:
            >>>     pass

            >>> backbones = Storage('backbone')
            >>> @backbones.store_module(name='mnet')
            >>> class MobileNet:
            >>>     pass

            >>> backbones = Storage('backbone')
            >>> class ResNet:
            >>>     pass
            >>> backbones.store_module(ResNet)

        Args:
            name (str | None): The module name to be stored. If not specified, the class name will be used.
            module (type): Module class or function to be stored.
        """

        # use it as a normal method: x.storage_module(module=SomeClass)
        if module is not None:
            self._storage_module(module=module, module_name=name)
            return module

        # use it as a decorator: @x.storage_module()
        def _storage(module):
            self._storage_module(module=module, module_name=name)
            return module

        return _storage
