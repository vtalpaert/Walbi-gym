import numpy as np


def _clip(x, low, high):
    return max(low, min(high, x))


def constrain(x, in_min,  in_max, out_min, out_max, clip=False):
    if clip:
        x = _clip(x, in_min, in_max)
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def constrain_spaces(x, in_space, out_space, clip):
    assert in_space.shape == out_space.shape
    if len(in_space.shape) == 1:
        return np.array([
            constrain(
                value,
                in_space.low[index],
                in_space.high[index],
                out_space.low[index],
                out_space.high[index],
                clip=clip
            ) for index, value in enumerate(x)
        ], dtype=out_space.dtype)
    elif len(in_space.shape) == 2:
        return np.array([
            [
                constrain(
                    subvalue,
                    in_space.low[index][subindex],
                    in_space.high[index][subindex],
                    out_space.low[index][subindex],
                    out_space.high[index][subindex],
                    clip=clip
                ) for subindex, subvalue in enumerate(value)
            ] for index, value in enumerate(x)
        ], dtype=out_space.dtype)
