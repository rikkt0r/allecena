# coding: utf-8
from django.conf import settings
from ac_engine.actions.prediction import AbstractPrediction


class Prediction(AbstractPrediction):
    EXCLUSION_SET = settings.PREDICTION_EXCLUSION_SET

    @property
    def data_processor_class(self):
        from ac_engine_allegro.data.data_processor import DataProcessor
        return DataProcessor

    @property
    def data_container_class(self):
        from ac_engine_allegro.data.data_container import DataContainerSimple, DataContainerDetailed
        return DataContainerDetailed if self.ADVANCED_MODE else DataContainerSimple

    @property
    def get_api_name(self):
        return 'allegro_prediction'
