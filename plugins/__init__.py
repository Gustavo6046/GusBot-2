import os

__all__ = [x.rstrip(".py") for x in filter(lambda x: x.endswith(".py"), os.listdir("plugins\\"))]