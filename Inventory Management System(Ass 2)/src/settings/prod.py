from .base import *
from src import vault
from src.vault import credentials
DEBUG = False

# Override SECRET_KEY for production (use from environment variable)
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', credentials.get('prod', {}).get('SECRET_KEY', SECRET_KEY))

# SECURITY: Set proper allowed hosts - NEVER use ["*"] in production
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',') if os.environ.get('DJANGO_ALLOWED_HOSTS') else []

CORS_ORIGIN_ALLOW_ALL = False

CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', 'http://localhost:5173,http://localhost:3000').split(',')


DATABASES = {
    "default": {
        "ENGINE": credentials['prod']['DB_ENGINE'],
        "NAME": credentials['prod']['DB_NAME'],
        "USER": credentials['prod']['DB_USER'],
        "PASSWORD": credentials['prod']['DB_PASSWORD'],
        "HOST": credentials['prod']['DB_HOST'],  # set in docker-compose.yml
        "PORT": credentials['prod']['DB_PORT'],  # default postgres port
    },
}

EMAIL = credentials['prod']["EMAIL"]
PASSWORD = credentials['prod']["PASSWORD"]

# AWS credentials

# PROD SECRET KEYS
S3_BUCKET = credentials['prod']['S3_BUCKET']
AWS_ACCESS_KEY_ID = credentials['prod']['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = credentials['prod']['AWS_SECRET_ACCESS_KEY']
REGION = credentials['prod']['REGION']
AWS_URL = "https://%s.s3.%s.amazonaws.com" % (S3_BUCKET, REGION)

# Frontend Urls
FRONTEND_BASE_URL = credentials['prod']['FRONTEND_BASE_URL']
ADMIN_FRONTEND_BASE_URL = credentials['prod']['ADMIN_FRONTEND_BASE_URL']

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Production security settings
if not DEBUG:
    # HSTS (HTTP Strict Transport Security)
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # SSL/HTTPS
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # Additional security headers
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    
    # Remove debug tools from production
    if 'debug_toolbar' in INSTALLED_APPS:
        INSTALLED_APPS.remove('debug_toolbar')
    if "atomicloops.middleware.QueryCountMiddleware" in MIDDLEWARE:
        MIDDLEWARE.remove("atomicloops.middleware.QueryCountMiddleware")
    if "debug_toolbar.middleware.DebugToolbarMiddleware" in MIDDLEWARE:
        MIDDLEWARE.remove("debug_toolbar.middleware.DebugToolbarMiddleware")
