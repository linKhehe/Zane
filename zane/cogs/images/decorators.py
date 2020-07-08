from functools import wraps


def manipulation(image_manager, cmap=None):
    def decorator(function):
        @wraps(function)
        def wrapper(image, *args, **kwargs):
            image_bytes = image_manager.input(image)
            image_bytes = function(image_bytes, *args, **kwargs)
            return image_manager.output(image_bytes, cmap=cmap)
        return wrapper
    return decorator


def executor(function):
    @wraps(function)
    def decorator(*args, loop=None, **kwargs):
        future = loop.run_in_executor(None, function, *args, **kwargs)
        return future
    return decorator
