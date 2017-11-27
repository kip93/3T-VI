#!/usr/bin/env python
# -*- coding: utf-8 -*-

import view


class Main(view.Game):
    def __init__(self):
        super().__init__()

        self._board_model = model.Board()
        self._vi_o_model = model.VI('3T-VI O')
        self._vi_x_model = model.VI('3T-VI X')

        self._start = random.choice([-1, +1])
        self._turn = self._start
        self._thinking = True
        self._checking = True

        self._step_timer = QTimer()
        self._step_timer.timeout.connect(self._step)
        self._step_timer.setInterval(int(self.delay() * 1000))

    def refresh(self, board: 'model.Board'):
        super().refresh(board)
        if self._step_timer.interval() != int(self.delay() * 1000):
            self._step_timer.setInterval(int(self.delay() * 1000))

    def _toggle(self):
        super()._toggle()
        if self.is_running():
            self._step_timer.start()
        else:
            self._step_timer.stop()

    def _check(self, result):
        if result < 0:
            self._x_wins += 1
            self.state_o = 'lost'
            self.state_x = 'won'
        elif result > 0:
            self._o_wins += 1
            self.state_o = 'won'
            self.state_x = 'lost'
        else:
            self._ties += 1
            self.state_o = 'tied'
            self.state_x = 'tied'

        self._vi_o_model.train(result)
        self._vi_x_model.train(-result)
        self._vi_o_model.save()
        self._vi_x_model.save()

        self._checking = False

    def _move(self):
        if self._turn == +1:
            move = self._vi_o_model.move(self._board_model)
            self._board_model.set(*move, +1)

        elif self._turn == -1:
            move = self._vi_x_model.move(self._board_model.invert())
            self._board_model.set(*move, -1)

        self._turn *= -1
        self._thinking = True

    def _reset(self):
        self._board_model.clear()
        self._start *= -1
        self._turn = self._start

        self._checking = True

    def _step(self):
        result = self._board_model.result()
        if result is None:
            if self._thinking:
                self._think()
            else:
                self._move()
        else:
            if self._checking:
                self._check(result)
            else:
                self._reset()

    def _think(self):
        if self.delay() != 0:
            if self._turn == +1:
                self.state_o = 'thinking'
                self.state_x = 'waiting'
            else:
                self.state_o = 'waiting'
                self.state_x = 'thinking'
            self._thinking = False


if __name__ == '__main__':
    view.splash_show()

    import model
    from PyQt5.QtCore import QTimer
    from PyQt5.QtWidgets import QApplication
    import random

    view.splash_remove()

    app = QApplication([])
    window = Main()

    exit(app.exec_())
