from setuptools import setup, find_packages
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

setup(
    name='Kairos',
    url='https://github.com/timelyart/Kairos',
    packages=find_packages(),
    license='End-User License Agreement: https://www.eulatemplate.com/live.php?token=zduUYsiBp0PFzzX0UANHUodYVMifuNRp',
    author='timelyart',
    version='2.13',
    author_email='timelyart@protonmail.com',
    description='Kairos aims to help you save time by automating repetitive tasks on TradingView such as refreshing '
                'alerts and creating new ones.',
    long_description=long_description,
    install_requires=['pyyaml', 'beautifulsoup4', 'urllib3', 'selenium>=3.141,<4', 'configparser', 'pip', 'Pillow',
                      'requests', 'gspread', 'google-api-python-client', 'oauth2client', 'pymongo', 'dill', 'numpy',
                      'fastnumbers', 'psutil', 'Cython', 'tqdm', 'soupsieve'],
    extras_require={
        'platform_system == "Windows"': [],
        'platform_system == "Linux"': ['python3-Xlib', 'pyvirtualdisplay'],
        'platform_system == "Darwin"': ['pyobjc-core', 'pyobjc']
    },
)
