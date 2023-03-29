from abc import ABCMeta, abstractmethod
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))))
from utils.config import ConfigDict
from utils.logging_custom import *
import pandas as pd

class Base_Method(metaclass = ABCMeta) :

    def __init__(self, inputs: ConfigDict) -> None:
        """
        Args:
            inputs : ConfigDict. There are fn, iter_num, stop_diff, print_interim, init_val, ...
                fn : lambda expression.
                iter_num : positive integer. Use either iter_num or stop_diff.
                stop_diff : zero or positive float. Use either iter_num or stop_diff.
                print_interim : boolean
                init_val : differ according to each method.
        """
        self._sanity_check(inputs)
        self._set_logger(inputs)
        self.calculate(inputs)

    def _sanity_check(self, inputs: ConfigDict) -> None:
        """Check sanity if needed."""
        pass

    def _set_logger(self, inputs: ConfigDict) -> None:
        """
        Set logger.

        Args:
            inputs: refer __init__
        """
        _dir = inputs._dir

        logger_interim = CustomLogger('logger_interim')
        logger_interim.add_stream_handler(level='INFO')
        logger_interim.add_file_handler(level='INFO', filename=_dir+'log_interim.txt')

        logger_result = CustomLogger('logger_result')
        logger_result.add_stream_handler(level='INFO')
        logger_result.add_file_handler(level='INFO', filename=_dir+'log_result.txt')

        self.logger_interim = logger_interim.get_logger()
        self.logger_result = logger_result.get_logger()     

    @abstractmethod
    def calculate(self, inputs: ConfigDict) -> None:
        """
        Define calculation process backbone.

        Args:
            inputs : same as __init__
        
        Return:
            There's no any return.
            
        """
        pass

    @abstractmethod
    def _change_format(self, val: ConfigDict):
        """
        Change to a specific format for each method.
        
        Args:
            val : ConfigDict
        
        Returns:
            float, tensor[float], ...
        
        """
        pass

    @abstractmethod
    def save_init_val_for_csv(self, val) -> None:
        """
        Save the initial value to create csv result file.
        use pandas with self.df

        Args:
            val : return type of _change_format for each method
        
        Returns:
            There's no any return.
        
        Example:
        ==========================================================
            # make dict for series of each variables
            var0 = {
                0: val[0]
            }
            var1 = {
                0: val[1]
            }
            ...

            # make Series
            var0 = pd.Series(var0)
            var1 = pd.Series(var1)
            ...

            # make DataFrame
            self.df = pd.DataFrame({
                'var0' : var0,
                'var1' : var1,
                ...
            })
        ==========================================================
        """
        pass

    def save_val_for_csv(self, idx:int, val:list) -> None:
        """
        If "val" is not list, this method must be modified by overriding.

        Save values to create csv result file.
        use pandas with self.result

        Args:
            idx : index for Data Frame
            val : return type of _change_format for each method
        
        Returns:
            There's no any return.
        """
        # add next index series to self.df
        self.df.loc[idx] = val

    @abstractmethod
    def _calculate_helper(self, fn, val):
        """
        Calculate according to each method.
        
        Args:
            fn : explicit lambda form
            val : return type of _change_format for each method

        Returns:
            same as val

        """
        pass

    @abstractmethod
    def log_result(self, val) -> None:
        """
        Should include "self.logger_result".
        Log the result with the format for each method.

        Args:
            val : value of result. The type is from "_change_format" method for each method

        Returns:
            There's no any return.
        """
        # self.logger_result.info(f"Result : {val:6.6f}")
        pass

    @abstractmethod
    def log_interim(self, val_interim, cnt: int, print_interim: bool) -> None:
        """
        Should include "self.logger_interim".
        Log the interim values with the format for each method.

        Args:
            val_interim : interim value. The type is from "_change_format" method for each method
            cnt : express the number of iteration
            print_interim : boolean from inputs of __init__.
        
        Returns:
            There's no any return.
        """
        # if print_interim:
        #     self.logger_interim.info()
        pass
        

    # @abstractmethod
    # def _plot_helper():
    #     pass