@echo off
ren setup.py _setup.py
ren cython.py setup.py
@echo on
REM Generating C code
python setup.py build_ext --inplace
@echo off
:: Rename setup.py to cython.py and _setup.py to setup.py
ren setup.py cython.py
ren _setup.py setup.py
@echo on
REM Installing Kairos
python setup.py install
REM Clean up the distribution
call process.bat
del process.bat
:: Remove cython.py (optional)
del cython.py
