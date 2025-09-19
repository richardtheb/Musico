"""
PyAudioOp compatibility module for Python 3.13+.

This module provides compatibility for the pyaudioop module that was removed in Python 3.13+.
It imports from the pyaudioop_compat module to provide the necessary functionality.
"""

# Import all functions from the compatibility module
from pyaudioop_compat import *

# Re-export everything for compatibility
__all__ = [
    'ratecv', 'mul', 'add', 'bias', 'reverse', 'tostereo', 'tostereo',
    'lin2lin', 'lin2ulaw', 'ulaw2lin', 'AFMT_S16_LE', 'AFMT_S16_BE', 'AFMT_S16_NE'
]
