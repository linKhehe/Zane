import asyncio
import functools


loop = asyncio.get_event_loop()


def manipulation(image_manager):
    def decorator(function):
        @functools.wraps(function)
        def wrapper(image, *args, **kwargs):
            image_bytes = image_manager.input(image)
            image_bytes = function(image_bytes, *args, **kwargs)
            return image_manager.output(image_bytes)
        return wrapper
    return decorator


def executor(function):
    @functools.wraps(function)
    def decorator(*args, **kwargs):
        partial = functools.partial(function, *args, **kwargs)
        future = loop.run_in_executor(None, partial)
        return future
    return decorator

