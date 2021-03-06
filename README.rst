=============================
django-closuredag
=============================

.. image:: https://img.shields.io/pypi/v/django-closuredag.svg
        :target: https://pypi.python.org/pypi/django-closuredag

.. image:: https://travis-ci.org/farmlab/django-closuredag.svg?branch=master
        :target: https://travis-ci.org/farmlab/django-closuredag

.. image:: https://readthedocs.org/projects/django-closuredag/badge/?version=latest
        :target: https://django-closuredag.readthedocs.io/en/latest
        :alt: Documentation Status

.. image:: https://codecov.io/gh/farmlab/django-closuredag/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/farmlab/django-closuredag


A django model to represent direct acyclic graph coupled with closure table

Documentation
-------------

The full documentation is at https://django-closuredag.readthedocs.io.

The objective is to develop a reusable django app to represent direct acyclic graph coupled with closure table (see: closure_DAG_concept_ ). It should combine feature provided by django-DAG and django-closuretree.


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

.. _closure_DAG_concept: https://www.codeproject.com/Articles/22824/A-Model-to-Represent-Directed-Acyclic-Graphs-DAG-o 
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
