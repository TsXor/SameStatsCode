from typing import Any, Optional

from .dest_types import IDestination
from .utils import *


def perturb(
    df: pd.DataFrame,
    dest: IDestination,
    x_bounds: Bound,
    y_bounds: Bound,
    temperature: float,
    shake: float = 0.1,
    allowed_dist: float = 2,
):
    '''
    This is the function which does one round of perturbation
    df: is the current dataset
    dest: the destination shape, whatever implementing IDestination
    shake: the maximum amount of movement in each iteration
    
    此函数进行一轮扰动。
    df: 当前数据集
    dest: 目标形状，随便是什么，只要实现IDestination即可
    shake: 每次迭代的最大移动量

    注：事实上取随机扰动的时候使用的函数是np.random.randn，而这个函数
    生成的是服从标准正态分布的随机数，并没有上下限，也就是说shake只是
    一个控制常数，并不真的代表“每次迭代的最大移动量”
    本改编者曾试过将扰动使用的随机函数改为np.random.rand，这个函数生成
    均匀分布于[0,1)的随机数，这样就符合原作者“shake为最大移动量”的观点，
    但是这样会导致选中的点很容易“卡住”。对此我的评价是：原作者你就是个
    大聪明。
    '''

    # take one row at random
    # 随机取一行
    row = np.random.randint(0, len(df))
    point = df_get_ith_point(df, row)

    # this is the simulated annealing step, if "do_bad", then we are willing to 
    # accept a new state which is worse than the current one
    # 这是模拟退火步骤，如果“do_bad”为真，那么我们愿意
    # 接受比当前状态更糟糕的新状态
    do_bad = np.random.random_sample() < temperature

    op_success = False
    while not op_success:
        new_point = shake_point(point, shake)

        # 此处距离的计算委托给具体的实现
        # 学点程序设计吧哥们，这对你有好处
        old_dist = dest.distance(point)
        new_dist = dest.distance(new_point)

        # check if the new distance is closer than the old distance
        # or, if it is less than our allowed distance
        # or, if we are do_bad, that means we are accpeting it no matter what
        # if one of these conditions are met, jump out of the loop
        # 检查新距离是否比旧距离更近
        # 或者，它是否小于我们允许的距离
        # 或者，是否处于do_bad状态，那意味着我们无论如何都要接受
        # 如果满足上述条件之一，就跳出循环
        dist_acceptable = new_dist < old_dist or new_dist < allowed_dist or do_bad
        pos_acceptable = point_in_bound(new_point, x_bounds, y_bounds)
        op_success = dist_acceptable and pos_acceptable

    return row, new_point


def is_error_still_ok(stats1: DFStats, stats2: DFStats, n_decimal_trunc: int):
    '''
    checks to see if the statistics are still within the acceptable bounds
    with df1 as the original dataset, and df2 as the one we are testing

    检查统计数字是否仍在可接受的范围内
    df1作为原始数据集，df2作为我们正在测试的数据集
    '''

    error = tuple(abs(decimal_trunc_sub(n1, n2, n_decimal_trunc))
                  for n1, n2 in zip(stats1, stats2))
    return max(error) == 0


class SameStatsTransformation:
    '''算法主类。'''

    source: pd.DataFrame
    cur_state: pd.DataFrame
    cur_stats: DFStats
    target: IDestination
    total_iters: int
    cur_iter: int
    x_bounds: Bound
    y_bounds: Bound
    temperature_range: tuple[float, float]
    n_error_trunc: int
    perturb_params: dict[str, Any]

    def __init__(self,
        source: pd.DataFrame,
        target: IDestination,
        total_iters: int = 100000,
        x_bounds: Bound = (0, 100),
        y_bounds: Bound = (0, 100),
        temperature_range: tuple[float, float] = (0.0, 0.4),
        n_error_trunc: int = 2,
        perturb_params: Optional[dict[str, Any]] = None,
    ) -> None:
        xmin, xmax = x_bounds
        ymin, ymax = y_bounds
        source = source.clip([xmin, ymin], [xmax, ymax]) # type: ignore

        self.source = source
        self.target = target
        self.total_iters = total_iters
        self.x_bounds = x_bounds
        self.y_bounds = y_bounds
        self.temperature_range = temperature_range
        self.n_error_trunc = n_error_trunc
        self.perturb_params = {} if perturb_params is None else perturb_params

        self.cur_iter = 0
        # 备份源状态，虽然我也不知道有什么用
        self.cur_state = source.copy()
        self.cur_stats = df_stats(source)

    @property
    def temperature(self) -> float:
        iter_ratio_left = (self.total_iters - self.cur_iter) / self.total_iters
        min_temp, max_temp = self.temperature_range
        return interpolate(min_temp, max_temp, s_curve(iter_ratio_left))
    
    def iterate(self) -> bool:
        '''做一轮迭代，如果已完成全部迭代，返回真。'''
        target_row, new_point = perturb(self.cur_state, self.target,
                                        self.x_bounds, self.y_bounds,
                                        self.temperature,
                                        **self.perturb_params)
        orig_point = df_get_ith_point(self.cur_state, target_row)

        # 这样就不用每次都复制整个源数据集，或许能提高效率
        df_set_ith_point(self.cur_state, target_row, new_point)
        new_stats = df_stats(self.cur_state)

        if is_error_still_ok(self.cur_stats, new_stats, self.n_error_trunc):
            self.cur_stats = new_stats
        else:
            # 撤销本次扰动
            df_set_ith_point(self.cur_state, target_row, orig_point)
        
        self.cur_iter += 1
        return self.cur_iter >= self.total_iters

