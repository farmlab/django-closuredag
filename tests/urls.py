# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.conf.urls import url, include

from closuredag.urls import urlpatterns as closuredag_urls

urlpatterns = [
    url(r'^', include(closuredag_urls, namespace='closuredag')),
]
