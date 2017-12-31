# coding: utf-8
from django.conf import settings
from ac_engine.actions.statistics import AbstractStatistics


class Statistics(AbstractStatistics):
    EXCLUSION_SET = settings.HINT_EXCLUSION_SET

    @property
    def data_processor_class(self):
        from ac_engine_allegro.data.data_processor import DataProcessor
        return DataProcessor

    @property
    def get_api_name(self):
        return 'allegro_statistics'
