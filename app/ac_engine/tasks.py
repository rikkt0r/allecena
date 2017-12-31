# coding: utf-8

import json
import importlib
from celery import Task
from time import time

from ac_common.loggers import stat_logger, exception_logger
from ac_common.models import User, Category, TaskScheduler
from ac_common.exceptions import AllecenaException
from ac_common.utils import send_mail
from ac_engine.models import Results, Triggers, TriggerValues


class ComputingTask(Task):
    FEATURES = ('hint', 'prediction', 'statistics', 'histogram', 'trends')
    SOURCES = ('allegro', 'ebay')

    def get_model(self, source, feature, input_data, processing_data):
        if source in self.SOURCES and feature in self.FEATURES and processing_data is not None:
            try:
                model = importlib.import_module('ac_engine_%s.actions.%s' % (source.lower(), feature.lower()))
                return getattr(model, feature.title())(input_data, processing_data)
            except ImportError as e:
                exception_logger.exception(e)

        exc = AllecenaException('Feature %s is not supported for data source %s.' % (feature, source))
        exception_logger.log(exc)
        raise exc

    def run(self, input_data=None, user_id=None):

        time_start = time()

        user = User.objects.get(pk=user_id)
        advanced = input_data['data']['analysis']['advanced']

        if 'account' in input_data['data']:
            for s in self.SOURCES:
                user_name = getattr(user, '%s_user_name' % s)
                if s not in input_data['data'] and user_name:
                    input_data['data']['account'][s] = user_name
        else:
            input_data['data']['account'] = {}
            for s in self.SOURCES:
                user_name = getattr(user, '%s_user_name' % s)
                if user_name:
                    input_data['data']['account'][s] = user_name

        try:
            results = {}

            for source in input_data['sources']:

                mod_loader = importlib.import_module('ac_engine_%s.data.data_loader' % source.lower())
                processing_data = getattr(mod_loader, 'DataLoader').get_data(input_data['data'])

                for action in input_data['actions']:
                    result = self.get_model(source.lower(), action.lower(), input_data['data'], processing_data)
                    result.execute()
                    results[result.get_api_name] = result.serialize

            stat_logger.info('Result %s: %s' % (input_data['actions'], results))
            stat_logger.info('Computation time: %fs' % round(time() - time_start, 2))

            result = Results()

            result.user = user
            result.category = Category.objects.get(pk=input_data['data']['item']['category_id'])

            result.name = input_data['data']['item']['name']
            result.provider = 2 if len(input_data['sources']) == 2 else 2 if 'allegro' in input_data['sources'] else 1
            result.advanced = advanced
            result.statistics = 'statistics' in input_data['actions']
            result.hint = 'hint' in input_data['actions']
            result.prediction = 'prediction' in input_data['actions']
            result.histogram = 'histogram' in input_data['actions']
            result.trends = 'trends' in input_data['actions']
            result.json_dump = json.dumps(results)
            result.error = False
            result.computing_hash = self.request.id

            result.save()

        except Exception as e:
            exception_logger.exception(e)
            self.retry(countdown=2, exc=e, max_retries=3)

    # error handling
    def after_return(self, status, retval, task_id, args, kwargs, einfo):

        if issubclass(retval.__class__, BaseException):
            exception_logger.exception(retval)

            input_data = kwargs.get('input_data')

            user = User.objects.get(pk=kwargs.get('user_id'))
            advanced = input_data['data']['analysis']['advanced']

            result = Results()

            result.user = user
            result.category = Category.objects.get(pk=input_data['data']['item']['category_id'])
            result.name = input_data['data']['item']['name']
            result.provider = 2 if len(input_data['sources']) == 2 else 2 if 'allegro' in input_data['sources'] else 1
            result.advanced = advanced
            result.json_dump = '{}'
            result.error = True
            result.computing_hash = self.request.id

            result.save(force_insert=True)


class TriggerTask(Task):

    def get_model(self, provider):
        try:
            model = importlib.import_module('ac_engine_%s.data.data_grabber' % provider)
            return getattr(model, 'DataGrabber')(advanced_mode=True)
        except ImportError as e:
            exception_logger.exception(e)
            raise e

    def stop_periodic_task(self, trigger, success=True):
        TaskScheduler.terminate_by_task_name(trigger.task_name)

        trigger.finished = True
        trigger.error = not success
        trigger.save(force_update=True)

    def notify_user(self, trigger, success=True):
        context = {
            'user_id': trigger.user.id,
            'success': success,
            'trigger_name': trigger.name,
        }
        send_mail("AlleCena auction tracking finished", 'email_auction_tracking_finished.html', trigger.user.email, context)

    def run(self, trigger_id=None):

        try:
            trigger = Triggers.objects.get(pk=trigger_id)
            grabber = self.get_model(trigger.get_provider_display())

            auction = grabber.get_offer_by_id(trigger.auction_id)[0]
            if not trigger.name:
                trigger.name = str(auction.name.encode('utf8'))
                trigger.save()

            if trigger.mode == trigger.MODE_PRICE:
                value = auction.priceHighestBid
            elif trigger.mode == trigger.MODE_QUANTITY:
                value = auction.amountLeft
            elif trigger.mode == trigger.MODE_VIEWS:
                value = auction.views
            else:
                raise AllecenaException("Sorry mate, no such trigger option")

            if value >= trigger.mode_value:
                self.stop_periodic_task(trigger)
                self.notify_user(trigger, True)

            if auction.endingDate <= int(time()) and not auction.offerInfinite:
                self.stop_periodic_task(trigger)
                self.notify_user(trigger, False)

            TriggerValues.objects.create(trigger=trigger, value=value)

        except Exception as e:
            exception_logger.exception(e)
            self.retry(countdown=1, exc=e, max_retries=3)


class TestPeriodicTask(Task):

    def run(self):
        exception_logger.error("TESTING PERIODIC TASK")
