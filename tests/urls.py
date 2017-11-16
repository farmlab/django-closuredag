# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.conf.urls import url, include

from django_closuredag.urls import urlpatterns as django_closuredag_urls

urlpatterns = [
    url(r'^', include(django_closuredag_urls, namespace='django_closuredag')),
]
