"""
    Create a tag with a version number
    SCM will add 1 to the last number when using python setyp.pu sdist
    If you want to create version 1.1.5 going from version 1.1.4 create tag 1.1.4
    If you want to create version 1.2 going from version 1.1.4 create tag 1.1
    If you want to create version 2 going from version 1.1.4 create tag 1
"""
from setuptools import setup, find_packages, Extension
from pkg_resources import get_distribution
from os import path
import sys
from Cython.Build import cythonize

release = get_distribution('kairos').version
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

include_dirs = []
library_dirs = []
libraries = []
extra_link_args = []
extra_compile_args = []
ext_options = dict(
    include_dirs=include_dirs,
    library_dirs=library_dirs,
    libraries=libraries,
    extra_link_args=extra_link_args,
    extra_compile_args=extra_compile_args)

# When building from a repo, Cython is required.
if not cythonize:
    print('Cython.Build.cythonize not found. ')
    print('Cython is required to generate C code.')
    sys.exit(1)

# Define the extension modules.
ext_modules = cythonize([
    Extension('tv.tv', ['tv//tv.py'], **ext_options),
    ],
    compiler_directives={"language_level": "3"}
)

setup(
    name='Kairos',
    packages=find_packages(),
    url='https://github.com/timelyart/',
    license='End-User License Agreement: https://eulatemplate.com/live.php?token=F2am7Ud98HlFDECoTq2GYhIksQmn6T9A',
    author='timelyart',
    version=release,
    author_email='timelyart@protonmail.com',
    description='Kairos aims to help you save time by automating repetitive tasks on TradingView such as refreshing alerts and creating new ones.',
    long_description=long_description,
    install_requires=['pyyaml', 'beautifulsoup4', 'urllib3>=1.26.5', 'selenium>=3.141,<4', 'configparser', 'tools', 'pip',
                      'Pillow', 'requests', 'gspread', 'google-api-python-client', 'oauth2client', 'pymongo', 'dill', 'numpy',
                      'fastnumbers', 'psutil', 'tqdm', 'soupsieve'],
    extras_require={
        'platform_system == "Windows"': [],
        'platform_system == "Linux"': ['python3-Xlib'],
        'platform_system == "Darwin"': ['pyobjc-core', 'pyobjc']
    },
    zip_safe=False,
    ext_modules=ext_modules
)
