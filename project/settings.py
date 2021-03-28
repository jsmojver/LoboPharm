# -*- coding: utf-8 -*-

import os
import settings_local

local = settings_local

DEBUG = not local.Deploy
TEMPLATE_DEBUG = DEBUG
DEBUG_TOOLBAR = local.DebugToolbar

ADMINS = local.Admins
MANAGERS = ADMINS

DATABASES = local.DATABASES
DATABASE_ROUTERS = local.DATABASE_ROUTERS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Zagreb'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'hr'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
#USE_L10N = False
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = local.DataRoot

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/static/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
# Put strings here, like "/home/html/static" or "C:/www/django/static".
# Always use forward slashes, even on Windows.
# Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'r_)ff9g%dgx7)u7^itvcj((3_bmas#nka_t994b%0&8t8y-$o@'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    #    'sqldebug.SQLLogMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'requirelogin.RequireLoginMiddleware',
    'project.main.middleware.pagination.PaginationMiddleware',
)

ROOT_URLCONF = 'project.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(local.ProjectPath, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    #'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'coffin',
    'main',
    'handler',
    'depo',
    'meds',
    'order',
    'sysapp',
    'fiskalizacija',
    'eskulap',
    'nabava',
    #    'blagajna',
    #    'debug_toolbar',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
        'level': 'ERROR',
        'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
        'handlers': ['mail_admins'],
        'level': 'ERROR',
        'propagate': True,
        },
    }
}

if hasattr(local, 'LOGGING'):
    LOGGING = local.LOGGING

INTERNAL_IPS = ('127.0.0.1',)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
)


LOGIN_URL = '/accounts/login/'

LOGIN_EXEMPT_URLS = (
    r'^accounts/login/',
    r'^temperatura',
    r'^sysapp/snapshot/submit',
    r'^sysapp/supervisor',
)

if not local.Deploy:
    LOGIN_EXEMPT_URLS += (r'^static',)

USLUGA_POSREDOVANJA = '15.00'
OIB_OBVEZNIKA = '52740408813'
POSLOVNI_PROSTOR = '1'
NACIN_PLACANJA = 'G'
STOPA_PDV = '25.00'
POCETNI_BROJ_RACUNA = 1

EMAIL_HOST = local.EMAIL_HOST
EMAIL_HOST_USER = local.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = local.EMAIL_HOST_PASSWORD
EMAIL_PORT = local.EMAIL_PORT
EMAIL_USE_TLS = local.EMAIL_USE_TLS
DEFAULT_FROM_EMAIL = local.DEFAULT_FROM_EMAIL
SERVER_EMAIL = local.SERVER_EMAIL

BankAccountNumber = "HR9525030071100084230"
TaxRate = 25.0
ApoKzTaxRate = 5.0

VIRMAN_PDF = getattr(local, 'VIRMAN_PDF', False)

PAGINATION_DEFAULT_PAGINATION = 50

#*************************************************************
# Jinja2

JINJA2_TEMPLATE_DIRS = TEMPLATE_DIRS

JINJA2_ENVIRONMENT_OPTIONS = {
    #"line_statement_prefix": "#",
    "trim_blocks": True,
    "auto_reload": not local.Deploy,
}

JINJA2_FILTERS = (
)

JINJA2_TESTS = {}
JINJA2_GLOBALS = {}

JINJA2_EXTENSIONS = (
    'project.main.middleware.pagination.AutopaginateExtension',
)

