@echo off
echo ========================================
echo    Math Routing Agent - Startup
echo ========================================
echo.

echo Checking system status...
python quick_test.py

echo.
echo ========================================
echo Starting the server...
echo ========================================
echo Server will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.

python main.py