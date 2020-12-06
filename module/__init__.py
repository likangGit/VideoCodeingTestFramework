import os
modules = os.listdir(os.path.dirname(__file__))
modules = [i.replace('.py','') for i in modules if i not in ['__pycache__', '__init__.py'] ]
__all__ = modules
from module import *
