# coding: utf-8

from celery import Task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import loader

from ac_common.loggers import exception_logger
from ac_common.models import User


class MailTask(Task):

    def run(self, subject=None, email_to=None, email_template=None, context=None,html_email_template=None):
        try:

            if 'user_id' in context:
                context['user'] = User.objects.get(pk=context['user_id'])

            body = loader.render_to_string(email_template, context)

            email_message = EmailMultiAlternatives(subject, body, settings.ALLECENA_EMAIL, [email_to])
            if html_email_template is not None:
                html_email = loader.render_to_string(html_email_template, context)
                email_message.attach_alternative(html_email, 'text/html')

            email_message.send()

        except Exception as e:
            exception_logger.exception(e)
            self.retry(countdown=1, exc=e, max_retries=3)
