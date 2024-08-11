import asyncio
from abc import ABC
from concurrent.futures import ThreadPoolExecutor

from lark import Transformer


class BaseTransformer(Transformer, ABC):
    def __init__(self):
        def initializer():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        self.executor = ThreadPoolExecutor(max_workers=1, initializer=initializer)
        super().__init__()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.executor.shutdown()
