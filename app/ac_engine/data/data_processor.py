# coding: utf-8


class AbstractDataProcessor(object):

    @staticmethod
    def multiply_by_correlations(data, correlations):
        for i, dataItem in enumerate(data):
            for j, variableValue in enumerate(dataItem):
                data[i][j] = data[i][j] * abs(correlations[j])
        return data

    @staticmethod
    def normalize(data):

        import math
        for i, dataItem in enumerate(data):
            for j, variableValue in enumerate(dataItem):

                try:
                    max_value = max(list(zip(*data))[j], key=abs)
                    data[i][j] = data[i][j] / max_value
                except ZeroDivisionError:
                    data[i][j] = 0.0

                if math.isnan(data[i][j]) or math.isinf(data[i][j]):
                    data[i][j] = 0.0

        return data

    @staticmethod
    def correlations_filter(data, correlations, mode, parameter):
        variables_tuple = zip(*data)
        variables = [list(i) for i in variables_tuple]
        result_variables = []

        if mode == 'threshold':
            for i, correlation in enumerate(correlations):

                if abs(correlation) > parameter:
                    result_variables.append(variables[i])

            result = zip(*result_variables)
            return [list(i) for i in result]

        elif mode == 'number':
            import heapq
            import numpy as np
            correlations = np.absolute(correlations).tolist()
            max_correlations = heapq.nlargest(parameter, correlations)

            for i, correlation in enumerate(correlations):

                if correlation in max_correlations:
                    result_variables.append(variables[i])

            result = zip(*result_variables)
            result_list = [list(i) for i in result]

            return result_list

        else:
            return data

    @staticmethod
    def correlations_filter_update(correlations, mode, parameter):
        result_correlations = []

        if mode == 'threshold':
            for i, correlation in enumerate(correlations):

                if abs(correlation) > parameter:
                    result_correlations.append(correlation[i])

            return [float(i) for i in result_correlations]

        elif mode == 'number':
            import heapq
            import numpy as np
            correlations = np.absolute(correlations).tolist()
            result_correlations = heapq.nlargest(parameter, correlations)

            return [float(i) for i in result_correlations]

        else:
            return correlations

    @staticmethod
    def get_win_and_lose(offers):
        win = []
        lose = []

        for offer in offers:
            if offer.success:
                win.append(offer)
            else:
                lose.append(offer)

        return {
            'win': win,
            'lose': lose,
        }

    @staticmethod
    def get_classification(offers):
        classification = []

        for offer in offers:
            if offer.success:
                classification.append(1.0)
            else:
                classification.append(-1.0)

        return classification
