# coding: utf-8

import hmac
import hashlib
from functools import wraps
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from ac_common.exceptions import AllecenaException, AllegroException
from ac_common.loggers import exception_logger, api_logger


def reverse_key_val_choice_from_tuple(tpl, choice):
    return {v: k for k, v in tpl}[choice]


def create_token(email):
    date = timezone.now() + timedelta(days=1)
    token_data = '|'.join([str(date), email, settings.AUTH_KEY_ADDITION])
    token_data += '|%s' % hashlib.md5(token_data).hexdigest()
    token = hmac.new(settings.SECRET_KEY, token_data, hashlib.sha256).hexdigest()
    return date, token


def median(input_list):
    from numpy import median
    return float(median(input_list))


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i+n]


def send_mail(subject, email_template, email_to, context, html_email_template=None):
    from ac_common.tasks import MailTask
    MailTask().delay(subject=subject, email_to=email_to, email_template=email_template, context=context,
                   html_email_template=html_email_template)


def grabber_exception_fallback(f):

    @wraps(f)
    def inner(*args, **kwargs):
        from suds import WebFault
        try:
            return f(*args, **kwargs)
        except WebFault as e:
            ex = AllegroException("Allegro is dying.. @ %s, args: %s, kwargs: %s" % (f.__name__, str(args), str(kwargs)))
            exception_logger.exception(ex)
            exception_logger.exception(e)
        except Exception as e:
            ex = AllecenaException("Error executing %s, args: %s, kwargs: %s" % (f.__name__, str(args), str(kwargs)))
            exception_logger.exception(ex)
            exception_logger.exception(e)
            raise ex
    return inner


def maintain_api_session(f):
    def wrapper(self, *args, **kwargs):
        if not getattr(self, 'token', None):
            self.set_user_token()
            return f(self, *args, **kwargs)
        else:
            from suds import WebFault
            try:
                return f(self, *args, **kwargs)
            except WebFault as e:
                if e.fault.faultcode in self.FAULTS['session_expired']:
                    api_logger.warning('API session expired, pinging API for new')
                    self.set_user_token()
                    return f(self, *args, **kwargs)
                else:
                    exception_logger.exception(e)

    return wrapper
