from __future__ import absolute_import, division, print_function, unicode_literals
from pathlib import Path
import warnings
import sys

warnings.filterwarnings("ignore")

__version__ = '1.03.0'

# Get path to mymodule
u_marking_gui_path = str(Path(__file__).parent)
sys.path.append(u_marking_gui_path)


from .main import *
