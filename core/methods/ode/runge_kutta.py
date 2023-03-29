"""
TODO
1. 여러 개의 distance를 한 번에 계산
"""

from .base_method_ode import Base_Method_ODE
from ...builder import METHODS
import pandas as pd

@METHODS.store_module('Runge_Kutta')
class Runge_Kutta(Base_Method_ODE):
    """
    4th Runge-Kutta method.
    
    For this method, "iter_num" means n. "stop_diff" is not supported.
        For example, init_x = 0 and iter_num = 5 means x = [0, 0.2, 0.4, 0.6, 0.8, 1.0]

    example of config file;
    ================================================================================
        calculator = dict(
        fn = lambda x, y: x + y,
        input = dict(init_x = 0, init_y = 0, distance=0.2),
        type = 'Runge-Kutta',
        iter_num = 5,
        print_interim = True,
                )
    ================================================================================
                    
    """
    def _sanity_check(self, inputs) -> None:
        is_stop_diff = inputs.get('stop_diff') or inputs.get('stop_diff')==0
        assert not is_stop_diff, '"stop_diff" is not supported for Runge-Kutta'

    def _change_format(self, val) -> list[float]:
        """
        distance는 상수니까 속성으로 남긴다. 출력해야 하는 x, y값만 내보내기
        """
        self.distance = val.distance
        xy_pair = [val.init_x, val.init_y]
        return xy_pair
    
    def save_init_val_for_csv(self, val: list[float]) -> None:
        x = {
            0: val[0]
        }
        y = {
            0: val[1]
        }
        x = pd.Series(x)
        y = pd.Series(y)
        self.df = pd.DataFrame({
            'x' : x,
            'y' : y,
        })
    
    def save_val_for_csv(self, idx:int, val:list[float]):
        self.df.loc[idx] = val

    def _calculate_helper(self, fn, xy_pair: list[float]) -> list[float]:
        h = self.distance
        x, y = xy_pair[0], xy_pair[1]

        k1 = h * fn(x, y)
        k2 = h * fn(x + 0.5*h, y + 0.5*k1)
        k3 = h * fn(x + 0.5*h, y + 0.5*k2)
        k4 = h * fn(x + h, y + k3)

        x = x + h
        y = y + (k1 + 2*k2 + 2*k3 + k4)/6

        xy_pair = [x, y]
        return xy_pair

    def log_result(self, val: list[float]) -> None:
        self.logger_result.info(f"Result : y = {val[1]:6.6f} when x = {val[0]:6.3f}")

    def log_interim(self, val_interim: list[float], cnt: int, print_interim: bool) -> None:
        if print_interim:        
            self.logger_interim.info(f"The value of {cnt:>3}th iteration : y = {val_interim[1]:6.6f} when x = {val_interim[0]:6.3f}")

