@echo off
echo Setting up Math Routing Agent server...

echo.
echo Creating directories...
python setup.py

echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Loading sample data...
python load_sample_data.py

echo.
echo Setup complete!
pause