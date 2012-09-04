import gc

class Timer:
    def __init__(self, timer=None, disable_gc=False, verbose=True):
        if timer is None:
            from timeit import default_timer as timer
        self.timer = timer
        self.disable_gc = disable_gc
        self.verbose = verbose
        self.start = self.end = self.interval = None

    def __enter__(self):
        if self.disable_gc:
            self._gc_state = gc.isenabled()
            gc.disable()
        self.interval = None
        self.start = self.timer()
        return self

    def __exit__(self, *args):
        self.end = self.timer()
        if self.disable_gc and self._gc_state:
            gc.enable()
        self.interval = self.end - self.start
        if self.verbose:
            print('time taken: %f seconds' % self.interval)

