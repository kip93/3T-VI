#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_CPP_MIN_VLOG_LEVEL'] = '3'

from keras.layers import Dense, Dropout, Flatten, Input
from keras.models import Model
import numpy
import random
from typing import Union


class Board:
    """A model class to hold the game board and do operations with it."""
    def __init__(self, id: int = 0x15555):
        """Create a new empty board, or regenerate a board from a given id."""
        self._id = id

    def as_array(self) -> numpy.array:
        """Return a 3x3 tuple array representing the board, where -1=='X', 1=='O', and 0==empty."""
        return numpy.array([numpy.array([self.get(i, j) for j in range(3)]) for i in range(3)])

    def clear(self) -> 'Board':
        """Empties the game board. Returns self."""
        self._id = Board()._id
        return self

    def get(self, i: int, j: int) -> int:
        """Get the element in the ith row and jth column."""
        assert i in range(3), 'Index i out of range(3)'
        assert j in range(3), 'Index j out of range(3)'

        return (((self._id >> (6 * i)) & 0x3F) >> (j << 1) & 0x03) - 1

    def id(self):
        return self._id

    def invert(self) -> 'Board':
        return Board(self._id ^ ((0x15555 & self._id ^ 0x3FFFF) << 1 & 0x2AAAA))

    def result(self) -> Union[int, None]:
        """Check if the game is over. Return +1 if the 'O' won, 0 for a tie, -1 if 'X' won, and None otherwise."""
        id = self._id
        for k in range(3):
            row = id >> (6 * k) & 0x3F
            column = id >> (2 * k) & 0x30C3

            if row == 0x00 or column == 0x0000:
                return -1

            if row == 0x2A or column == 0x2082:
                return +1

        main_diagonal = id & 0x30303
        if main_diagonal == 0x00000:
            return -1
        if main_diagonal == 0x20202:
            return +1

        anti_diagonal = id & 0x03330
        if anti_diagonal == 0x00000:
            return -1
        if anti_diagonal == 0x02220:
            return +1

        # No empty spaces
        if id & 0x15555 == 0x00000:
            return 0
        return None

    def set(self, i: int, j: int, xo: int) -> 'Board':
        """Set the element in the ith row and the jth column inplace, as defined by xo. Returns self."""
        assert i in range(3), 'Index i out of range(3)'
        assert j in range(3), 'Index j out of range(3)'
        assert xo in [-1, +1], 'Invalid argument: xo. Must be either -1 or +1'

        index = (3 * i + j) << 1
        mask = 0x3FFFF ^ (0x3 << index)
        bit = {-1: 0x0, +1: 0x2}[xo] << index
        self._id = self._id & mask | bit
        return self

    def __hash__(self) -> int:
        return self._id

    def __eq__(self, other) -> bool:
        if isinstance(other, Board):
            return self._id == other._id
        return NotImplemented

    def __ne__(self, other) -> bool:
        return not self == other

    def __str__(self) -> str:
        return str('\n'.join(' '.join('X-O'[k + 1] for k in row) for row in self.as_array()))


class VI:
    """3T-VI's model class. This class contains the algorithm that plays Tic Tac Toe."""
    def __init__(self, name: str = '3T-VI'):
        """Class constructor. Initializes model and loads any previous progress made."""
        self._build()

        self._epsilon = 1.0
        self._experience = {}
        self._name = name.upper()

        self.load()

    def load(self):
        """Load previously stored model's weights from disk. Does nothing if there is nothing to load."""
        try:
            self._model.load_weights(os.path.join('res', 'progress', self._name + '.h5'))
            with open(os.path.join('res', 'progress', self._name + '.txt'), 'r') as file:
                self._epsilon = float(file.read())
        except OSError:
            pass

    def move(self, board: Board):
        """Ask 3T-VI to make a move, given the current board."""
        action = tuple(map(int, numpy.argmax(self._predict(board), axis=2).flat))
        if (self._epsilon > 0 and random.random() < 1 / self._epsilon) or board.get(*action) != 0:
            action = self._randomize(board)

        self._experience[Board(board.id())] = action

        return action

    def save(self):
        """Save the current model's weights to disk."""
        self._model.save_weights(os.path.join('res', 'progress', self._name + '.h5'))
        with open(os.path.join('res', 'progress', self._name + '.txt'), 'w') as file:
            file.write('{:.32f}'.format(self._epsilon))

    def train(self, result: int):
        """Train with the result of the last match. This method assumes that it is called after every match finishes."""
        X, y = self._prepare_batch(result)
        self._model.train_on_batch(X, y)

        self._epsilon = max(self._epsilon - 1e-4, 0)

    def _build(self):
        input = Input(shape=(3, 3), name='Input')

        layer = Flatten(name='Flatten')(input)
        for n in range(3):
            layer = Dense(9, activation='relu', name='Dense{0}'.format(n + 1))(layer)
            layer = Dropout(0.5, name='Dropout{0}'.format(n + 1))(layer)

        outputs = Dense(3, activation='softmax', name='OutputX')(layer), \
                  Dense(3, activation='softmax', name='OutputY')(layer)

        self._model = Model(inputs=input, outputs=outputs)
        self._model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['categorical_accuracy'])

        # self._model.summary()

    def _prepare_batch(self, result):
        reward = self._reward(result)

        items = [(k, v) for k, v in self._experience.items()]
        self._experience = {}

        keys, values = [k for k, v in items], [v for k, v in items]
        X = numpy.array([board.as_array() for board in keys])
        y0, y1 = [], []

        for before, after in zip(items[:-1], items[1:]):
            prediction = self._predict(before[0])
            y0.append(prediction[0][0])
            y1.append(prediction[1][0])

            prediction = self._predict(after[0])
            y0[-1][before[1][0]] = 0.9 * prediction[0][0][after[1][0]]
            y1[-1][before[1][1]] = 0.9 * prediction[1][0][after[1][1]]

        prediction = self._predict(keys[-1])
        y0.append(prediction[0][0])
        y1.append(prediction[1][0])
        y0[-1][values[-1][0]] = reward
        y1[-1][values[-1][1]] = reward
        y = [numpy.array(y0), numpy.array(y1)]

        return X, y

    def _predict(self, board):
        return self._model.predict(numpy.array([board.as_array()]))

    def _randomize(self, board):
        action = None
        while action is None or board.get(*action) != 0:
            action = random.randrange(3), random.randrange(3)

        return action

    def _reward(self, result):
        multiplier = min(1, 3 / len(self._experience))

        if result == 0:
            return +0.7 * multiplier
        elif result > 0:
            return +1.0 * multiplier
        elif result < 0:
            return -1.0 * multiplier

    def __repr__(self) -> str:
        return '<model.VI object [name=\'{0}\'] at 0x{1:X}>'.format(self._name, id(self))
