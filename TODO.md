# Deployment to Render.com

## Prerequisites
- GitHub repository: https://github.com/Solomon117j/retail_management_system
- Render account

## Steps to Deploy

### 1. Push Code to GitHub
- Ensure all changes are committed and pushed to the main branch

### 2. Create Render Web Service
- Go to Render Dashboard
- Click "New" > "Web Service"
- Connect your GitHub repository
- Configure the service:
  - Name: retail-management-system
  - Environment: Docker
  - Branch: main
  - Build Command: (leave default, uses Dockerfile)
  - Start Command: (leave default, uses CMD from Dockerfile)

### 3. Set Environment Variables
In Render service settings, add these environment variables:
- SECRET_KEY: Generate a new secret key (use `python -c "import secrets; print(secrets.token_urlsafe(50))"`)
- DEBUG: False
- ALLOWED_HOSTS: your-render-app.onrender.com
- DATABASE_URL: (provided by Render Postgres, copy from database settings)
- LOG_LEVEL: INFO
- SESSION_COOKIE_SECURE: True
- CSRF_COOKIE_SECURE: True
- CSRF_TRUSTED_ORIGINS: https://your-render-app.onrender.com
- MTN_MOMO_API_KEY: (your API key)
- MTN_MOMO_API_SECRET: (your API secret)
- PAYFAST_MERCHANT_ID: (your merchant ID)
- PAYFAST_MERCHANT_KEY: (your merchant key)
- MYGATE_MERCHANT_ID: (your merchant ID)
- MYGATE_APPLICATION_ID: (your application ID)
- EMAIL_HOST_USER: (your email)
- EMAIL_HOST_PASSWORD: (your email password)

### 4. Create Render Postgres Database
- In Render Dashboard, create a new Postgres database
- Note the DATABASE_URL from the database settings
- Add DATABASE_URL to the web service environment variables

### 5. Deploy
- Click "Create Web Service"
- Render will build and deploy automatically
- Monitor the build logs for any errors

### 6. Run Migrations
- After deployment, run migrations via Render shell or add a build command
- For initial deployment, you may need to run: `python manage.py migrate`

### 7. Collect Static Files
- Static files are collected during Docker build via Dockerfile

### 8. Test the Deployment
- Visit your Render app URL
- Test login, e-commerce features, etc.

## Post-Deployment Tasks
- Set up monitoring if needed
- Configure domain if required
- Set up backups for the database
