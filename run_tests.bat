@echo off
title FinGuard AI - Unit Test Suite
color 0A
echo ===============================================================================
echo                FINGUARD AI - VERIFICATION & UNIT TEST SUITE
echo ===============================================================================
echo.
python -m unittest discover tests -v
echo.
echo ===============================================================================
pause
