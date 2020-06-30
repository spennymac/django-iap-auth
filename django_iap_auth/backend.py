import logging
from functools import cached_property
from typing import Optional, Mapping

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from google.auth import jwt

UserModel = get_user_model()


class IAPSettings:
    prefix = 'AUTH_IAP_'

    defaults = {
        'PROJECT_ID': '',
        'PROJECT_NUMERIC_ID': '',
        'AUDIENCE_FORMAT': '/projects/{}/apps/{}',
        'PUBLIC_KEY_ENDPOINT': 'https://www.gstatic.com/iap/verify/public_key',
        'HEADER_KEY': 'HTTP_X_GOOG_IAP_JWT_ASSERTION',
        'EMAIL_CLAIM_KEY': 'email',
        'SUBJECT_CLAIM_KEY': 'sub',
        'TIMEOUT': 5,
        'USER_ATTRS': {
            'USERNAME_FIELD_FROM_CLAIM': 'email',
            'EMAIL_FIELD_FROM_CLAIM': 'email',
        },
        'USERS_IS_STAFF': [],
        'USERS_IS_SUPERUSER': [],
    }

    def __init__(self):
        for name, default in self.defaults.items():
            value = getattr(settings, f'{self.prefix}{name}', default)
            setattr(self, name, value)


class IAPBackend(BaseBackend):
    CERTS = None

    @cached_property
    def settings(self):
        return IAPSettings()

    @cached_property
    def keys(self):
        response = requests.get(self.settings.PUBLIC_KEY_ENDPOINT, timeout=self.settings.TIMEOUT)
        if response.status_code != 200:
            raise Exception(f'unable to fetch IAP keys: {response.status_code} / {response.headers} / {response.text}')
        return response.json()

    @cached_property
    def audience(self):
        return self.settings.AUDIENCE_FORMAT.format(
            self.settings.PROJECT_NUMERIC_ID,
            self.settings.PROJECT_ID,
        )

    def _validate(self, iap_jwt) -> Optional[Mapping[str, str]]:
        key = self._get_public_key(iap_jwt)
        try:
            return jwt.decode(iap_jwt, certs=key, audience=self.audience)
        except Exception:
            logging.exception('failed to validate jwt')
            return None

    def authenticate(self, request, **kwargs):
        iap_jwt = request.META.get(self.settings.HEADER_KEY, None)
        if iap_jwt is None:
            logging.info('failed to retrieve iap jwt from request')
            return None

        validated = self._validate(iap_jwt)
        if not validated:
            return None

        username = validated.get(self.settings.USER_ATTRS['USERNAME_FIELD_FROM_CLAIM'], None)
        email = validated.get(self.settings.USER_ATTRS['EMAIL_FIELD_FROM_CLAIM'], None)
        if email is None or username is None:
            logging.info('failed to retrieve email or username from iap jwt')
            return None

        user, created = UserModel._default_manager.get_or_create(**{
            UserModel.USERNAME_FIELD: username,
            UserModel.EMAIL_FIELD: email,
        })

        is_staff = True if username in self.settings.USERS_IS_STAFF else False
        is_superuser = True if username in self.settings.USERS_IS_SUPERUSER else False

        save_needed = False
        if user.is_staff is False and is_staff is True:
            user.is_staff = is_staff
            save_needed = True

        if user.is_superuser is False and is_superuser is True:
            user.is_superuser = is_superuser
            save_needed = True

        if save_needed:
            user.save()

        return user

    def _get_public_key(self, iap_jwt: str) -> Optional[str]:
        key_id = jwt.decode_header(iap_jwt).get('kid')
        if not key_id:
            return None

        try:
            if key_id not in self.keys:
                # invalidate cache
                del self.keys

                # refetch
                if key_id not in self.keys:
                    logging.error(f'public key {key_id} not found')
                    return None

            return self.keys[key_id]
        except Exception:
            logging.exception(f'failed to retrieve public keys')
            return None

    def get_user(self, user_id):
        try:
            user = UserModel._default_manager.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
        return user
