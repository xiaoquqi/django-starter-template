"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 5.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import dj_database_url
import logging.config
import os
from pathlib import Path

from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv

from .constants import *
from .logging_config import configure_logging

# ============================
# General Settings
# ============================

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load env from parent path
ENV_DIR = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_DIR)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    'django-insecure-$k0f0!qp@0k%1xa_)zy!+xvwpv)+&$q&!d69ma@l615bdc2ytd')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DJANGO_DEBUG", True)

ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', 'http://localhost').split(",")

# ============================
# Logging Configuration
# ============================

LOG_LEVEL = os.getenv('DJANGO_LOG_LEVEL', 'info').upper()
configure_logging(LOG_LEVEL)

# ============================
# Application Definitions
# ============================

# Django & thrid party apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Required by django-allauth for managing site-specific data,
    # such as site domains and configurations.
    'django.contrib.sites',

    # Core Django Rest Framework (DRF) package that provides tools
    # to build APIs and handle request/response data in various formats (JSON, XML, etc.).
    'rest_framework',

    # Enables token-based authentication in DRF, allowing users
    # to authenticate using tokens.
    'rest_framework.authtoken',

    # A Django app that integrates dj-rest-auth with Django-allauth,
    # providing authentication and registration endpoints for RESTful APIs.
    'dj_rest_auth',

    # Provides JWT authentication support for Django REST Framework,
    # allowing for secure token-based authentication using JSON Web Tokens.
    'rest_framework_simplejwt',

    # Django-allauth package, which provides comprehensive user authentication,
    # registration, and account management.
    'allauth',

    # A submodule of django-allauth that handles user account registration,
    # login, password management, and more.
    'allauth.account',

    # Extends allauth to support social authentication
    # (e.g., logging in with Facebook, Google, etc.).
    'allauth.socialaccount',

    # Adds user registration endpoints to dj-rest-auth, enabling JWT-based
    # user registration and management (e.g., email verification, password reset).
    'dj_rest_auth.registration',

    # Provides tools for generating interactive API documentation with Swagger UI
    # or ReDoc, making it easier to visualize and test API endpoints.
    'drf_yasg',

    # A Django app that provides support for periodic task scheduling
    # using Celery. It allows you to manage and schedule tasks in a
    # database-backed way, making it easier to handle recurring tasks.
    'django_celery_beat',

    # A Django app that stores the results of Celery tasks in the database,
    # allowing for easy retrieval and management of task outcomes.
    'django_celery_results',
]

# Project-Specific Apps
INSTALLED_APPS += [
    'accounts',
    'v1.sample',
]

# The ID of the site that this Django project is associated with.
# This is required for django.contrib.sites and django-allauth to work correctly.
SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Middleware for django-allauth that manages account-related operations,
    # such as handling user sessions and account state.
    "allauth.account.middleware.AccountMiddleware",

    # 'django.middleware.locale.LocaleMiddleware' is Django's localization middleware.
    # It sets the language environment based on the user's language preferences.
    # The middleware checks headers (e.g., Accept-Language) or session settings.
    'django.middleware.locale.LocaleMiddleware',
]

ROOT_URLCONF = 'core.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# ============================
# Database Configuration
# ============================

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3')
DATABASES = {
    'default': dj_database_url.config(default=DATABASE_URL)
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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

# ============================
# Internationalization Configuration
# https://docs.djangoproject.com/en/5.1/topics/i18n/
# ============================

# LANGUAGE_CODE: Specifies the default language code for the application.
# This determines the language strings used by Django. For example, setting
# it to 'en-us' will make Django use American English translations. To
# support other languages, change it to the appropriate language code,
# such as 'zh-hans' for Simplified Chinese.
LANGUAGE_CODE = 'en'

# LANGUAGES: Defines a list of supported languages for the project. It is
# structured as tuples, where the first element is the language code (e.g.,
# 'en-us' for American English, 'de' for German), and the second is the
# language's display name. The display names are usually wrapped in the
# gettext translation function _() for internationalization support. These
# languages appear in Django's language switcher for multi-language support.
# Example: ('zh-hans', _('Simplified Chinese')) adds support for Simplified Chinese.
LANGUAGES = (
    ('zh-hans', '简体中文'),
    ('en', 'English'),
)

# TIME_ZONE: Sets the default time zone, which controls how dates and times
# are displayed and stored. For example, setting it to 'UTC' will make Django
# use Coordinated Universal Time. Change it to the appropriate time zone,
# such as 'Asia/Shanghai', for users in a specific region.
TIME_ZONE = 'UTC'

# USE_I18N: Enables internationalization support. When set to True, Django
# loads translation files and handles language-specific functionalities. Set
# this to False if the application does not require multi-language support.
USE_I18N = True

# USE_L10N: Enables localization support. When set to True, Django adjusts
# the format of dates, times, and numbers based on the language code and
# time zone. For example, date formats may change from 'YYYY-MM-DD' to
# 'DD/MM/YYYY' depending on the language and region.
USE_L10N = True

# USE_TZ: Enables time zone support. When set to True, Django stores dates
# and times in a timezone-aware format. Time is stored in UTC in the database
# and converted to the user's local time zone when displayed. Set to False
# if the application does not require time zone handling.
USE_TZ = True

# LOCALE_PATHS: Specifies the paths for translation files. This global setting
# combines the 'locale' directory with the project's root directory (BASE_DIR),
# so all translation files are stored in the 'locale' folder at the project
# root.
#
# You can also set translation file paths for individual apps. Each app can
# have its own 'locale' directory for storing translation files. For example,
# the translations for the 'cloud_platform' app can be stored in:
# 'yourapp/locale/zh_hans/LC_MESSAGES'.
LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),  # Locale folder at the project root
]

# ============================
# Static and Media Files
# https://docs.djangoproject.com/en/5.1/howto/static-files/
# ============================

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================
# External Libraries Configuration
# ============================
from .celery import *
from .rest import *
from .swagger import *