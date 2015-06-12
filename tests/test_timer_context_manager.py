"""Tests for the timer module and Stopwatch, for Python 2.6 and above.

All tests related to context managers and the with statement should be in
this file. For everything else, see the test_timer module.
"""

import unittest
import functools

from timer import Stopwatch  # Class to be tested.

# Test timing function.
DELTA = 1.5
def gen():
    x = DELTA
    while True:
        yield x
        x += DELTA

mock_time = functools.partial(next, gen())

assert mock_time() == DELTA
assert mock_time() == 2*DELTA
assert mock_time() == 3*DELTA

class Stopwatch_Tests(unittest.TestCase):
    """Testing Stopwatch as context manager."""

    def test_count(self):
        with Stopwatch(verbose=False) as sw:
            x = 1
        self.assertEqual(sw.count, 1)

    def test_elapsed(self):
        with Stopwatch(timer=mock_time, verbose=False) as sw:
            x = 1
        self.assertEqual(sw.elapsed, DELTA)

    def test_total(self):
        with Stopwatch(timer=mock_time, verbose=False) as sw:
            x = 1
        self.assertEqual(sw.total, DELTA)

    def test_running(self):
        with Stopwatch(verbose=False) as sw:
            self.assertTrue(sw.running)
        self.assertFalse(sw.running)

    def test_reset(self):
        with Stopwatch(verbose=False) as sw:
            x = 1
        sw.reset()
        self.assertEqual(sw.count, 0)
        self.assertEqual(sw.total, 0.0)
        self.assertEqual(sw.elapsed, 0.0)
        self.assertFalse(sw.running)


if __name__ == '__main__':
    import unittest
    unittest.main()

