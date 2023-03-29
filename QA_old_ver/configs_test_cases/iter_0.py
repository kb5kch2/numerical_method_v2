import math
A = math.pi*(11**2)**4

calculator = dict(
    fn = lambda x: 6411.2*math.pow(x/(60*A),1.2727)*(0.5+0.1) - 1531.9 - 5.927*x + 0.0165 * x * x,
    init_val=1000,
    type = 'newton_raphson',
    iter_num = 0,
    # stop_diff = 0.001,
    print_interim = True,
              )