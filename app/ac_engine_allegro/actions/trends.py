# coding: utf-8
from ac_engine.actions.trends import AbstractTrends
from django.conf import settings


class Trends(AbstractTrends):
    EXCLUSION_SET = settings.HINT_EXCLUSION_SET

    @property
    def data_processor_class(self):
        from ac_engine_allegro.data.data_processor import DataProcessor
        return DataProcessor

    @property
    def get_api_name(self):
        return 'allegro_trends'
