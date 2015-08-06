# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import factory

from kong_admin.models import APIReference


class APIReferenceFactory(factory.DjangoModelFactory):
    class Meta:
        model = APIReference

    target_url = factory.Sequence(lambda n: ("http://mockbin%d.com" % n).encode('utf-8'))
