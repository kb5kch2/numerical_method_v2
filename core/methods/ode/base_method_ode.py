from ..base_method import Base_Method
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))
from utils.config import ConfigDict

class Base_Method_ODE(Base_Method) :

    def cal_centered_divided_difference(self, fn, x:float, dx:float = 1e-5) -> float:
        """
        미분을 대신할 중앙차분법.
        (f(x+dx)-f(x-dx))/2dx에서 dx를 설정하기
        """
      # sanity check
        assert dx != 0, '"dx" must not be zero.'
        dfn = (fn(x+dx)-fn(x-dx)) / (2*dx)
        return dfn

    def calculate(self, inputs: ConfigDict) -> None:

        fn = inputs.fn
        init_val = self._change_format(inputs.input)
            # input = {init_x : 10, init_y : 10, ...}
        self.save_init_val_for_csv(init_val)
        iter_num = inputs.get('iter_num', -1)
        stop_diff = inputs.get('stop_diff')
        print_interim = inputs.print_interim

        # calculate by iteration 
        if iter_num != -1:
            cnt = 0
            val = init_val
            self.log_interim(val, cnt, print_interim)
            for _ in range(iter_num):
                val = self._calculate_helper(fn, val)
                cnt += 1
                self.log_interim(val, cnt, print_interim)
                self.save_val_for_csv(cnt, val)
        
        # calculate by difference of last two values
        else:
            cnt = 0
            pre_val = init_val
            self.log_interim(pre_val, cnt, print_interim)
            val = self._calculate_helper(fn, pre_val)
            cnt += 1
            self.log_interim(val, cnt, print_interim)
            self.save_val_for_csv(cnt, val)
            while abs(val - pre_val) > stop_diff:
                pre_val = val
                val = self._calculate_helper(fn, pre_val)
                cnt += 1
                self.log_interim(val, cnt, print_interim)
                self.save_val_for_csv(cnt, val)
                if cnt == 10000:
                    self.logger_interim.warning('For "stop_diff", calculate up to 10,000 times.')
                    break
                
        self.log_result(val)

        self.df.to_csv(inputs._dir + 'result.csv', encoding='utf-8')