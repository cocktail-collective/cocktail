import functools


def run_once(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if wrapper.has_run:
            return
        else:
            wrapper.has_run = True
            return func(*args, **kwargs)

    wrapper.has_run = False
    return wrapper
