"""Test the timer module and Stopwatch class.

This module is expected to work with Python 2.4 and 2.5, consequently do
not test anything related to the with statement here. For tests related to
the with statement and context managers, see test_timer_context_manager.py.
"""

import unittest

from timer import Stopwatch  # Class to be tested.

# Keep this compatible with Python 2.4.
try:
    next
except NameError:
    def next(it):
        return it.next()

# Test timing function.
def gen(delta):
    x = delta
    while True:
        yield x
        x += delta

DELTA = 1.5
def mock_time(_it=gen(DELTA)):
    return next(_it)

assert mock_time() == DELTA
assert mock_time() == 2*DELTA
assert mock_time() == 3*DELTA


class MyStopwatch(Stopwatch):
    """Used for testing the warn method."""
    def __init__(self, *args, **kwargs):
        super(MyStopwatch, self).__init__(*args, **kwargs)
        self.warned = False
    def warn(self):
        self.warned = True
    def report(self):
        pass


class Stopwatch_Tests(unittest.TestCase):
    """Testing Stopwatch (but not as a context manager).

    For context manager tests, see the test_timer26 module.
    """

    def test_attributes(self):
        # Test that Stopwatch instances have the expected attributes.
        sw = Stopwatch(mock_time, True, 0.1)
        self.assertEqual(sw.timer, mock_time)
        self.assertEqual(sw.verbose, True)
        self.assertEqual(sw.cutoff, 0.1)

    def test_count(self):
        # Test that the count attribute is incremented correctly.
        sw = Stopwatch(verbose=False)
        self.assertEqual(sw.count, 0)
        for i in range(1, 6):
            sw.start(); sw.stop()
            self.assertEqual(sw.count, i)

    def test_elapsed(self):
        # Test that the elapsed attribute is calculated correctly.
        sw = Stopwatch(timer=mock_time, verbose=False)
        self.assertEqual(sw.elapsed, 0.0)
        for i in range(5):
            sw.start(); sw.stop()
            self.assertEqual(sw.elapsed, DELTA)

    def test_total(self):
        # Test that the total attribute is calculated correctly.
        sw = Stopwatch(timer=mock_time, verbose=False)
        self.assertEqual(sw.total, 0.0)
        for i in range(5):
            self.assertEqual(sw.total, i*DELTA)
            sw.start(); sw.stop()
        self.assertEqual(sw.total, (i+1)*DELTA)

    def test_running(self):
        # Test that the running flag is set and cleared correctly.
        sw = Stopwatch(verbose=False)
        self.assertFalse(sw.running)
        sw.start()
        self.assertTrue(sw.running)
        sw.stop()
        self.assertFalse(sw.running)

    def test_reset(self):
        # Test the reset method.
        sw = Stopwatch(verbose=False)
        for i in range(5):
            sw.start(); sw.stop()
        sw.reset()
        self.assertEqual(sw.count, 0)
        self.assertEqual(sw.total, 0.0)
        self.assertEqual(sw.elapsed, 0.0)
        self.assertFalse(sw.running)

    def test_count_while_running(self):
        # Test that count is calculated correctly while running.
        sw = Stopwatch(verbose=False)
        self.assertEqual(sw.count, 0)
        sw.start()
        self.assertEqual(sw.count, 1)
        sw.stop()
        self.assertEqual(sw.count, 1)

    def test_elapsed_while_running(self):
        # Test that elapsed is calculated correctly while running.
        sw = Stopwatch(timer=mock_time, verbose=False)
        sw.start()
        self.assertEqual(sw.elapsed, DELTA)
        self.assertEqual(sw.elapsed, 2*DELTA)
        sw.stop()
        self.assertEqual(sw.elapsed, 3*DELTA)
        # Check it again, to be sure it's no longer increasing.
        self.assertEqual(sw.elapsed, 3*DELTA)

    def test_total_while_running(self):
        # Test that total is calculated correctly while running.
        sw = Stopwatch(timer=mock_time, verbose=False)
        sw.start()
        self.assertEqual(sw.total, DELTA)
        self.assertEqual(sw.total, 2*DELTA)
        sw.stop()
        self.assertEqual(sw.total, 3*DELTA)
        # Check it again, to be sure it's no longer increasing.
        self.assertEqual(sw.total, 3*DELTA)

    def test_report_method(self):
        # Test the report method is called when appropriate.
        reported = [False]
        class MyStopwatch(Stopwatch):
            def report(self):
                reported[0] = True
        # First check it is not called when verbose is False.
        sw = MyStopwatch(verbose=False, cutoff=None)
        sw.start(); sw.stop()
        self.assertFalse(reported[0],
            'report method was called when verbose=False')
        # Second check it is called when verbose is True.
        sw.verbose = True
        sw.start(); sw.stop()
        self.assertTrue(reported[0],
            'report method was not called when verbose=True')

    def test_warn_is_called(self):
        # Test that the warn method is called when appropriate.
        sw = MyStopwatch(verbose=True, cutoff=1e99)
        assert not sw.warned
        sw.start(); sw.stop()
        assert sw.elapsed < sw.cutoff
        self.assertTrue(sw.warned,
            'warn method was not called when it should have been')

    def test_warn_not_called_when_cutoff_is_none(self):
        # Test that the warn method is not called when cutoff is None.
        sw = MyStopwatch(verbose=True, cutoff=None)
        assert not sw.warned
        sw.start(); sw.stop()
        self.assertFalse(sw.warned,
            "warn method was called when it shouldn't have been")

    def test_warning_is_disabled(self):
        # Test that the warn method is not called when verbose=False.
        sw = MyStopwatch(verbose=False, cutoff=1e99)
        assert not sw.warned
        sw.start(); sw.stop()
        self.assertFalse(sw.warned,
            "warn method was called when it shouldn't have been")



if __name__ == '__main__':
    import unittest
    unittest.main()

