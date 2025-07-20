@echo off
echo Starting Math Routing Agent...

echo.
echo Activating virtual environment and installing dependencies...
cmd /c "venv\Scripts\activate.bat && cd server && pip install -r requirements.txt"

echo.
echo Starting server...
start cmd /c "cd server && ..\venv\Scripts\python.exe main.py"

echo.
echo Installing client dependencies...
cmd /c "cd client && npm install"

echo.
echo Starting client...
start cmd /c "cd client && npm run dev"

echo.
echo Math Routing Agent is now running!
echo Server: http://localhost:8000
echo Client: http://localhost:5173