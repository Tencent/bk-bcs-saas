# -*- coding: utf-8 -*-
from .dev import *

DATABASES['default'] = {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': 'bcs-app',
    'USER': 'root',
    'PASSWORD': os.environ.get('DB_PASSWORD', '654321'),
    'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
    'PORT': '3306',

    'OPTIONS': {
        'init_command': 'SET default_storage_engine=INNODB',
    }
}
