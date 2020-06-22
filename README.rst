=============================
Django IAP Auth
=============================

.. image:: https://badge.fury.io/py/django-iap-auth.svg
    :target: https://badge.fury.io/py/django-iap-auth


Django authentication backend for Google's Identity Aware Proxy (IAP)

Documentation
-------------

The full documentation is at https://django-iap-auth.readthedocs.io.

Quickstart
----------

Install Django IAP Auth::

    pip install django-iap-auth

To use the auth backend, add ``'django_iap_auth.backend.IAPBackend'`` to AUTHENTICATION_BACKENDS.

.. code-block:: python

    AUTHENTICATION_BACKENDS = [
        'django_iap_auth.backend.IAPBackend',
    ]

To use the iap auto login middleware, add ``'django_iap_auth.middleware.IapUserLoginMiddleware'`` to MIDDLEWARE.

.. code-block:: python

    MIDDLEWARE = [
        ...
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django_iap_auth.middleware.IapUserLoginMiddleware',
        ...
    ]


Features
--------

* TODO


Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
