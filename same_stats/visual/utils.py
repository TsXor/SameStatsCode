from typing import Callable

import matplotlib.pyplot as plt
import pytweening

RampMode = tuple[bool, bool]
Tweener = Callable[[int | float], int | float]


def tweener_of_mode(ramp_mode: RampMode) -> Tweener:
    ramp_in, ramp_out = ramp_mode
    if ramp_in and not ramp_out:
        return pytweening.easeInSine
    elif ramp_out and not ramp_in:
        return pytweening.easeOutSine
    elif ramp_out and ramp_in:
        return pytweening.easeInOutSine
    else:
        return pytweening.linear
    
def plt_add_data(
    x: float, y: float,
    line_height: float, font_size: float,
    total_precision: int, shadow_precision: int,
    data: list[tuple[str, float]],
):
    '''
    total_precision: 总共保留的小数位
    shadow_precision: 显示为半透明的小数位数
    '''
    if shadow_precision >= total_precision: raise ValueError
    
    max_label_length = max(len(label) for label, val in data)
    y_pos = y
    for label, val in data:
        val_repr = format(val, f'0.{total_precision}f')
        val_repr_noshadow = val_repr[:-shadow_precision]
        val_repr_shadow = val_repr[-shadow_precision:]
        plt_str = f'{label.ljust(max_label_length)}: {val_repr_noshadow}'
        shadow_str = ' ' * len(plt_str) + val_repr_shadow
        plt.text(x, y_pos, plt_str, fontsize=font_size, alpha=1)
        plt.text(x, y_pos, shadow_str, fontsize=font_size, alpha=0.3)
        y_pos -= line_height
