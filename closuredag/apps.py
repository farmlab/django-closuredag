# -*- coding: utf-8
from django.apps import AppConfig


class ClosuredagConfig(AppConfig):
    name = 'closuredag'

    def ready(self):
        import closuredag.signals
