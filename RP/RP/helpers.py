import threading, sys, functools, traceback
import logging

_logger = logging.getLogger("Lazy")

def lazy(on_error = _logger.warn):
    """Make a function immediately return a function of no args which, when called,
    waits for the result, which will start being processed in another thread.
    
    @lazy(logger.warn)
    def network_request(...):
        ...
    
    resource = network_request(...)
    ...
    use(resource())"""
    def inner(f):

        @functools.wraps(f)
        def lazy_thunked(*args, **kwargs):
            wait_event = threading.Event()

            result = [None]
            exc = [False, None]

            def worker_func():
                try:
                    func_result = f(*args, **kwargs)
                    result[0] = func_result
                except Exception:
                    exc[0] = True
                    exc[1] = sys.exc_info()
                    on_error("Lazy thunk has thrown an exception (will be raised on thunk()):\n%s" % (
                        traceback.format_exc()))
                finally:
                    wait_event.set()

            def thunk():
                wait_event.wait()
                if exc[0]:
                    raise exc[1][0], exc[1][1], exc[1][2]

                return result[0]

            t = threading.Thread(target=worker_func)
            t.daemon = True
            t.start()

            return thunk

        return lazy_thunked
    return inner

def memoize(obj):
    cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        if args not in cache:
            cache[args] = obj(*args, **kwargs)
        return cache[args]
    return memoizer
