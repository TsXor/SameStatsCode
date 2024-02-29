'''
命令行接口。
我可能会写个GUI或者TUI之类的帮你调用它。
'''

from io import BytesIO
from pathlib import Path
from typing import Any, Iterator

import click
import pandas as pd
import tqdm

import same_stats.algo as algo
from same_stats.utils import (IFileSaver, ILoopIndicator, read_point_csv,
                              run_pattern, create_video)

LAUNCHER_GLOBAL_NAME = '__launcher_config__'

def get_launcher_config() -> dict[str, Any]:
    return globals().get(LAUNCHER_GLOBAL_NAME, {})


class DefaultFileSaver(IFileSaver):
    source_name: str
    target_name: str
    output_home_path: Path
    images: list[Path]

    def __init__(self,
        source_name: str,
        target_name: str,
        output_home_path: Path,
    ) -> None:
        self.source_name = source_name
        self.target_name = target_name
        self.output_home_path = output_home_path
        (output_home_path / 'images').mkdir(exist_ok=True)
        (output_home_path / 'video').mkdir(exist_ok=True)
        (output_home_path / 'data').mkdir(exist_ok=True)
        self.images = []
    
    @property
    def transform_name(self) -> str:
        return f'{self.source_name}-{self.target_name}'

    def save_visual_frame(self, img: BytesIO, i_frame: int) -> None:
        fname = f"{self.transform_name}-image-{format(i_frame, '05')}.png"
        img_path = self.output_home_path / 'images' / fname
        self.images.append(img_path)
        return self.write_bio_to(img, img_path)
    
    def save_data_snapshot(self, data: pd.DataFrame, i_frame: int, i_iter: int) -> None:
        fname = f"{self.transform_name}-data-{format(i_frame, '05')}-iter-{format(i_iter, '08')}.csv"
        return data.to_csv(self.output_home_path / 'data' / fname)
    
    def save_video(self) -> None:
        fname = f"{self.transform_name}-video.mp4"
        vid_path = self.output_home_path / 'video' / fname
        create_video(self.images, 30, vid_path)


class DefaultLoopIndicator(ILoopIndicator):
    looper_it: Iterator[int]
    
    def init(self, n_total: int):
        self.looper_it = iter(tqdm.trange(n_total))
        next(self.looper_it)
    
    def increment(self):
        try: next(self.looper_it)
        except StopIteration: pass


def do_single_run(
    source_path_str: str, target_path_str: str,
    n_iter: int, n_frames: int, error_precision: int,
    source_home_path: Path, output_home_path: Path,
):
    source_home_path.mkdir(parents=True, exist_ok=True)
    output_home_path.mkdir(parents=True, exist_ok=True)

    source_path = Path(source_path_str)
    # 如果输入文件名不是.csv结尾，那么加上这个后缀
    if source_path.suffix != '.csv':
        source_path = source_path.with_name(source_path.name + '.csv')
    # 如果输入文件名是相对路径，那么输入文件名将相对于源搜索目录
    if not source_path.is_absolute():
        source_path = source_home_path / source_path
    if not source_path.is_file():
        raise ValueError(f'找不到源数据集文件({source_path_str}，扩展为{source_path})')
    source = read_point_csv(source_path)

    # 目前只在默认的硬编码图形中搜索，文件读取功能有待开发
    try: target = algo.DEFAULT_DESTS[target_path_str]
    except KeyError:
        raise ValueError(f'找不到目标图形({target_path_str})')
    
    run_pattern(
        source, target,
        n_iter, n_frames, error_precision,
        DefaultFileSaver(source_path.stem, target_path_str, output_home_path),
        DefaultLoopIndicator(),
    )


if __name__ == '__main__':
    @click.command
    @click.argument('source', type=str)
    @click.argument('target', type=str)
    @click.option('--n-iter', type=int, default=100000)
    @click.option('--n-frames', type=int, default=100)
    @click.option('--error-precision', type=int, default=2)
    @click.option('--source-home', 'source_home_str', type=str, default='seed_datasets')
    @click.option('--output-home', 'output_home_str', type=str, default='results')
    def main(
        source: str, target: str,
        n_iter: int, n_frames: int, error_precision: int,
        source_home_str: str, output_home_str: str,
    ):
        laucher_config = get_launcher_config()
        source_home_str = laucher_config.get('source_home', source_home_str)
        output_home_str = laucher_config.get('output_home', output_home_str)

        do_single_run(
            source, target,
            n_iter, n_frames, error_precision,
            Path(source_home_str), Path(output_home_str)
        )

    main()
