@echo off
ren setup.py _setup.py
ren cython.py setup.py
REM Generating C code
python setup.py build_ext --inplace generate
REM Renaming files and cleaning source code
process.bat
REM Linking C code
python setup.py build_ext --inplace
:: REM Removing unnecessary files
:: TODO remove unnecessary files
::del setup.py
ren setup.py cython.py
ren _setup.py setup.py
REM Installing Kairos (test)
python setup.py install