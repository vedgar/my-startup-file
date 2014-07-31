import sys

try:
    from functools import wraps
except ImportError:
    from backports import wraps

try:
    next
except NameError:
    # Likely Python 2.4 or 2.5.
    def next(it):
        return it.next()



class Stopwatch(object):
    """Time hefty or long-running code.

    (Timings taken with the Stopwatch class have a small amount of overhead.
    For small code snippets, or extremely fast operations, the overhead of
    the Stopwatch class may be significant, and you should use timeit.Timer
    instead.)

    Stopwatch instances can be used as a context manager to time code
    inside a ``with`` statement:

    >>> with Stopwatch():  #doctest: +SKIP
    ...     do_this()
    ...     do_that()
    ...
    time taken: 1.2345 seconds

    Alternatively you can manually start and stop a Stopwatch:

    >>> def example():
    ...     sw = Stopwatch()
    ...     sw.start()
    ...     perform_calculations()
    ...     sw.stop()
    ...
    >>> example()  #doctest: +SKIP
    time taken: 1.2345 seconds

    Instances can also be used as instrumentation on functions or
    methods. See the ``decorate`` method for details.

    Stopwatch instances support being started and stopped repeatedly,
    and expose the following properties for introspection:

        count           The number of times the timer has run.
        elapsed         While the timer is running, the elapsed
                        time so far; when no timer is running,
                        the most recent timing.
        running         True if the timer is currently running,
                        otherwise False.
        total           The total accumulated time.

    """
    def __init__(self, timer=None, verbose=True, cutoff=0.001):
        """Initialise the Stopwatch instance.

        All arguments are optional, and a exposed as public attributes
        with the same name:

            timer:
                Timer function; if not given or None, the instance will
                try to pick the best timer function for your platform.

            verbose:
                If true (the default), the timer result is printed
                when the stopwatch stops (including on exit of the
                with block). If the elapsed time is too small, a
                warning is also printed. Otherwise, suppresses
                printing of the elapsed time and/or warning.

            cutoff:
                If None, elapsed time warnings are disabled; otherwise
                the amount of time in seconds below which a warning is
                displayed. Defaults to 0.001 second.

        """
        if timer is None:
            from timeit import default_timer as timer
        self.timer = timer
        self.verbose = verbose
        self.cutoff = cutoff
        self.reset()

    def reset(self):
        """Reset all the collected timer results."""
        try:
            del self._start
        except AttributeError:
            pass
        self._running = False
        self._count = 0
        self._elapsed = self._total = 0.0

    def start(self):
        """Start the timer.

        Called automatically when used as a context manager.
        If the stopwatch is already running, has no effect.
        """
        if not self._running:
            self._running = True
            self._count += 1
            self._start = self.timer()

    def stop(self):
        """Stop the timer.

        Called automatically when used as a context manager.
        If the stopwatch is already stopped, has no effect. Otherwise,
        it stops the timer, then calls the ``warn`` and ``report``
        methods if appropriate.
        """
        if self._running:
            self._running = False
            self._elapsed = self.timer() - self._start
            self._total += self._elapsed
            del self._start
            if self.verbose:
                if self.cutoff is not None and self.elapsed < self.cutoff:
                    self.warn()
                self.report()

    def report(self):
        """Report on time taken.

        Override this method to customize the reporting mechanism.
        """
        print('time taken: %f seconds' % self.elapsed)

    def warn(self):
        """Warn on short elapsed times.

        Override this method to customize the warning mechanism.
        """
        sys.stderr.write(
            "elapsed time is very small; consider using timeit.Timer"
            " for micro-timings of small code snippets\n"
            )

    @property
    def running(self):
        """True if the timer is currently running, else False."""
        return bool(self._running)

    @property
    def elapsed(self):
        """Elapsed time for the latest timing."""
        if self.running:
            return self.timer() - self._start
        else:
            return self._elapsed

    @property
    def total(self):
        """Total accumulated time for all timings."""
        if self.running:
            return self._total + self.elapsed
        else:
            return self._total

    @property
    def count(self):
        """Number of times the timer has been run."""
        return self._count

    # Context manager special methods.

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()

    # Decorator to add instrumentation to functions.

    @classmethod
    def decorate(cls, function):
        """Decorate functions with a Stopwatch instance as instrumentation.

        Wraps the decorated function so that each call to that function
        runs inside a wrap``self`` as context manager, recording total elapsed
        time. ``self`` is exposed as an attribute ``stopwatch``.

        >>> import time
        >>> @Stopwatch.decorate
        ... def func(a, b):
        ...     time.sleep(0.01)  # Simulate a long calculation.
        ...     return a + 2*b
        ...
        >>> func.stopwatch.verbose = False  # Disable reporting.
        >>> func(1, 2)
        5
        >>> func(2, 5)
        12
        >>> func.stopwatch.count
        2
        >>> func.stopwatch.elapsed >= 0.01
        True
        >>> func.stopwatch.total > func.stopwatch.elapsed
        True

        """
        stopwatch = cls()  # Use the defaults.

        @wraps(function)
        def inner(*args, **kwargs):
            # Keep this compatible with Python 2.4. What we want is:
            #   with stopwatch:
            #       return function(*args, **kwargs)
            #
            # but since 2.4 (and 2.5, without the appropriate __future__
            # directive) don't support the with statement, we have to
            # emulate it by manually calling the context manager.
            # See PEP 343 for details:
            #   http://www.python.org/dev/peps/pep-0343/

            exit = type(stopwatch).__exit__  # Don't call it yet.
            value = type(stopwatch).__enter__(stopwatch)
            exc = True
            try:
                try:
                    # The with block.
                    return function(*args, **kwargs)
                except:  # Catch *any* exception at all.
                    exc = False
                    if not exit(stopwatch, *sys.exc_info()):
                        raise
                    # The exception is swallowed if exit() returns True.
            finally:
                # The normal and non-local-goto cases are handled here.
                if exc:
                    exit(stopwatch, None, None, None)

        inner.stopwatch = stopwatch
        return inner

