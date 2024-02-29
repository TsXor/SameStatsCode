import abc
import itertools

from .utils import *


class IDestination(abc.ABC):
    '''目标图形接口'''

    @abc.abstractmethod
    def distance(self, point: Point) -> float:
        '''求某点到该图形的最短距离'''
        raise NotImplementedError


class ConcentricCirclesDestination(IDestination):
    '''同心圆目标图形'''

    center: Point
    radius_list: list[float]

    def __init__(self, center: Point, radius_list: list[float]) -> None:
        self.center = center
        self.radius_list = radius_list

    def distance(self, point: Point) -> float:
        dis = point_distance(point, self.center)
        return min(abs(dis - r) for r in self.radius_list)


class GridPointsDestination(IDestination):
    '''网格点目标图形'''
    
    xs: list[float]
    ys: list[float]

    def __init__(self, xs: list[float], ys: list[float]) -> None:
        self.xs = xs
        self.ys = ys
    
    def distance(self, point: Point) -> float:
        return min(point_distance(point, gridp)
                   for gridp in itertools.product(self.xs, self.ys))


class LineShapeDestination(IDestination):
    '''线段组成的目标图形'''

    lines: list[Line]

    def __init__(self, lines: list[Line]) -> None:
        self.lines = lines
    
    def distance(self, point: Point) -> float:
        return min(point_line_distance(point, l) for l in self.lines)


class PolylineDestination(LineShapeDestination):
    '''折线/多边形目标图形'''

    def __init__(self, points: list[Point], connect_polygon: bool = False) -> None:
        '''当connect_polygon为真，折线会首尾相连形成多边形'''
        if len(points) < 3: raise ValueError
        lines = [(points[i], points[i+1]) for i in range(len(points) - 1)]
        if connect_polygon: lines.append((points[-1], points[0]))
        super().__init__(lines)
