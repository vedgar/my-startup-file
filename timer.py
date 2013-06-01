import gc

class Stopwatch:
    """Time long-running pieces of code.

    Time hefty or long-running block of code:

    >>> with Stopwatch():  #doctest: +SKIP
    ...     do_this()
    ...     do_that()
    ...
    time taken: 1.234567 seconds

    The Stopwatch class takes four optional arguments:

    timer::
        Timer function; by default, the default timer from the
        timeit module is used.

    allow_gc::
        If true (the default), the garbage collector is free to
        operate while the code block is running, otherwise, the
        garbage collector is temporarily disabled.

    verbose::
        If a true value (the default), the timer result is
        reported after the code block completes, and a warning
        displayed if the elapsed time is too small.

    cutoff::
        If None, elapsed time warnings are disabled; otherwise,
        the amount of time in seconds below which a warning is
        displayed. Defaults to 0.001.

    For non-interactive use, you can retrieve the time taken using the
    ``interval`` attribute:

    >>> with Stopwatch(verbose=False) as sw:  #doctest: +SKIP
    ...     do_this()
    ...     do_that()
    ...
    >>> print(sw.interval)  #doctest: +SKIP
    1.234567

    """
    def __init__(self, timer=None, allow_gc=True, verbose=True, cutoff=0.001):
        if timer is None:
            from timeit import default_timer as timer
        self.timer = timer
        self.allow_gc = allow_gc
        self.verbose = verbose
        self.cutoff = cutoff
        self.start = self.end = self.interval = None

    def __enter__(self):
        if not self.allow_gc:
            self._gc_state = gc.isenabled()
            gc.disable()
        self.interval = None
        self.start = self.timer()
        return self

    def __exit__(self, *args):
        self.end = self.timer()
        if not self.allow_gc and self._gc_state:
            gc.enable()
        self.interval = self.end - self.start
        self._report()

    def _report(self):
        if not self.verbose:
            return
        if self.cutoff is not None and self.interval < self.cutoff:
            print("elapsed time is very small; consider using timeit.Timer"
                  " for micro-timings of small code snippets")
        print('time taken: %f seconds' % self.interval)

