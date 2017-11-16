=============================
django-closuredag
=============================

.. image:: https://badge.fury.io/py/django-closuredag.svg
    :target: https://badge.fury.io/py/django-closuredag

.. image:: https://travis-ci.org/farmlab/django-closuredag.svg?branch=master
    :target: https://travis-ci.org/farmlab/django-closuredag

.. image:: https://codecov.io/gh/farmlab/django-closuredag/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/farmlab/django-closuredag

A django model to represent direct acyclic graph coupled with closure table

Documentation
-------------

The full documentation is at https://django-closuredag.readthedocs.io.

Quickstart
----------

Install django-closuredag::

    pip install django-closuredag

Add it to your `INSTALLED_APPS`:

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

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
