"""
    Create a tag with a version number
    SCM will add 1 to the last number when using python setyp.pu sdist
    If you want to create version 1.1.5 going from version 1.1.4 create tag 1.1.4
    If you want to create version 1.2 going from version 1.1.4 create tag 1.1
    If you want to create version 2 going from version 1.1.4 create tag 1
"""
from setuptools import setup, find_packages
from pkg_resources import get_distribution
from os import path
release = get_distribution('kairos').version
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

setup(
    name='Kairos',
    packages=find_packages(),
    url='https://github.com/timelyart/Kairos/',
    license='GNU General Public License v3.0',
    author='timelyart',
    version=release,
    author_email='timelyart@protonmail.com',
    description='Kairos aims to help you save time by automating repetitive tasks on TradingView such as refreshing alerts and creating new ones.',
    long_description=long_description,
    install_requires=['pyyaml', 'beautifulsoup4', 'urllib3', 'selenium', 'configparser', 'tools', 'pip>=18.1', 'Pillow', 'requests', 'pyautogui', 'pyperclip'],
    extras_require={
        'platform_system == "Windows"': [],
        'platform_system == "Linux"': ['python3-Xlib'],
        'platform_system == "Darwin"': ['pyobjc-core', 'pyobjc']
    },
)
