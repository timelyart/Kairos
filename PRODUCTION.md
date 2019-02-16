# Create Kairos Distribution for public use #
1. [File preparation](#python-file-preparation)
2. [Generate C code](#generate-c-code)
3. [Install](#install)
4. [Clean up](#clean-up)

Alternatively, you can automate steps 2-4 by running (Windows CMD):
`build_public.bat`

## Python file preparation ##
For each python file you wish to generate C for, do the following:
* Add it to setup.py under extension modules (both for generation and linking), e.g. `Extension('tv.tv', ['tv//tv.py'], **ext_options)` and `Extension('tv.tv', ['tv//tv.pyd'], **ext_options)`
* Add it to process.bat so that the output file is properly named (as per setup.py), in the following format: `ren <basename>.cp37-win32.pyd <basename>.pyd`, for example: `ren tv.cp37-win32.pyd tv.pyd`
* If you want to obfuscate the source code, add it to process.bat again in the following format: `del <basename>.py`, for example: `del tv.py`

## Generate C code ##
Generate C code:

`python setup.py build_ext --inplace`

## Install dependencies 
Install dependencies: 

`python setup.py install`

## Clean up:
Process the generated files by running (Windows CMD): `process.bat`

The script will do the following:
* Rename \<basename>.cp37-win32.pyd files to \<basename>.pyd
* Remove source files
* Remove unnecessary files 
