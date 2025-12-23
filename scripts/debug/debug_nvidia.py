
import os
import sys
import importlib.util

print(f"Python: {sys.executable}")
try:
    import nvidia
    print(f"nvidia: {nvidia}")
except ImportError:
    print("nvidia not found")

try:
    import nvidia.cublas
    print(f"nvidia.cublas: {nvidia.cublas}")
    print(f"nvidia.cublas.__file__: {getattr(nvidia.cublas, '__file__', 'MISSING')}")
    print(f"nvidia.cublas.__path__: {getattr(nvidia.cublas, '__path__', 'MISSING')}")
except ImportError:
    print("nvidia.cublas not found")

try:
    import nvidia.cudnn
    print(f"nvidia.cudnn: {nvidia.cudnn}")
    print(f"nvidia.cudnn.__path__: {getattr(nvidia.cudnn, '__path__', 'MISSING')}")
except ImportError:
    print("nvidia.cudnn not found")
