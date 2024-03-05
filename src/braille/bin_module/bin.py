import ctypes as ct
import os

project_path = os.getcwd()
path_to_dll = os.path.join(project_path, "src", "braille", "bin_module", "bin_module.dll")

DLL = ct.CDLL(path_to_dll)

def bradley_binarization(pixels, width, height, bradley_param):
    """Takes list of grayskale pixels and converts to black-white accroding to Bradley algorihtm\n
    Args: pixels(List), width(int), height(int), bradley_param(int)
    Output: None
"""
    bradley_bin = ct.PYFUNCTYPE(None, ct.py_object, ct.py_object, ct.py_object, ct.py_object)(('bradley_binarization', DLL))
    bradley_bin(pixels, width, height, bradley_param)


bradley_bin = ct.PYFUNCTYPE(None, ct.py_object, ct.py_object, ct.py_object, ct.py_object)(('bradley_binarization', DLL))

bradley_bin.__doc__ = """Takes list of grayskale pixels and converts to black-white accroding to Bradley algorihtm\n
    Args: pixels(List), width(int), height(int), bradley_param(int)
    Output: None
"""
bradley_bin.__annotations__ = {
    'pixels':'grayscale pixels(list)',
    'width': 'image width(int)',
    'height': 'image height(int)',
    'bradley_param': 'number of secotors into which the image will be divided(int)'
    }

anti_aliasing = ct.PYFUNCTYPE(None, ct.py_object, ct.py_object, ct.py_object, ct.py_object)(('anti_aliasing', DLL))
anti_aliasing.__doc__ = """Takes list of grayscale pixels and applies antialising\n
    Args: pixels(List), width(int), height(int), intensity(int)
    Output: None
"""
anti_aliasing.__annotations__ = {
    'pixels':'grayscale pixels(list)',
    'width': 'image width(int)',
    'height': 'image height(int)',
    'intensity': 'anti_aliasing intensity(int)'
    }
