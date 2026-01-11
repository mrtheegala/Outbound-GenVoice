@echo off
echo ========================================
echo   Healthcare AI Voice Agent Demo
echo ========================================
echo.
echo [1/3] Starting Ngrok Tunnel...
start "Ngrok Tunnel" cmd /k ngrok http 3000
echo     Waiting for Ngrok to initialize...
timeout /t 3 /nobreak > nul
echo     IMPORTANT: Copy the ngrok HTTPS URL (e.g., https://xxxx.ngrok-free.app)
echo     and update NGROK_HTTPS_URL in __config__.py (line 63)
echo.
echo [2/3] Starting FastAPI Server...
start "FastAPI Server" cmd /k python app.py
echo     Waiting for server to start...
timeout /t 5 /nobreak > nul
echo.
echo [3/3] Starting Streamlit Interface...
start "Streamlit UI" cmd /k streamlit run streamlit_app.py
echo.
echo ========================================
echo   Demo Started Successfully!
echo ========================================
echo.
echo Ngrok Tunnel:   See Ngrok window for URL
echo FastAPI Server: http://localhost:3000
echo Streamlit UI:   http://localhost:8501
echo.
echo REMINDER: Update __config__.py with your ngrok URL!
echo.
echo Press any key to stop all services...
pause > nul
echo.
echo Stopping all services...
taskkill /FI "WINDOWTITLE eq Ngrok Tunnel*" /T /F > nul 2>&1
taskkill /FI "WINDOWTITLE eq FastAPI Server*" /T /F > nul 2>&1
taskkill /FI "WINDOWTITLE eq Streamlit UI*" /T /F > nul 2>&1
echo.
echo All services stopped.
pause
