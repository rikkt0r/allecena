# coding: utf-8

import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone

from ac_common.models import User, Category


class Results(models.Model):
    MODES = ('hint', 'prediction', 'statistics', 'histogram', 'trends')

    user = models.ForeignKey(User, related_name='results', related_query_name='result')
    category = models.ForeignKey(Category, related_name='+')  # + --> do not create reverse reference from categories

    name = models.CharField(max_length=120)
    computing_hash = models.CharField(max_length=100)
    provider = models.PositiveSmallIntegerField(choices=settings.PROVIDERS)
    advanced = models.BooleanField(default=False)
    statistics = models.BooleanField(default=False)
    hint = models.BooleanField(default=False)
    prediction = models.BooleanField(default=False)
    histogram = models.BooleanField(default=False)
    trends = models.BooleanField(default=False)
    json_dump = models.TextField(max_length=1500)
    error = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)


class Triggers(models.Model):

    MODE_PRICE = 0
    MODE_QUANTITY = 1
    MODE_VIEWS = 2

    MODES = (
        (MODE_PRICE, 'price'),
        (MODE_QUANTITY, 'quantity'),
        (MODE_VIEWS, 'views'),
    )

    TIME_LAZY = 0
    TIME_MODERATE = 1
    TIME_TURBO = 2
    TIME_TURBO_ULTRA = 3

    TIMES = (
        (TIME_LAZY, 'lazy'),
        (TIME_MODERATE, 'moderate'),
        (TIME_TURBO, 'turbo'),
        (TIME_TURBO_ULTRA, 'ultra_turbo'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='triggers', related_query_name='trigger')
    name = models.CharField(max_length=120, null=True, blank=True)
    task_name = models.CharField(max_length=120, null=True, blank=True)
    mode = models.PositiveSmallIntegerField(choices=MODES)
    time = models.PositiveSmallIntegerField(choices=TIMES)
    mode_value = models.PositiveSmallIntegerField()
    provider = models.IntegerField(choices=settings.PROVIDERS)
    auction_id = models.IntegerField()
    finished = models.BooleanField(default=False)
    error = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_finished = models.DateTimeField(auto_now=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.task_name = self.get_task_name()
        super(Triggers, self).save(*args, **kwargs)

    @property
    def task_interval(self):
        return {
            self.TIME_LAZY: 60,
            self.TIME_MODERATE: 15,
            self.TIME_TURBO: 5,
            self.TIME_TURBO_ULTRA: 2
        }[self.time]

    def get_task_name(self):
        return "TriggerTask__%d__%s__%s" % (self.task_interval, timezone.now().strftime('%Y-%m-%d %H:%M:%S'), uuid.uuid4().hex)


class TriggerValues(models.Model):

    trigger = models.ForeignKey(Triggers, on_delete=models.CASCADE,
                                related_name='trigger_values', related_query_name='trigger_value')
    date_created = models.DateTimeField(auto_now_add=True)
    value = models.PositiveSmallIntegerField()
