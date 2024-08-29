import os
from functools import partial
from itertools import product
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation
from matplotlib.artist import Artist

FRAME_COUNT = 300

N = 40
STEPS = (-1, 0, 1)
NEIGHBORS_STEPS = set(product(STEPS, STEPS)).difference([(0, 0)])


def generate_data(n=N, how='random'):
    c = (n // 2, n // 2)
    if how == 'random':
        a = np.random.rand(n, n) * 0.6
    elif how == 'T':
        a = np.zeros((n, n))
        a[*c] = 1
        a[c[0], c[1] - 1] = 1
        a[c[0], c[1] + 1] = 1
        a[c[0] + 1, c[1]] = 1
    elif how == 'chaos':
        a = np.zeros((n, n))
        a[*c] = 1
        a[c[0], c[1] - 1] = 1
        a[c[0], c[1] + 1] = 1
        a[c[0] + 1, c[1]] = 1
        a[c[0] - 1, c[1] - 1] = 1
    else:
        raise ValueError('Invalid value for `how`')
    a = a.round().astype(int)
    return a


def generate_1d_data(n=N, how='random'):
    c = n // 2
    if how == 'random':
        a = np.random.rand(1, n) * 0.6
    elif how == 'center':
        a = np.zeros((1, n))
        a[0, c] = 1
    # elif how == 'chaos':
    #     a = np.zeros((n, n))
    #     a[*c] = 1
    #     a[c[0], c[1] - 1] = 1
    #     a[c[0], c[1] + 1] = 1
    #     a[c[0] + 1, c[1]] = 1
    #     a[c[0] - 1, c[1] - 1] = 1
    else:
        raise ValueError('Invalid value for `how`')
    a = a.round().astype(int)
    return a


def game_of_life(data: np.ndarray) -> np.ndarray:
    new_data = np.copy(data)
    for i, j in product(range(data.shape[0]), range(data.shape[1])):
        cell = data[i, j]
        n_neighbors = sum(
            data[i + si, j + sj]
            for si, sj in NEIGHBORS_STEPS
            if 0 <= i + si < data.shape[0] and 0 <= j + sj < data.shape[1]
        )

        if cell == 0 and n_neighbors == 3:
            # Any dead cell with exactly 3 live neighbours becomes a live cell, as if by reproduction.
            new_data[i, j] = 1

        elif cell == 1 and n_neighbors not in (2, 3):
            # Any live cell with 2 or 3 live neighbours lives on to the next generation.
            # Any live cell with fewer than 2 live neighbours dies, as if by underpopulation.
            # Any live cell with more than 3 live neighbours dies, as if by overpopulation.
            new_data[i, j] = 0

    return new_data


def rule_1d(data: np.ndarray, rule_number=30) -> np.ndarray:
    """
    current pattern                       111 110 101 100 011 010 001 000
    new state for center cell in rule 30   0   0   0   1   1   1   1   0
    new state for center cell in rule 110  0   1   1   0   1   1   1   0
    """
    s, n = data.shape
    new_data = np.copy(data)
    if rule_number == 30:
        one_patterns = ('100', '011', '010', '001')
    elif rule_number == 110:
        one_patterns = ('110', '101', '011', '010', '001')
    else:
        raise ValueError('Invalid value for `rule_number`')
    for i in range(1, n - 1):
        pattern = ''.join(str(int(data[0, i + si])) for si in STEPS)
        new_state = 1 if pattern in one_patterns else 0
        new_data[0, i] = new_state
    return new_data


def get_fun_str(fun) -> str:
    if isinstance(fun, partial):
        main_fun = fun.func.__name__
        kw = '_'.join(f'{k}_{v}' for k, v in fun.keywords.items())
        return f'{main_fun}_{kw}'
    return fun.__name__


def cellular_automaton(
    initial_setup='chaos',
    rule=game_of_life,
    save: bool | str = False,
    interval=100,
    frames=FRAME_COUNT,
    n_grid=N
):
    is_2d = rule == game_of_life
    is_1d = not is_2d
    dim = '1d' if is_1d else '2d'
    initial_data = generate_data(n=n_grid, how=initial_setup) if is_2d else generate_1d_data(
        n=n_grid,
        how=initial_setup,
    )
    kw = {}
    if is_1d:
        kw['figsize'] = (10, 3)
    fig, ax = plt.subplots(**kw)
    mat = ax.matshow(initial_data, cmap='gray_r')
    if is_1d:
        plt.yticks([])
    info = dict(step=0, arrays=[initial_data])

    def update(*args) -> Iterable[Artist]:
        info['step'] += 1
        print('update', info['step'])
        current = mat.get_array()
        new = rule(current)
        info['arrays'].append(new)
        mat.set_data(new)
        return mat

    ani = animation.FuncAnimation(fig, update, frames=frames, interval=interval, repeat=False)
    name = ''
    if save:
        name = f"animation_{dim}_{get_fun_str(rule)}_{initial_setup}_{frames}_{interval}"
        ani.save(f"{name}.mp4")
        if save == 'gif':
            os.system(f'convert {name}.mp4 {name}.gif')
    else:
        plt.show()

    if is_1d:
        history = np.vstack(info['arrays'])
        fig, ax = plt.subplots()
        ax.matshow(history, cmap='gray_r')
        plt.ylabel('Step')
        if save:
            name_history = name + '_history'
            plt.savefig(f'{name_history}.png')
        plt.show()


if __name__ == '__main__':
    cellular_automaton(
        # save='gif',
        n_grid=60,  # number of tiles in the grid
        frames=100,  # number of frames (aka steps)
        rule=game_of_life,  # type of evolution law
        initial_setup='chaos',  # initial state
        interval=200,  # interval between two steps (in milliseconds)
    )
