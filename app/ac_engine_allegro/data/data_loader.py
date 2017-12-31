# coding: utf-8
from ac_engine.data.data_loader import AbstractDataLoader
from django.conf import settings


class DataLoader(AbstractDataLoader):

    SOURCE = 'allegro'

    @staticmethod
    def get_api_class():
        from ac_engine_allegro.data.data_grabber import DataGrabber
        return DataGrabber

    @staticmethod
    def get_hint_input_current_quantity():
        return settings.HINT_INPUT_ALLEGRO_CURRENT_QUANTITY

    @staticmethod
    def get_hint_input_ended_quantity():
        return settings.HINT_INPUT_ALLEGRO_ENDED_QUANTITY

    @staticmethod
    def get_prediction_input_current_quantity():
        return settings.PREDICTION_INPUT_ALLEGRO_CURRENT_QUANTITY

    @staticmethod
    def get_prediction_input_ended_quantity():
        return settings.PREDICTION_INPUT_ALLEGRO_ENDED_QUANTITY
