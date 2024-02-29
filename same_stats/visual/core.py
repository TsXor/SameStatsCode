from functools import cached_property
from io import BytesIO
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

if TYPE_CHECKING:
    from ..algo import SameStatsTransformation

from .utils import *

BOUND_PAD: float = 5

MPL_RC_PARAMS = {
    'font.size': 12.0,
    'font.family': 'monospace',
    'font.weight': 'normal',
    'font.sans-serif': (
        'Helveitca',
        'Bitstream Vera Sans',
        'Lucida Grande',
        'Verdana',
        'Geneva',
        'Lucid',
        'Arial',
        'Avant Garde',
        'sans-serif',
    ),
    'font.monospace': (
        'Decima Mono',
        'Bitstream Vera Sans Mono',
        'Andale Mono',
        'Nimbus Mono L',
        'Courier New',
        'Courier',
        'Fixed',
        'Terminal',
        'monospace',
    ),
    'text.color': '#222222',
    'pdf.fonttype': 42,
}


class ImageGenerator:
    '''用于可视化图片生成。'''

    transformer: 'SameStatsTransformation'
    n_frames: int
    ramp_mode: RampMode

    def __init__(self,
        transformer: 'SameStatsTransformation',
        n_frames: int,
        ramp_mode: RampMode = (False, False),
    ) -> None:
        self.transformer = transformer
        self.n_frames = n_frames
        self.ramp_mode = ramp_mode

    @cached_property
    def target_iters(self) -> dict[int, int]:
        '''字典键为应被采样的迭代数，值为对应的帧编号'''
        tweener = tweener_of_mode(self.ramp_mode)
        frame_list = (round(tweener(x) * self.transformer.total_iters)
                      for x in np.arange(0, 1, 1 / self.n_frames))
        return {i_iter: i_frame for i_frame, i_iter in enumerate(frame_list)}
    
    @cached_property
    def _plot_xylim(self):
        '''可视化图的xy轴区域，取决于算法参数'''
        xmin, xmax = self.transformer.x_bounds
        ymin, ymax = self.transformer.y_bounds
        xlim = (xmin - BOUND_PAD, xmax + BOUND_PAD)
        ylim = (ymin - BOUND_PAD, ymax + BOUND_PAD)
        return xlim, ylim
    
    def make_scatter(self) -> BytesIO:
        '''
        create a plot which shows both the plot, and the text of the summary statistics
        calling this method will not modify algorithm state
        
        创建一个显示汇总统计数据的图和文本的图
        调用这个方法不会改变算法的状态
        '''
        with plt.rc_context(MPL_RC_PARAMS):
            # 下面的这些硬编码图片参数谁爱改谁改罢，，，
            plt.figure(figsize=(20, 5))
            sns.regplot(x="x", y="y", data=self.transformer.cur_state,
                        ci=None, fit_reg=False,
                        scatter_kws={"s": 50, "alpha": 0.7, "color":"black"})
            xlim, ylim = self._plot_xylim
            plt.xlim(xlim); plt.ylim(ylim)
            plt.tight_layout()

            labels = ("X Mean", "Y Mean", "X SD", "Y SD", "Corr.")
            plt_add_data(110, 75, 15, 30, 7, 5, list(zip(labels, self.transformer.cur_stats)))
            plt.tight_layout(rect=(0, 0, 0.57, 1))
            
            # 将图片暂存到BytesIO，给自己一些操作的自由
            out = BytesIO()
            plt.savefig(out, dpi=72, format="png")
            plt.clf(); plt.cla(); plt.close()
        return out
    