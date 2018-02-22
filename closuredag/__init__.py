__version__ = '0.1.0'

from django.conf import settings


CLOSUREDAG_CONFIG = getattr(settings, 'CLOSUREDAG_CONFIG', {})

app_settings = dict({
    'CLOSURE': True,
}, **CLOSUREDAG_CONFIG)
