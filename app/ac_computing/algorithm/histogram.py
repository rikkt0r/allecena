# coding: utf-8


class Histogram(object):

    def __init__(self, current_prices, ended_prices):
        self.current_prices = current_prices
        self.ended_prices = ended_prices

    def calculate(self, ranges=20):

        import numpy

        min_cp = min(self.current_prices)
        max_cp = max(self.current_prices)

        min_ep = min(self.ended_prices)
        max_ep = max(self.ended_prices)

        min_range = min_cp if min_cp < min_ep else min_ep
        max_range = max_cp if max_cp > max_ep else max_ep

        range_step = int(round(((max_range-min_range)/ranges) / 5.0)) * 5

        range_range = range(int(min_range), int(max_range), range_step)

        return {
            'current': numpy.histogram(self.current_prices, bins=range_range),
            'ended': numpy.histogram(self.ended_prices, bins=range_range)
        }
