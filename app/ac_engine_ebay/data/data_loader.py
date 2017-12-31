# coding: utf-8

from ac_engine.data.data_loader import AbstractDataLoader
from django.conf import settings


class DataLoader(AbstractDataLoader):

    SOURCE = 'ebay'

    @staticmethod
    def get_api_class():
        from ac_engine_ebay.data.data_grabber import DataGrabber
        return DataGrabber

    @staticmethod
    def get_hint_input_current_quantity():
        return settings.HINT_INPUT_EBAY_CURRENT_QUANTITY

    @staticmethod
    def get_hint_input_ended_quantity():
        return settings.HINT_INPUT_EBAY_ENDED_QUANTITY

    @staticmethod
    def get_prediction_input_current_quantity():
        return settings.PREDICTION_INPUT_EBAY_CURRENT_QUANTITY

    @staticmethod
    def get_prediction_input_ended_quantity():
        return settings.PREDICTION_INPUT_EBAY_ENDED_QUANTITY
