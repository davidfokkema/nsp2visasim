import importlib

metadata = importlib.metadata.metadata("nsp2visasim")
__version__ = metadata["version"]
