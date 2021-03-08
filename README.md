# HelloNeoPixel

My introduction to controlling WS2812 individually-addressable
LEDs via a controller running [MicroPython](https://micropython.org/)

## Installation

### Local Setup

Local development and board management is handled via a `conda` environment.
The [Miniforge](https://github.com/conda-forge/miniforge) distribution is highly recommended.

Once you have `conda` installed, simply clone this repo, navigate to the project's root, and run:

```bash
$ conda env create
```

(the [`-f environment.yml`](environment.yml) is implicit),

then activate the development environment:

```bash
$ conda activate espy
```

This environment includes MicroPython, esptool and ampy, which should be everything you need to
work with MicroPython boards (I also recommend installing 
[`picocom`](https://github.com/npat-efault/picocom) while you're at it, though `screen` or the
[WebREPL](http://micropython.org/webrepl) will do in a pinch).

### On the PyBoard

Follow the
[MicroPython website's instructions](http://docs.micropython.org/en/latest/pyboard/quickref.html)
for setting up your particular microcontroller. When you're done, you can upload the
`hello_neopixel` package using the [`deploy.sh`](deploy.sh) script. With this repo cloned,
first navigate to the project's root directory, activate the development environment

```bash
$ conda activate espy
```

and then run the deploy script, which will build the package using `setup.py`, then use `ampy`
to upload it to the PyBoard (note that it will be installed in the root directory as opposed to
`/lib`).

From there, you can `import hello_neopixel` and get started with some animations.

## Tests

While `py.test` is included in this project's development
environment, the tests themselves are written using pure unittest,
as that's what's implemented in MicroPython, and the tests are intended
to be runnable directly on the microcontroller.

> :warning: The test suite currently cannot be run outside of MicroPython,
> as several MicroPython-specific libraries (namely `utime`) are not available
> on desktop platforms. This means no `py.test` until a workaround is implemented.

The recommended way to run the test suite is via the [`run_tests.py`](run_tests.py) script:

```bash
$ micropython run_tests.py
```

To run the test suite on the microcontroller itself via the REPL, first make sure the
unittest library is installed:

```python
>>> import upip
>>> upip.install('micropython-unittest')
```

and then run:

```python
>>> import unittest
>>> unittest.main("hello_neopixel.tests")
```

> :warning: Note the following issue with test discovery in `micropython-unittest`:
> https://github.com/micropython/micropython-lib/issues/414
