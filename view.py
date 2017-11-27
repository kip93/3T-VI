#!/usr/bin/env python
# -*- coding: utf-8 -*-


from multiprocessing import Process, Value
import os
from platform import system
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QFont, QIcon, QImage, QMouseEvent, QMovie, QPainter, QPixmap
from PyQt5.QtWidgets import QAction, QApplication, QDialog, QGridLayout, QHBoxLayout, QLabel, QMainWindow, QPushButton,\
    QSlider, QSplashScreen, QVBoxLayout, QWidget
import random


if system().lower() == 'windows':
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(u'kip93.3T-VI')


class Game(QMainWindow):
    """Game's main view, containing everything."""
    def __init__(self):
        """Class constructor. Create a window and put everything in it."""
        super().__init__()
        self._widgets()
        self._layout()
        self._add()
        self._other()

    def delay(self) -> float:
        """Return the delay between each player's moves."""
        return self._slider_view.value()

    def refresh(self, board: 'model.Board'):
        """Update the game's view."""
        self._vi_o_view.refresh(self.state_o)
        self._vi_x_view.refresh(self.state_x)
        self._board_view.refresh(board)
        self._scoreboard_view.refresh(self._x_wins, self._ties, self._o_wins)

    def is_running(self) -> bool:
        """Return whether the start button has been pressed."""
        return self._go.isChecked()

    def _add(self):
        self._controls_view.layout().addWidget(self._go)
        self._controls_view.layout().addWidget(self._space_view)
        self._controls_view.layout().addWidget(self._scoreboard_view)
        self._controls_view.layout().addWidget(self._slider_view)

        self._game_view.layout().addWidget(self._vi_o_view)
        self._game_view.layout().addWidget(self._board_view)
        self._game_view.layout().addWidget(self._vi_x_view)

        self.centralWidget().layout().addWidget(self._controls_view)
        self.centralWidget().layout().addWidget(self._game_view)

    def _layout(self):
        self._controls_view.setLayout(QHBoxLayout())
        self._controls_view.layout().setSpacing(10)

        self._game_view.setLayout(QHBoxLayout())
        self._game_view.layout().setSpacing(5)

        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(QVBoxLayout())
        self.centralWidget().layout().setSpacing(5)

    def _other(self):
        self.setWindowTitle('3T-VI')
        self.setWindowIcon(QIcon(os.path.join('res', 'icons', 'icon.png')))

        file_menu = self.menuBar().addMenu('&File')
        help_menu = self.menuBar().addMenu('&Help')

        exit_action = QAction('&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application.')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        about_action = QAction('&About', self)
        about_action.setStatusTip('Information about the program.')
        about_action.triggered.connect(self._about_view.exec_)
        help_menu.addAction(about_action)

        self.statusBar().setSizeGripEnabled(False)
        self.setFixedSize(self.sizeHint())

        self.show()

        self._refresh_timer.start()

    def _widgets(self):
        self._about_view = _About()
        self._board_view = _Board()
        self._slider_view = _Slider()
        self._space_view = QLabel(' ' * 4)
        self._space_view.setFont(QFont(QFont().defaultFamily(), 16))
        self._vi_o_view = _VI('3T-VI O')
        self._vi_x_view = _VI('3T-VI X')
        self.state_o = 'ready'
        self.state_x = 'ready'

        self._scoreboard_view = _Scoreboard()
        self._o_wins = 0
        self._x_wins = 0
        self._ties = 0

        self._start_icon = QIcon(os.path.join('res', 'icons', 'start.png'))
        self._stop_icon = QIcon(os.path.join('res', 'icons', 'stop.png'))

        self._go = QPushButton()
        self._go.setCheckable(True)
        self._go.setChecked(False)
        self._go.clicked.connect(self._toggle)
        self._go.setFixedSize(50, 50)
        self._go.setIcon(self._start_icon)
        self._go.setStatusTip('Start the simulation.')

        self._controls_view = QWidget()
        self._game_view = QWidget()

        self._refresh_timer = QTimer()
        self._refresh_timer.timeout.connect(lambda: self.refresh(self._board_model))
        self._refresh_timer.setInterval(1000 // 30)

    def _toggle(self):
        if self._go.isChecked():
            self._go.setIcon(self._stop_icon)
            self._go.setStatusTip('Stop the simulation.')
            self.statusBar().showMessage('Stop the simulation.')
        else:
            self._go.setIcon(self._start_icon)
            self._go.setStatusTip('Start the simulation.')
            self.statusBar().showMessage('Start the simulation.')


def splash_show():
    """Create a new thread and use it to show the splashscreen."""
    global splashscreen, wait
    wait = Value('i', True)
    splashscreen = Process(target=_splash_process, args=(wait,))
    splashscreen.start()


def splash_remove():
    """Close the splashscreen thread."""
    global splashscreen, wait
    wait.value = False
    splashscreen.join()
    del splashscreen, wait


class _About(QDialog):
    """A dialog widget containing a brief description of the program, legal information, and version number."""
    def __init__(self):
        """Class constructor. Initialize widgets and distribute them on the grid layout."""
        super().__init__()
        self._widgets()
        self._layout()
        self._add()
        self._other()

    def _add(self):
        self.layout().addWidget(self._description, 1, 1, 1, 2)
        self.layout().addWidget(QLabel(''), 2, 1)
        self.layout().addWidget(self._license, 3, 1, 1, 2)
        self.layout().addWidget(QLabel(''), 4, 1)
        self.layout().addWidget(self._version, 5, 1, 1, 2)
        self.layout().addWidget(self._author, 6, 1, 1, 2)
        self.layout().addWidget(self._github, 7, 1)
        self.layout().addWidget(self._ok, 7, 2)

    def _layout(self):
        self.setLayout(QGridLayout())
        self.layout().setSpacing(5)

    def _other(self):
        self.setWindowTitle('About')
        self.setWindowIcon(QIcon(os.path.join('res', 'icons', 'about.png')))
        self.setFixedSize(self.sizeHint())

    def _widgets(self):
        self._description = QLabel('Graphic User Interface for 3T-VI, using PyQt5 library for Python.')
        self._description.setWordWrap(True)

        self._license = QLabel('This software is distributed under '
                               '<a href=\'https://opensource.org/licenses/BSD-3-Clause\'>'
                               'the BSD 3-Clause license</a>.')
        self._license.setWordWrap(True)
        self._license.setTextFormat(Qt.RichText)
        self._license.setOpenExternalLinks(True)

        self._version = QLabel('Version: ' + 'BETA')

        self._author = QLabel('Author: Leandro E. Reina Kiperman.')

        self._github = QLabel('Github: <a href=\'http://link/to/github/\'>http://link/to/github/</a>.')
        self._github.setTextFormat(Qt.RichText)
        self._github.setOpenExternalLinks(True)

        self._ok = QPushButton('OK')
        self._ok.clicked.connect(self.close)
        self._ok.setFixedSize(QSize(80, 30))


class _Board(QLabel):
    """Widget class containing the Board UI."""
    def __init__(self):
        """Class constructor. Creates the widget and loads board resources from disk."""
        super().__init__()
        self._widgets()
        self._other()

    def refresh(self, board: 'model.Board'):
        """Refresh the board and it's pieces."""
        coords = [21, 103, 185]
        board_image = QImage(os.path.join('res', 'board', 'board.png'))
        self._painter.begin(board_image)
        for i in range(3):
            for j in range(3):
                if board.get(i, j) == -1:
                    self._painter.drawImage(coords[j], coords[i], self._x)
                elif board.get(i, j) == +1:
                    self._painter.drawImage(coords[j], coords[i], self._o)

        self._painter.end()
        self.setPixmap(QPixmap.fromImage(board_image))

    def _other(self):
        self.setStatusTip('Game Board. Left player is represented with \'O\', right player with \'X\'.')
        self.setPixmap(QPixmap.fromImage(QImage(os.path.join('res', 'board', 'board.png'))))

    def _widgets(self):
        self._x = QImage(os.path.join('res', 'board', 'x.png'))
        self._o = QImage(os.path.join('res', 'board', 'o.png'))
        self._painter = QPainter()


class _Loading(QSplashScreen):
    """A splashscreen to show while loading TensorFlow."""
    def __init__(self):
        """Class constructor. Loads a gif to show while loading."""
        path = os.path.join('res', 'loading', 'loading.gif')
        self._gif = QMovie(path)
        self._gif.jumpToFrame(0)
        super().__init__(self._gif.currentPixmap(), Qt.WindowStaysOnTopHint)
        self.showMessage('Loading, please wait...', color=Qt.yellow)
        self._gif.frameChanged.connect(self._update)
        self.setFixedSize(self.pixmap().size())
        self._gif.start()
        self.show()

    def mousePressEvent(self, event: QMouseEvent):
        """Override the method so the splashscreen won't go away by clicking."""

    def _update(self):
        self.setPixmap(self._gif.currentPixmap())


class _Scoreboard(QWidget):
    """Widget containing the game's score."""
    def __init__(self):
        """Class constructor. Instantiates labels to show."""
        super().__init__()
        self._widgets()
        self._layout()
        self._add()
        self._other()

    def refresh(self, x: int, t: int, o: int):
        """Update the game score."""
        self._x.setText('X: {}'.format(x))
        self._ties.setText('T: {}'.format(t))
        self._o.setText('O: {}'.format(o))

    def _add(self):
        self.layout().addWidget(self._o)
        self.layout().addWidget(self._ties)
        self.layout().addWidget(self._x)

    def _layout(self):
        self.setLayout(QVBoxLayout())
        self.layout().setSpacing(10)

    def _other(self):
        self.setStatusTip('Game score.')

    def _widgets(self):
        size_hint = QLabel('A: 1234567890')
        size_hint.setFont(QFont(QFont().defaultFamily(), 16))
        self._ties = QLabel('T: 0')
        self._ties.setFont(size_hint.font())
        self._ties.setFixedSize(size_hint.sizeHint())
        self._x = QLabel('X: 0')
        self._x.setFont(size_hint.font())
        self._x.setFixedSize(size_hint.sizeHint())
        self._o = QLabel('O: 0')
        self._o.setFont(size_hint.font())
        self._o.setFixedSize(size_hint.sizeHint())


class _Slider(QWidget):
    """Widget containing delay slider and labels for extra visualization."""
    def __init__(self):
        """Class constructor. Create and distribute widgets for the slider."""
        super().__init__()
        self._widgets()
        self._layout()
        self._add()
        self._other()

    def value(self) -> float:
        """Return the current value of the slider."""
        return self._slider.value() / 10

    def _add(self):
        self._row0.layout().addWidget(self._current)
        self._row1.layout().addWidget(self._min)
        self._row1.layout().addWidget(self._slider)
        self._row1.layout().addWidget(self._max)
        self.layout().addWidget(self._row0)
        self.layout().addWidget(self._row1)

    def _layout(self):
        self._row0.setLayout(QHBoxLayout())
        self._row0.layout().setSpacing(0)
        self._row0.layout().setAlignment(Qt.AlignCenter)

        self._row1.setLayout(QHBoxLayout())
        self._row1.layout().setSpacing(5)

        self.setLayout(QVBoxLayout())
        self.layout().setSpacing(5)

    def _other(self):
        self.setStatusTip('Set the delay between each player\'s movements.')

    def _update(self):
        self._current.setText('Delay: {0:.02f}s'.format(self.value()))

    def _widgets(self):
        self._slider = QSlider(Qt.Horizontal)
        self._slider.setMaximum(10)
        self._slider.setMinimum(1)
        self._slider.setTickInterval(1)
        self._slider.setTickPosition(QSlider.TicksBelow)
        self._slider.setValue(self._slider.minimum())
        self._slider.valueChanged.connect(self._update)

        self._max = QLabel('{0:.02f}s'.format(self._slider.maximum() / 10))
        self._min = QLabel('{0:.02f}s'.format(self._slider.minimum() / 10))
        self._current = QLabel('Delay: {0:.02f}s'.format(self.value()))

        self._row0 = QWidget()
        self._row1 = QWidget()


class _VI(QWidget):
    """Widget class containing 3T-VI interface."""
    def __init__(self, name: str):
        """Class constructor. Creates the widget prepares layout."""
        super().__init__()
        self._widgets()
        self._layout()
        self._add()
        self._other(name)

    def refresh(self, state: str):
        """Writes 3T-VI's state and selects an image to represent it."""
        state = state.lower()
        assert state in {'ready', 'lost', 'thinking', 'tied', 'waiting', 'won'}
        if self._text.text().lower() != state:
            path = os.path.join('res', 'states', state)
            path = os.path.join(path, random.choice([f for f in os.listdir(path)]))
            self._text.setText(state.capitalize())
            self._image.setPixmap(QPixmap(path))

    def _add(self):
        self.layout().addWidget(self._text)
        self.layout().addWidget(self._image)

    def _layout(self):
        self.setLayout(QVBoxLayout())
        self.layout().setSpacing(5)

    def _other(self, name):
        self.setStatusTip(name)
        self.refresh('ready')
        self.setFixedSize(self.sizeHint())

    def _widgets(self):
        self._text = QLabel()
        self._image = QLabel()


def _splash_process(wait: Value):
    """A splashscreen thread to allow loading in the main thread."""
    import time
    app = QApplication([])
    splashscreen = _Loading()
    while wait.value:
        app.processEvents()
        time.sleep(0)
    del splashscreen
