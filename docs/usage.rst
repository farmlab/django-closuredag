=====
Usage
=====

To use django-closuredag in a project, add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_closuredag.apps.DjangoClosuredagConfig',
        ...
    )

Add django-closuredag's URL patterns:

.. code-block:: python

    from django_closuredag import urls as django_closuredag_urls


    urlpatterns = [
        ...
        url(r'^', include(django_closuredag_urls)),
        ...
    ]
