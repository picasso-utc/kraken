import os
from core import settings_confidential as confidentials

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def make_path(rel):
	return os.path.join(BASE_DIR, rel.replace('/', os.path.sep))


# --------------------------------------------------------------------------
# 		Database
# --------------------------------------------------------------------------
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = confidentials.DATABASES

# --------------------------------------------------------------------------
# 		Django REST Configuration
# --------------------------------------------------------------------------

REST_FRAMEWORK = {
	# 'DEFAULT_AUTHENTICATION_CLASSES': (
	# 	'core.auth.AdminSiteBackend',
	# 	'rest_framework.authentication.SessionAuthentication',
	# ),
	'EXCEPTION_HANDLER': 'core.exception_handler.custom_exception_handler'
}


# --------------------------------------------------------------------------
# 		Django Main Configuration
# --------------------------------------------------------------------------

INSTALLED_APPS = [
	# Django Core
	'constance',
    'constance.backends.database',
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	# API
	'corsheaders',
	'rest_framework',
	# Applications
	'core',
	'perm',
	'treso',
	'payutc',
]

# AUTH_USER_MODEL = 'core.User'
ROOT_URLCONF = 'core.urls'
WSGI_APPLICATION = 'core.wsgi.application'
STATIC_URL = '/static/'

MIDDLEWARE = [
	'corsheaders.middleware.CorsMiddleware', # preventing CORS rules errors
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# AUTHENTICATION_BACKENDS = (
# 	'core.auth.AdminSiteBackend',
# )

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



# --------------------------------------------------------------------------
# 		Confidentials & Keys
# --------------------------------------------------------------------------

DEBUG = confidentials.DEBUG

ALLOWED_HOSTS = confidentials.ALLOWED_HOSTS
CORS_ORIGIN_ALLOW_All = True
CORS_ORIGIN_WHITELIST = confidentials.CORS_ORIGIN_WHITELIST
CORS_ALLOW_CREDENTIALS = True
CSRF_COOKIE_HTTPONLY = False # False to enable the use of cookies in ajax requests
CSRF_USE_SESSIONS = False  # Useful ??
CORS_ALLOW_HEADERS = ('content-disposition', 'accept-encoding',
                      'content-type', 'accept', 'origin', 'withcredentials')

SECRET_KEY = confidentials.SECRET_KEY
PAYUTC_APP_KEY = confidentials.PAYUTC_APP_KEY
PAYUTC_APP_URL = confidentials.PAYUTC_APP_URL
PAYUTC_FUN_ID = confidentials.PAYUTC_FUN_ID
PAYUTC_SYSTEM_ID = confidentials.PAYUTC_SYSTEM_ID
PAYUTC_ARTICLES_CATEGORY = confidentials.PAYUTC_ARTICLES_CATEGORY
CURRENT_SEMESTER = "19"


GINGER_URL = confidentials.GINGER_URL
GINGER_KEY = confidentials.GINGER_KEY

# CONSTANCE_CONFIG = {
# 	'SEMESTER': (0, 'Semestre actuel', int),
# 	'TEST' : ('Test', 'Test', str)
# }

# CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

CONSTANCE_CONFIG = {
    'GINGER_URL': (confidentials.GINGER_URL, 'Adresse de connexion à Ginger.', str),
    'GINGER_KEY': (confidentials.GINGER_KEY, 'Clé de connexion à Ginger', str),
    'PAYUTC_CONNECTION_UID': (confidentials.PAYUTC_CONNECTION_UID, 'UID de l\'utilisateur dont les droits sont utilisés'
                                           'pour la connexion à PayUTC. Doit avoir les droits'
                                           'GESARTICLE et TRESO.', str),
    'PAYUTC_CONNECTION_PIN': (confidentials.PAYUTC_CONNECTION_PIN, 'PIN de l\'utilisateur dont les droits sont utilisés'
                                     'pour la connexion à PayUTC.', int),
    'PAYUTC_APP_KEY': (confidentials.PAYUTC_APP_KEY, 'Clé d\'application permettant de se connecter à PayUTC.', str),
    'PAYUTC_APP_URL': (confidentials.PAYUTC_APP_URL, 'Adresse permettant de se connecter à PayUTC.', str),
    'SEMESTER': (0, 'Semestre actuel', int),
}

CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'


# --------------------------------------------------------------------------
# 		Internationalization
# --------------------------------------------------------------------------
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
