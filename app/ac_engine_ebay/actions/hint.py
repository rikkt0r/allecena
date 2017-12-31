# coding: utf-8

from django.conf import settings
from ac_engine.actions.hint import AbstractHint


class Hint(AbstractHint):
    EXCLUSION_SET = settings.HINT_EXCLUSION_SET

    @property
    def data_processor_class(self):
        from ac_engine_ebay.data.data_processor import DataProcessor
        return DataProcessor

    @property
    def get_api_name(self):
        return 'ebay_hint'
