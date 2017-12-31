# coding: utf-8
from ac_engine.actions.abstract import AbstractAction


class AbstractTrends(AbstractAction):

    EXCLUSION_SET = ()

    def prepare_data(self):
        pass

    def calculate(self):
        from ac_computing.algorithm.trends import Trends

        self.result = Trends(
            offers=self.offers
        ).calculate()

    def execute(self):
        self.prepare_data()
        self.calculate()

    @property
    def serialize(self):
        return {
            'dates': self.result['dates'],
            'meanPrices': self.result['meanPrices'],
            'amountSold': self.result['amountSold']
        }
