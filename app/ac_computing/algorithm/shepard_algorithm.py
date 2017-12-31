# coding: utf-8

import math
from ac_common.loggers import stat_logger


class ShepardAlgorithm(object):
    
    def __init__(self, historical_input_data, current_data, predictable_values):
        self.historical_input_data = historical_input_data
        self.current_data = current_data
        self.predictable_values = predictable_values

        self.items = self.historical_input_data.__len__()
        self.variables = self.historical_input_data[0].__len__()
          
    def calculate_metrics(self):
        metrics = []
        
        for i in range(0, self.items):
            item_metric = 0.0
            
            for j in range(0, self.variables):
                variable_metric = math.pow(self.historical_input_data[i][j] - self.current_data[j], 2)
                item_metric += variable_metric
               
            metrics.append(math.sqrt(item_metric))

        return metrics

    @staticmethod
    def calculate_weights(metrics):
        weights = []
        max_metric = max(metrics)

        for metric in metrics:
            try:
                weights.append(math.pow((max_metric - metric)/(max_metric * metric), 2))
            except ZeroDivisionError:
                weights.append(0.0)
         
        return weights

    @staticmethod
    def normalize_weights(weights):
        normalized_weights = []
        sum_weights = sum(weights)

        for weight in weights:
            try:
                normalized_weights.append(weight / sum_weights)
            except ZeroDivisionError:
                normalized_weights.append(0.0)
         
        return normalized_weights
        
    def calculate_predicted_value(self, normalized_weights):
        predicted_value = 0.0
    
        for i in range(0, normalized_weights.__len__()):
            predicted_value += normalized_weights[i] * self.predictable_values[i]
         
        return predicted_value

    @property
    def calculate(self):
        metrics = self.calculate_metrics()
        stat_logger.info('ShepardAlgorithm.calculateMetrics(): %s' % metrics)

        weights = self.calculate_weights(metrics)
        stat_logger.info('ShepardAlgorithm.calculateWeights(): %s' % weights)

        normalized_weights = self.normalize_weights(weights)
        stat_logger.info('ShepardAlgorithm.normalizeWeights(): %s' % normalized_weights)

        predicted_value = self.calculate_predicted_value(normalized_weights)
        stat_logger.info('ShepardAlgorithm.calculatePredictedValue(): %s' % predicted_value)
       
        return predicted_value
