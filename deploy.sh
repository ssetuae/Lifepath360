#!/bin/bash

# Deployment script for Learning Compass application to Render

# Set environment variables
export BACKEND_DIR="/home/ubuntu/shining_star_diagnostic/backend"
export FRONTEND_DIR="/home/ubuntu/shining_star_diagnostic/frontend/learning-compass-ui"

# Create requirements.txt for backend
echo "Creating requirements.txt for backend..."
cd $BACKEND_DIR
source venv/bin/activate
pip freeze > requirements.txt

# Add Gunicorn to requirements.txt if not already present
if ! grep -q "gunicorn" requirements.txt; then
  echo "gunicorn==20.1.0" >> requirements.txt
  echo "Added gunicorn to requirements.txt"
fi

# Add django-cors-headers to requirements.txt if not already present
if ! grep -q "django-cors-headers" requirements.txt; then
  echo "django-cors-headers==4.0.0" >> requirements.txt
  echo "Added django-cors-headers to requirements.txt"
fi

# Add whitenoise for static files
if ! grep -q "whitenoise" requirements.txt; then
  echo "whitenoise==6.4.0" >> requirements.txt
  echo "Added whitenoise to requirements.txt"
fi

# Add psycopg2-binary for PostgreSQL
if ! grep -q "psycopg2-binary" requirements.txt; then
  echo "psycopg2-binary==2.9.6" >> requirements.txt
  echo "Added psycopg2-binary to requirements.txt"
fi

# Add dj-database-url for database configuration
if ! grep -q "dj-database-url" requirements.txt; then
  echo "dj-database-url==2.0.0" >> requirements.txt
  echo "Added dj-database-url to requirements.txt"
fi

# Create Procfile for backend
echo "Creating Procfile for backend..."
echo "web: gunicorn learning_compass.wsgi:application" > $BACKEND_DIR/Procfile

# Create runtime.txt for backend
echo "Creating runtime.txt for backend..."
echo "python-3.10.12" > $BACKEND_DIR/runtime.txt

# Create .env.sample file for backend
echo "Creating .env.sample file for backend..."
cat > $BACKEND_DIR/.env.sample << EOL
SECRET_KEY=your_secret_key_here
DEBUG=False
ALLOWED_HOSTS=.render.com,localhost,127.0.0.1
DATABASE_URL=postgres://user:password@host:port/database
ENCRYPTION_KEY=your_encryption_key_here
OPENAI_API_KEY=your_openai_api_key_here
STRIPE_SECRET_KEY=your_stripe_secret_key_here
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key_here
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret_here
FRONTEND_URL=https://learning-compass-ui.render.com
EOL

# Update settings.py for production
echo "Updating settings.py for production..."
cat > $BACKEND_DIR/learning_compass/production_settings.py << EOL
import os
import dj_database_url
from datetime import timedelta

# Import base settings
from .settings import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Allow all hosts for now, will be restricted in render.yaml
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '.render.com').split(',')

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Simplified static file serving
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Add whitenoise middleware
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Import security settings
from .security_settings import *

# CORS settings
CORS_ALLOWED_ORIGINS = [
    os.environ.get('FRONTEND_URL', 'https://learning-compass-ui.render.com'),
]
CORS_ALLOW_CREDENTIALS = True

# Set session expiry time
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=30),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '20/hour',
        'user': '1000/day'
    },
}

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'learning_compass': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
EOL

# Create .env.sample file for frontend
echo "Creating .env.sample file for frontend..."
cat > $FRONTEND_DIR/.env.sample << EOL
REACT_APP_API_URL=https://learning-compass-api.render.com
REACT_APP_STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key_here
EOL

# Update package.json for frontend
echo "Updating package.json for frontend..."
cd $FRONTEND_DIR
if [ -f "package.json" ]; then
  # Add engines section if it doesn't exist
  if ! grep -q "\"engines\"" package.json; then
    sed -i '/^{/a \  "engines": {\n    "node": "20.18.0",\n    "npm": "10.x"\n  },' package.json
    echo "Added engines section to package.json"
  fi
  
  # Add build script if it doesn't exist
  if ! grep -q "\"build\"" package.json; then
    sed -i '/\"scripts\": {/a \    "build": "react-scripts build",' package.json
    echo "Added build script to package.json"
  fi
fi

# Create .gitignore file if it doesn't exist
echo "Creating .gitignore file..."
cat > /home/ubuntu/shining_star_diagnostic/.gitignore << EOL
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg
venv/

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
media/
staticfiles/

# React
node_modules/
/frontend/learning-compass-ui/build
/frontend/learning-compass-ui/.env
/frontend/learning-compass-ui/.env.local
/frontend/learning-compass-ui/.env.development.local
/frontend/learning-compass-ui/.env.test.local
/frontend/learning-compass-ui/.env.production.local
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Environment variables
.env
.env.local

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
EOL

# Create README.md for deployment
echo "Creating README.md for deployment..."
cat > /home/ubuntu/shining_star_diagnostic/DEPLOYMENT.md << EOL
# Learning Compass Deployment Guide

This document provides instructions for deploying the Learning Compass application to Render.

## Prerequisites

1. A Render account (https://render.com)
2. A GitHub repository with the Learning Compass code
3. OpenAI API key for AI-driven question generation
4. Stripe API keys for payment processing

## Deployment Steps

### 1. Fork or Clone the Repository

First, fork or clone the Learning Compass repository to your GitHub account.

### 2. Connect to Render

1. Log in to your Render account
2. Go to the Dashboard and click "New +"
3. Select "Blueprint"
4. Connect your GitHub account if you haven't already
5. Select the Learning Compass repository
6. Click "Connect"

### 3. Configure Environment Variables

Render will automatically detect the \`render.yaml\` file and create the services defined in it. You'll need to set the following environment variables:

- \`OPENAI_API_KEY\`: Your OpenAI API key
- \`STRIPE_SECRET_KEY\`: Your Stripe secret key
- \`STRIPE_PUBLISHABLE_KEY\`: Your Stripe publishable key
- \`STRIPE_WEBHOOK_SECRET\`: Your Stripe webhook secret

### 4. Deploy the Application

1. Click "Apply" to create the services
2. Render will automatically build and deploy the application
3. Once deployment is complete, you can access the application at the provided URLs

### 5. Database Setup

The database will be automatically created by Render. To initialize it:

1. Go to the "learning-compass-api" service in Render
2. Click on the "Shell" tab
3. Run the following commands:
   ```
   python manage.py migrate
   python manage.py createsuperuser
   ```
4. Follow the prompts to create an admin user

### 6. Verify Deployment

1. Access the frontend application at the URL provided by Render
2. Log in with the admin credentials you created
3. Verify that all features are working correctly

## Troubleshooting

If you encounter any issues during deployment:

1. Check the logs in the Render dashboard
2. Ensure all environment variables are set correctly
3. Verify that the database migrations have been applied
4. Check that the frontend is correctly configured to connect to the backend API

For more information, refer to the Render documentation: https://render.com/docs
EOL

echo "Deployment configuration complete!"
