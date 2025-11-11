# How to add 2FA for django admin panel

1. Update requirements.txt
```
    ...


    django-otp 
    qrcode

    ...
```


2. Update settings/base.py

```
INSTALLED_APPS = [
   
    ...


    'django_otp',
    'django_otp.plugins.otp_totp',
    'django_otp.plugins.otp_static',

    ...


]

MIDDLEWARE = [
    ...
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]
```


3. Do Database migration

```
python manage.py migrate
```

4. Now go to django admin panel and create TOPT and click on the qrcode and it to the autheticator app

5. For production in src/urls.py uncomment or add the following lines

```
from django_otp.admin import OTPAdminSite

admin.site.__class__ = OTPAdminSite
```
