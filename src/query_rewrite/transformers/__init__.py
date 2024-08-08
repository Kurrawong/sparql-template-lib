import asyncio
import itertools
from abc import ABC
from concurrent.futures import ThreadPoolExecutor

from lark import Transformer

# from src.services.graph import GraphService


class BaseTransformer(Transformer, ABC):
    # def __init__(self, service: GraphService, vars: set[str]):
    #     self.service = service
    #     self.vars = vars
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

    # def _get_real_graph_iris(self, iri: str):
    #     future = self.executor.submit(
    #         lambda _iri: async_to_sync(self.service.real_graphs)([_iri]), iri
    #     )
    #     real_graphs = future.result()
    #     real_graph_iris = set(itertools.chain.from_iterable(real_graphs.values()))
    #
    #     for key in real_graphs.keys():
    #         if not real_graphs[key]:
    #             real_graph_iris.add(key)
    #
    #     real_graph_iris = list(sorted(real_graph_iris))
    #     return real_graph_iris
    #
    # def _get_all_virtual_graphs(self):
    #     future = self.executor.submit(
    #         lambda: async_to_sync(self.service.all_virtual_graphs)()
    #     )
    #     graph_iris = future.result()
    #     return graph_iris
