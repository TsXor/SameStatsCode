import abc
from io import BytesIO
from pathlib import Path
from typing import Any

import av
import numpy as np
import pandas as pd
from PIL import Image

from . import algo, visual


def is_number(x: Any):
    return isinstance(x, int) or isinstance(x, float)

def read_point_csv(pth: str | Path):
    '''
    读入csv点集数据
    兼容有表头和无表头的数据
    '''
    df = pd.read_csv(pth, header=None)
    
    nrows, ncols = df.shape
    if ncols == 2: pass
    elif ncols == 3:
        # 第一列是序号，切掉
        df = df.iloc[:, 1:]
    else:
        raise ValueError('数据列数不正确')
    
    first_row = df.iloc[0, :]
    if all(is_number(x) for x in first_row):
        df.columns = ['x', 'y']
    elif set(first_row) == {'x', 'y'}:
        # 第一行是表头，切掉
        df = df.iloc[1:, :]
        # 尊重原表头
        df.columns = first_row
    else:
        raise ValueError('数据首行不正确')
    
    return df.astype(float)

def create_video(files: list[Path], fps: int, output: Path):
    vid = av.open(str(output), "w")
    vs = vid.add_stream("h264", fps)
    for i, file_path in enumerate(files):
        im = Image.open(file_path).convert('RGB')
        arr = np.asarray(im)
        if i == 0:
            height, width, _ = arr.shape
            vs.width = width
            vs.height = height
        new_frame = av.VideoFrame.from_ndarray(arr, format="rgb24")
        new_frame.pts = None
        vid.mux(vs.encode(new_frame))
    vid.close()

class IFileSaver(abc.ABC):
    '''输出文件保存接口。鉴定为：写Java写的。'''
    @staticmethod
    def write_bio_to(bio: BytesIO, pth: str | Path):
        Path(pth).write_bytes(bio.getbuffer())

    @abc.abstractmethod
    def save_visual_frame(self, img: BytesIO, i_frame: int) -> None:
        raise NotImplementedError
    
    @abc.abstractmethod
    def save_data_snapshot(self, data: pd.DataFrame, i_frame: int, i_iter: int) -> None:
        raise NotImplementedError
    
    @abc.abstractmethod
    def save_video(self) -> None:
        raise NotImplementedError

class ILoopIndicator(abc.ABC):
    '''循环进度显示接口。鉴定为：写Java写的。'''
    @abc.abstractmethod
    def init(self, n_total: int) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def increment(self) -> None:
        raise NotImplementedError


def run_pattern(
    source: pd.DataFrame, target: algo.dest_types.IDestination,
    n_iter: int, n_frames: int, error_precision: int,
    file_saver: IFileSaver, loop_indicator: ILoopIndicator,
):
    '''运行一次SameState转换'''
    algo_state = algo.SameStatsTransformation(source, target, n_iter,
                                              n_error_trunc=error_precision)
    image_gen = visual.ImageGenerator(algo_state, n_frames)

    img_initial = image_gen.make_scatter()
    file_saver.save_visual_frame(img_initial, 0)
    loop_indicator.init(n_iter)

    while True:
        completed = algo_state.iterate()
        if algo_state.cur_iter in image_gen.target_iters:
            img = image_gen.make_scatter()
            i_iter = algo_state.cur_iter
            i_frame = image_gen.target_iters[i_iter]
            file_saver.save_data_snapshot(algo_state.cur_state, i_frame, i_iter)
            file_saver.save_visual_frame(img, i_frame)
        loop_indicator.increment()
        if completed: break
    
    file_saver.save_video()

