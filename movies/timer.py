import time

def measure_time(label):   # 👈 decorator argument
    def decorator(func):   # 👈 actual decorator
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            end = time.perf_counter()
            print(f"{label} - {func.__name__} took {end - start:.6f}s")
            return result
        return wrapper
    return decorator