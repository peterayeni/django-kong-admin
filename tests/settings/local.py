# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from .base import *

DATABASES = {
    # https://github.com/joke2k/django-environ
    #  Raises ImproperlyConfigured exception if DATABASE_URL not in os.environ, and no default
    #  was given.
    'default': env.db(default='sqlite:///%s' % os.path.join((BASE_DIR - 2).root, 'db.sqlite3'))
}

KONG_ADMIN_URL = env('KONG_ADMIN_URL', default='http://localhost:8001')
KONG_ADMIN_SIMULATOR = env('KONG_ADMIN_SIMULATOR', default=False)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': env('DJANGO_LOG_LEVEL', default='INFO'),
            'propagate': True,
        },
        'kong_admin': {
            'handlers': ['console'],
            'level': env('DJANGO_LOG_LEVEL', default='INFO'),
        },
    },
}
