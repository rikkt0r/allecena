# coding: utf-8
from ac_engine.actions.abstract import AbstractAction


class AbstractHistogram(AbstractAction):

    EXCLUSION_SET = ()

    def __init__(self, input_params, data):
        super(AbstractHistogram, self).__init__(input_params, data)

        self.current_prices = []
        self.ended_prices = []
        self.histogram = {}

    def prepare_data(self):
        for off in self.offers_current:
            self.current_prices.append(off.price)

        for off in self.offers_ended:
            self.ended_prices.append(off.price)

    def calculate(self):
        from ac_computing.algorithm.histogram import Histogram

        self.histogram = Histogram(
            current_prices=self.current_prices,
            ended_prices=self.ended_prices
        ).calculate()

    def execute(self):
        self.prepare_data()
        self.calculate()

        self.result = {
            'current': self.histogram['current'],
            'ended': self.histogram['ended']
        }

    @property
    def serialize(self):
        return {
            "current": {
                "counts": self.result['current'][0].tolist(),
                "prices": [round(p, 2) for p in self.result['current'][1].tolist()]
            },
            "ended": {
                "counts": self.result['ended'][0].tolist(),
                "prices": [round(p, 2) for p in self.result['ended'][1].tolist()]
            },
        }
