import time

def format_response(data, status="success"):
    return {
        "status": status,
        "data": data
    }

class Timer:
    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.interval = self.end - self.start