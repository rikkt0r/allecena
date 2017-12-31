# coding: utf-8

from django.conf import settings
from ac_engine.actions.prediction import AbstractPrediction


class Prediction(AbstractPrediction):
    EXCLUSION_SET = settings.PREDICTION_EXCLUSION_SET

    @property
    def data_loader_class(self):
        from ac_engine_ebay.data.data_loader import DataLoader
        return DataLoader

    @property
    def data_processor_class(self):
        from ac_engine_ebay.data.data_processor import DataProcessor
        return DataProcessor

    @property
    def get_api_name(self):
        return 'ebay_prediction'
