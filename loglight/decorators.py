import functools
import inspect
import traceback
import time
from loglight import log


def log_function(level="info"):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Log function call
            func_name = func.__name__
            log.log(level, f"Calling {func_name}", function=func_name)
            try:
                result = func(*args, **kwargs)
                log.log(level, f"Completed {func_name}", function=func_name)
                return result
            except Exception as e:
                log.error(f"Error in {func_name}", function=func_name, error=str(e))
                raise
        return wrapper
    return decorator


def log_exceptions(level="error"):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Structured exception logging
                log.log(level, f"Exception in {func.__name__}",
                        function=func.__name__,
                        exception_type=type(e).__name__,
                        exception_message=str(e),
                        traceback=traceback.format_exc())
                raise
        return wrapper
    return decorator


def log_timing(level="info"):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            log.log(level, f"Starting {func.__name__}", function=func.__name__)
            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                duration = end_time - start_time
                log.log(level, f"Completed {func.__name__}", function=func.__name__, duration=duration)
                return result
            except Exception as e:
                end_time = time.time()
                duration = end_time - start_time
                log.error(f"Error in {func.__name__}", function=func.__name__, error=str(e), duration=duration)
                raise
        return wrapper
    return decorator


def log_with_metadata(metadata=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            extra = metadata or {}
            log.info(f"Calling {func.__name__}", function=func.__name__, **extra)
            try:
                result = func(*args, **kwargs)
                log.info(f"Completed {func.__name__}", function=func.__name__, **extra)
                return result
            except Exception as e:
                log.error(f"Error in {func.__name__}", function=func.__name__, error=str(e), **extra)
                raise
        return wrapper
    return decorator
