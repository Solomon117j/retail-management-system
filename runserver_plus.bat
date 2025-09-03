@echo off
echo Starting Django development server with runserver_plus (HTTPS)...
echo.
echo SSL Certificate: certs\devserver.crt
echo SSL Private Key: certs\devserver.key
echo.
echo Access the site at: https://127.0.0.1:8000
echo Note: You may need to accept the security warning for the self-signed certificate
echo.
python manage.py runserver_plus --cert certs\devserver.crt --key certs\devserver.key 127.0.0.1:8000
pause
