from .builder import METHODS, build_operator

def operate(cfg):
    """
    수치해석을 계산하는 메서드.
    config를 받아서
        1. 유효성 검사를 하고
        2. 지정된 method에 따라 계산 수행
    """
    cal = cfg.calculator
    is_iter = cal.get('iter_num') or cal.get('iter_num')==0
    is_stop_diff = cal.get('stop_diff') or cal.get('stop_diff')==0
    # sanity check
    assert not (is_iter and is_stop_diff), 'Only use either "iter_num" or "stop_diff".'
    if is_iter:
        assert cal.iter_num > 0, '"iter_num" should be a positive integer.'
    if is_stop_diff:
        if cal.stop_diff < 0:
            print('"stop_diff" is set to positive. (calculate with absolute value)')
            cal.stop_diff = -cal.stop_diff
    build_operator(cal)