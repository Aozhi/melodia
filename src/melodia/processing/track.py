import math
import random

from melodia.core import Track


def randomize_velocities(
        track: Track,
        minimum: float = 0.5,
        maximum: float = 1.0,
        mean: float = 0.75,
        variance: float = 0.01
) -> Track:
    """
    Randomizes velocities of the notes in the track.
    Returns copy of the provided track with randomized velocities.

    :param track: input track
    :param minimum: minimum velocity (default: 0.5)
    :param maximum: maximum velocity (default: 1.0)
    :param mean: mean velocity (default: 0.75)
    :param variance: velocity variance (default: 0.01)
    :return: new track with randomized velocities
    """
    if not 0 <= minimum <= 1.0:
        raise ValueError('minimum velocity must be in range [0.0, 1.0]')

    if not 0 <= maximum <= 1.0:
        raise ValueError('maximum velocity must be in range [0.0, 1.0]')

    if not 0 <= mean <= 1.0:
        raise ValueError('mean velocity must be in range [0.0, 1.0]')

    if not variance >= 0:
        raise ValueError('variance must be positive')

    result = Track(signature=track.signature)

    std = math.sqrt(variance)

    for position, note in track:
        new_velocity = max(minimum, min(maximum, random.gauss(mean, std)))
        result.add(note.with_velocity(new_velocity), position)

    return result
