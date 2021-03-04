from time import time


class Timer:

    def __init__(self, interval, function, max_count=None):
        self.interval = interval
        self.function = function
        # max_count can be a countdown quantity or None for infinite.
        self.max_count = max_count
        self._count = 0
        # timed event is inactive when _next_time is None.
        self._next_time = time() + self.interval

    def check(self, check_time=None):
        if self._next_time is None:
            return False
        time_to_check = check_time or time()
        if time_to_check < self._next_time:
            return False
        self._count += 1
        if self.max_count is None or self._count < self.max_count:
            self._next_time = time_to_check + self.interval
        else:
            self._next_time = None
        return True

    def is_active(self):
        return self._next_time is not None
