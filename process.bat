REM Renaming files and cleaning code
@echo off
cd tv
ren tv.cp37-win32.pyd tv.pyd
del tv.py
del tv.c
cd ..
rmdir /Q /S img
rmdir /Q /S build
rmdir /Q /S dist
rmdir /Q /S Kairos.egg-info
rmdir /Q /S .github
del .gitignore
del DONATE.md
del PRODUCTION.md
@echo on