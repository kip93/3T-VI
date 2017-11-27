# 3T-VI, a Machine Learning powered Virtual Intelligence that learns to play Tic-Tac-Toe

![](res/logo/logo.png)

![](http://forthebadge.com/images/badges/designed-in-ms-paint.svg)
![](http://forthebadge.com/images/badges/built-with-science.svg)
![](http://forthebadge.com/images/badges/powered-by-electricity.svg)
![](http://forthebadge.com/images/badges/certified-elijah-wood.svg)

The Tic-Tac-Toe Virtual Intelligence (or **3T-VI** for short) aims to learn how to play by a process of trial and error, having minimal feedback. For this a small [Deep Q Network](https://deepmind.com/research/dqn/) has been built using [Keras](https://keras.io/) with a [TensorFlow](https://github.com/tensorflow/tensorflow) backend.

## How does it work?

At the beginning **3T-VI** plays pseudo-randomly in order to gather some initial information to work with. Then it uses a process of "exploration", trying out unused approaches, in an attempt to follow and weight as many paths as possible. After a while these random choices start to disappear, in order to "exploit" the more successful options, and avoiding the losing paths. Eventually it stops exploring altogether, sticking to the exploitation of all the gathered information choosing exclusively the best possible moves. This process is known as "Exploration and Exploitation" (D'oh).

## Usage

The model itself can be found in the `model.py` file, and in there is everything needed to get it up and running, but a user interface has been provided as well, in the files `view.py` and `main.py`, containing the user interface and a controller between models and views, respectively. To run the user interface, simply run the `main.py` file.

In the given user interface, the approach taken to train **3T-VI** was to put it against another **3T-VI**. Why? Well, first, because this allows it to train against an equally good opponent, having at first random moves to help with the exploration phase of the training, and later they both play exploiting good moves, forcing each other to best its opponent. But most importantly:

![](https://media.giphy.com/media/Ri5Hs2Dr2VGj6/giphy.gif)

Finally, for an added bonus, the provided user interface has been enhanced with some lame memes, for your entertainment.

## Dependencies

The following lines list all dependencies and the oldest version they where tested against, along with instructions on how to install them.

### Python (3.6+)

For windows, I recommend to download [Anaconda](https://www.anaconda.com/download/). To install the rest of the dependencies use the generated Anaconda Prompt, and use conda instead of pip whenever possible.

For more details see [Anaconda package list and installation guide](https://docs.anaconda.com/anaconda/packages/pkg-docs)

For Linux and OSx, install via your OS' package manager. For example in Ubuntu:

```shell
$ sudo apt install python3.6
```

### Numpy (2.6+)

```shell
$ sudo pip install -U numpy
```

For more details, see [SciPy installation guide](https://scipy.org/install.html).

### TensorFlow (1.2+)

```shell
$ sudo pip install -U tensorflow
```

or

```shell
$ sudo pip install -U tensorflow-gpu
```

For more details, see [TensorFlow installation guide](http://www.tensorflow.org/install).

### h5py (2.7+)

```shell
$ sudo pip install -U h5py
```

For more details, see [h5py installation guide](http://docs.h5py.org/en/latest/build.html).

### Keras (2.0+)

```shell
$ sudo pip install -U keras
```

For more details, see [Keras installation guide](https://keras.io/#installation).

### PyQt (5.6+)

Not required by the model itself, but by the user interface

```shell
$ sudo pip install -U pyqt5
```

For more details, see [PyQt5 installation guide](http://pyqt.sourceforge.net/Docs/PyQt5/installation.html).
