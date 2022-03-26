from setuptools import setup
from Cython.Build import cythonize

setup(
    name='Lichess db fast parsing.',
    ext_modules=cythonize("fast_parsing_lib.py"),
    zip_safe=False,
)