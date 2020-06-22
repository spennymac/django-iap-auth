=====
Usage
=====

To use Django IAP Auth in a project, add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_iap_auth.apps.DjangoIapAuthConfig',
        ...
    )

Add Django IAP Auth's URL patterns:

.. code-block:: python

    from django_iap_auth import urls as django_iap_auth_urls


    urlpatterns = [
        ...
        url(r'^', include(django_iap_auth_urls)),
        ...
    ]
