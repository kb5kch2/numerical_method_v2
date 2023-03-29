from .base_method_ode import Base_Method_ODE
from ...builder import METHODS
import pandas as pd

@METHODS.store_module('Newton_Raphson')
class Newton_Raphson(Base_Method_ODE):
    """
    Newton-Raphson method.
    example of config file;
    ================================================================================
        import math
        A = math.pi*(11**2)**4

        calculator = dict(
            fn = lambda x: 6411.2*math.pow(x/(60*A),1.2727)*(0.5+0.1) - 1531.9 - 5.927*x + 0.0165 * x * x,
            input = 1000,
            type = 'Newton-Raphson',
            iter_num = 10,
            # stop_diff = 0.001,
            print_interim = True,
                    )
    ================================================================================

    """

    def _change_format(self, val: float) -> float:
        return val

    def save_init_val_for_csv(self, val: float) -> None:
        x = {
            0: val
        }
        x = pd.Series(x)
        self.df = pd.DataFrame({
            'x' : x,
        })
    
    def save_val_for_csv(self, idx:int, val:float):
        self.df.loc[idx] = val

    def _calculate_helper(self, fn, x: float) -> float:
        x = x - fn(x)/self.cal_centered_divided_difference(fn, x)
        return x

    def log_result(self, val: float) -> None:
        self.logger_result.info(f"Result : {val:6.6f}")

    def log_interim(self, val_interim: float, cnt: int, print_interim: bool) -> None:
        if print_interim:
            self.logger_interim.info(f"The value of {cnt:>5}th iteration : {val_interim:6.6f}")