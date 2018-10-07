"""
Django settings for BioPy project.

Generated by 'django-admin startproject' using Django 2.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
from YamJam import yamjam


#Setting base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#Safely getting secure keys and other information
config = yamjam(os.path.join(BASE_DIR,'config.yaml'))['biopy']

SECRET_KEY = config['secret_key']

DEBUG = True

ALLOWED_HOSTS = []


ROOT_URLCONF = 'BioPy.urls'


# Redirects
LOGIN_REDIRECT_URL = '/home'
LOGOUT_REDIRECT_URL = '/goodbye'

# Allauth configuration

# Ensure SITE_ID is set sites app 
SITE_ID = 1

# Add the 'allauth' backend to AUTHENTICATION_BACKEND and keep default ModelBackend
AUTHENTICATION_BACKENDS = [ 'django.contrib.auth.backends.ModelBackend',
                           'allauth.account.auth_backends.AuthenticationBackend'] 
# EMAIL_BACKEND so allauth can proceed to send confirmation emails
# ONLY for development/testing use console 
EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend'

# Custom allauth settings
ACCOUNT_EMAIL_SUBJECT_PREFIX = "[BioPy]"
ACCOUNT_AUTHENTICATION_METHOD="username_email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory' 
ACCOUNT_LOGOUT_REDIRECT_URL = "/goodbye"
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
ACCOUNT_USERNAME_VALIDATORS = 'BioPyApp.validators.allauth.UsernameValidators'



#crispy

CRISPY_TEMPLATE_PACK = 'bootstrap4'

# others

INSTALLED_APPS = [
    'BioPyApp',

    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'django.contrib.auth',    
    'django.contrib.sites',
    'django.contrib.admin',

    'crispy_forms', 
    'rest_framework',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.github',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.openid',
    #'sorl.thumbnail', add this when they fix the bug in github
    #'newsletter',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'BioPy.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

db = config['database']
DATABASES = {
    'default': {
        'ENGINE': db['engine'],
        'NAME': db['name'],
        'USER': db['user'],
        'PASSWORD': db['password'],
        'HOST': db['host'],
        'PORT': db['port']

    }
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS=[os.path.join(BASE_DIR,'BioPy','static')]