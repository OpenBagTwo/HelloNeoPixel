"""Test runner for use on either the desktop or microcontroller.

Usage:

$ python run_tests.py

or

$ micropython run_tests.py

or

>>> import run_tests
>>> run_tests.run_tests()
"""
import unittest


def run_tests():
    unittest.main("hello_neopixel.tests")


if __name__ == "__main__":
    run_tests()
