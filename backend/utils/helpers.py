def format_response(status: str, data: dict = None):
    return {
        "status": status,
        "data": data or {}
    }

class Timer:
    import time

    def __init__(self):
        self.start_time = None

    def start(self):
        self.start_time = self.time.time()

    def stop(self):
        if self.start_time is None:
            raise RuntimeError("Timer not started.")
        return self.time.time() - self.start_time