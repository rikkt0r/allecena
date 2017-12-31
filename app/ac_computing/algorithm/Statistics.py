# coding: utf-8

import math
import operator

from ac_common.utils import median
from scipy.stats.stats import pearsonr


class Statistics(object):
    
    def __init__(self, offers_data, offers_keys, prices):
        self.offers_data = offers_data
        self.offers_keys = offers_keys
        self.prices = prices
        self.correlations_factors = []

    def get_statistics(self, correlations_mode):

        result = {
            'min': min(i for i in self.prices),
            'max': max(i for i in self.prices),
            'mean': sum(i for i in self.prices) / float(len(self.prices)),
            'median': (median([float(i) for i in self.prices]))
        }
        std_dev_sum = 0.0

        for i in self.prices:
            std_dev_sum += math.pow((i - result['mean']), 2)

        result['stdDev'] = math.sqrt(std_dev_sum) * (1.0 / (len(self.prices) - 1))
        
        result_correlations = []
        
        if correlations_mode > 0 and len(self.correlations_factors) > 0:
            result_correlations = self.correlations_factors[:correlations_mode]
            
        result['correlations'] = result_correlations

        return result

    def get_correlations(self):
        correlations = []
        correlations_factors_unordered = {}
        variables = zip(*self.offers_data)

        for variable in variables:
            correlation = pearsonr(self.prices, variable)[0]

            if math.isnan(correlation):
                correlation = 0.0

            correlations.append(correlation)

        for key in self.offers_keys:
            correlations_factors_unordered[key] = abs(correlations[self.offers_keys.index(key)])
           
        self.correlations_factors = list(reversed(sorted(correlations_factors_unordered.items(), key=operator.itemgetter(1))))
        
        return correlations
