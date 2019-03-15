REM Removing unwanted files for distribution
@echo off
cd tv
ren tv.cp37-win32.pyd tv.pyd
del tv.py
del tv.c
:: remove old example files
del _browse.yaml
del _example.yaml
del _example_davo.yaml
del _screener_to_watchlist.yaml
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