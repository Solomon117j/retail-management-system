@echo off
echo Starting Django development server (HTTP)...
echo.
echo Access the site at: http://127.0.0.1:8000
echo.
set DEBUG=true
python manage.py runserver 127.0.0.1:8000
pause
