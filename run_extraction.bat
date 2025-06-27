@echo off
echo ===================================
echo Zizhi Tongjian XML Corpus Extractor
echo ===================================
echo.

echo Activating conda environment: tsflow-env
call conda activate tsflow-env

if %errorlevel% neq 0 (
    echo Error: Failed to activate conda environment 'tsflow-env'
    echo Please make sure conda is installed and the environment exists.
    echo To create the environment, run: conda create -n tsflow-env python=3.8
    pause
    exit /b 1
)

echo Environment activated successfully!
echo.

echo Running extraction script...
python extract_zizhi_tongjian_xml.py

echo.
echo Extraction completed. Check the log file for details.
pause
