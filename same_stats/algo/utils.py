import math
from typing import cast

import numpy as np
import pandas as pd
import pytweening

Point = tuple[float, float]
Bound = tuple[float, float]
Vector = tuple[float, float]
Line = tuple[Point, Point]

DFStats = tuple[float, float, float, float, float]


s_curve = pytweening.easeInOutQuad

def df_get_ith_point(df: pd.DataFrame, i: int) -> Point:
    return df['x'][i + 1], df['y'][i + 1]

def df_set_ith_point(df: pd.DataFrame, i: int, p: Point) -> None:
    x, y = p; df['x'][i + 1] = x; df['y'][i + 1] = y

def df_stats(df: pd.DataFrame) -> DFStats:
    xm = df.x.mean()
    ym = df.y.mean()
    xsd = df.x.std()
    ysd = df.y.std()
    pc = cast(float, df.corr().x.y)
    return (xm, ym, xsd, ysd, pc)

def interpolate(n1: float, n2: float, ratio: float):
    return (n2 - n1) * ratio + n1

def square(x: float): return x * x

def clamp(x: float, nmin: float, nmax: float):
    if (x < nmin): return nmin
    if (x > nmax): return nmax
    return x

def decimal_trunc_sub(n1: float, n2: float, n_trunc: int) -> int:
    m: int = 10 ** n_trunc
    return round(n1 * m) - round(n2 * m)

def shake_point(p: Point, max_shake: float):
    x, y = p
    dx = np.random.randn() * max_shake
    dy = np.random.randn() * max_shake
    return (x + dx, y + dy)

def interpolate_point(p1: Point, p2: Point, ratio: float):
    x1, y1 = p1; x2, y2 = p2
    x = interpolate(x1, x2, ratio)
    y = interpolate(y1, y2, ratio)
    return (x, y)

def point_in_bound(p: Point, x_bounds: Bound, y_bounds: Bound):
    x, y = p; xmin, xmax = x_bounds; ymin, ymax = y_bounds
    return x > xmin and x < xmax and y > ymin and y < ymax

def point_distance(p1: Point, p2: Point):
    '''求两点距离'''
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def line_midpoint(line: Line):
    '''求线段中点'''
    (x1, y1), (x2, y2) = line
    return (x1 + x2) / 2, (y1 + y2) / 2

def vec_dot(v1: Vector, v2: Vector):
    '''向量点积'''
    x1, y1 = v1; x2, y2 = v2
    return x1 * x2 + y1 * y2


def point_line_distance(p: Point, l: Line):
    p1, p2 = l; x1, y1 = p1; x2, y2 = p2; px, py = p
    line_mag_square = square(x1 - x2) + square(y1 - y2)
    line_mag = math.sqrt(line_mag_square)

    if line_mag < 0.00000001:
        # 下面这行被注释掉的是原作者的神奇实现。
        # 我必须指出：这是极为离谱的。虽然线段过短确实会使得下面的公式
        # 精度溢出，但是解决方法并不是拿一个很大的数糊弄。线段很短时，
        # 我们可以直接取点到线段中点的距离。
        #return 9999
        return point_distance(p, line_midpoint(l))
    
    lambda_ = - ((x2 - x1) * (px - x2) + (y2 - y1) * (py - y2)) / line_mag_square
    lambda_ = clamp(lambda_, 0, 1)
    min_point = interpolate_point(p2, p1, lambda_)

    return point_distance(p, min_point)

