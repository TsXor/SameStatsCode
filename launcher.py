import sys, runpy
from datetime import datetime
from pathlib import Path

WHERE_AM_I = Path(__file__).parent
LAUNCHER_GLOBAL_NAME = '__launcher_config__'
MODULE_NAME = 'same_stats'

if __name__ == '__main__':
    if len(sys.argv) == 1:
        source = input('请输入源数据集名：')
        target = input('请输入转化目标名：')
        more_args = [source, target]
        sys.argv.extend(more_args)

    dt_now_str = datetime.now().strftime('%Y-%m-%d-%H-%M-%S') 
    laucher_config = {
        'source_home': str(WHERE_AM_I / 'seed_datasets'),
        'output_home': str(WHERE_AM_I / 'results' / f'run-{dt_now_str}'),
    }
    runpy.run_path(
        str(WHERE_AM_I / MODULE_NAME),
        {LAUNCHER_GLOBAL_NAME: laucher_config},
        '__main__',
    )
