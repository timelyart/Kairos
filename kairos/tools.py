# File: tools.py


class Switch:
    def __init__(self, value): self._val = value

    def __enter__(self): return self

    def __exit__(self, type, value, traceback): return False # Allows traceback to occur

    def __call__(self, *mconds): return self._val in mconds

