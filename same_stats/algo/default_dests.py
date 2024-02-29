from .dest_types import *

# 作者在原代码中硬编码的图形

DEFAULT_DESTS: dict[str, IDestination] = {
    'circle': ConcentricCirclesDestination((54.26, 47.83), [30]),
    'bullseye': ConcentricCirclesDestination((54.26, 47.83), [18, 37]),
    # 注：原代码的'center'是一个两端点重叠的线段
    # 笑点解析：这个形状正好会触发原代码距离计算的一个bug，详见utils.py
    'center': ConcentricCirclesDestination((54.26, 47.83), [0]),
    'dots': GridPointsDestination([25, 50, 75], [20, 50, 80]),
    
    'x': LineShapeDestination([
        ((20, 0), (100, 100)),
        ((20, 100), (100, 0)),
    ]),
    'h_lines': LineShapeDestination([
        ((0, y), (100, y)) for y in [10, 30, 50, 70, 90]
    ]),
    'v_lines': LineShapeDestination([
        ((x, 0), (x, 100)) for x in [10, 30, 50, 70, 90]
    ]),
    'wide_lines': LineShapeDestination([
        ((10, 0), (10, 100)),
        ((90, 0), (90, 100)),
    ]),
    'high_lines': LineShapeDestination([
        ((0, 10), (100, 10)),
        ((0, 90), (100, 90)),
    ]),
    'slant_up': LineShapeDestination([
        ((0, 0), (100, 100)),
        ((0, 30), (70, 100)),
        ((30, 0), (100, 70)),
        ((50, 0), (100, 50)),
        ((0, 50), (50, 100)),
    ]),
    'slant_down': LineShapeDestination([
        ((0, 100), (100, 0)),
        ((0, 70), (70, 0)),
        ((30, 100), (100, 30)),
        ((0, 50), (50, 0)),
        ((50, 100), (100, 50)),
    ]),

    'star': PolylineDestination([
        (28, 60),
        (52, 60),
        (60, 90),
        (68, 60),
        (92, 60),
        (72, 40),
        (80, 10),
        (60, 30),
        (40, 10),
        (48, 40),
    ], True),
    'down_parab':PolylineDestination([
        (x, 90 - ((x - 50) / 4) ** 2) for x in np.arange(0, 100, 3)
    ], False)
}
