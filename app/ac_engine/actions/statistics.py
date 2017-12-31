# coding: utf-8
from ac_engine.actions.abstract import AbstractAction


class AbstractStatistics(AbstractAction):

    EXCLUSION_SET = ()

    @property
    def data_container_class(self):
        return None

    def prepare_data(self):

        for offer in self.offers:
            if offer:
                self.offers_data.append(offer.to_array(self.EXCLUSION_SET))
                self.offers_price.append(offer.price)

        self.offers_data_keys = self.offers[0].get_param_names(self.EXCLUSION_SET)

    def calculate(self):
        from django.conf import settings
        from ac_computing.algorithm.Statistics import Statistics

        os = Statistics(
            self.offers_data,
            self.offers_data_keys,
            self.offers_price
        )
        self.correlations = os.get_correlations()

        self.statistics = os.get_statistics(settings.HINT_CORRELATIONS_RESULT_NUMBER)

    def execute(self):
        self.prepare_data()
        self.calculate()

        self.result = {
            'statistics': self.statistics
        }

    @property
    def serialize(self):
        return {
            "price": {
                "min": round(float(self.result['statistics']['min']), 2),
                "max": round(float(self.result['statistics']['max']), 2),
                "mean": round(float(self.result['statistics']['mean']), 2),
                "median": round(float(self.result['statistics']['median'][0]), 2)
                if type(self.result['statistics']['median']) is list
                else round(float(self.result['statistics']['median']), 2),
                "deviation": round(float(self.result['statistics']['stdDev']), 2)
            },
            "correlations":
                [{'name': c[0], 'value': round(float(c[1]), 2)} for c in self.result['statistics']['correlations']]
        }
