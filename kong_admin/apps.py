# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from django.apps import AppConfig
from .receivers import *

class KongAdminConfig(AppConfig):
    name = 'kong_admin'
    verbose_name = 'Kong'
