# coding: utf-8

from sklearn import svm
from django.conf import settings
from ac_common.loggers import stat_logger


class SVMAlgorithm(object):

    def __init__(self, historical_data, historical_data_classification, current_data, analyzed_item):
        self.historical_data = historical_data
        self.historical_data_classification = historical_data_classification
        self.current_data = current_data
        self.analyzed_item = analyzed_item

    def prepare_data(self, win_data, lose_data):
        self.historical_data = win_data + lose_data
        self.historical_data_classification = [-1] * len(lose_data) + [1] * len(win_data)

    def find_neighbors(self, classification, threshold, win_only=True):
        neighbors = []
        
        for item in self.current_data:
            i = self.current_data.index(item)
            item_to_add = True
            
            for variable in item:
                j = item.index(variable)

                if (win_only and classification[i] == 1.0) or not win_only:
                    if not (self.analyzed_item[j] - threshold < variable < self.analyzed_item[j] + threshold):
                        item_to_add = False
                        break

                else:
                    item_to_add = False
            
            if item_to_add:
                neighbors.append(item)

        return neighbors

    @property
    def calculate(self):

        svm_engine = svm.SVC(
            C=settings.PREDICTION_SVM_C,
            kernel=settings.PREDICTION_SVM_KERNEL,
            degree=settings.PREDICTION_SVM_DEGREE,
            gamma=settings.PREDICTION_SVM_GAMMA,
            coef0=settings.PREDICTION_SVM_COEF0,
            shrinking=settings.PREDICTION_SVM_SHRINKING,
            probability=settings.PREDICTION_SVM_PROBABILITY,
            tol=settings.PREDICTION_SVM_TOL,
            cache_size=settings.PREDICTION_SVM_CACHE_SIZE,
            class_weight=settings.PREDICTION_SVM_CLASS_WEIGHT,
            verbose=settings.PREDICTION_SVM_VERBOSE,
            max_iter=settings.PREDICTION_SVM_MAX_ITER,
            random_state=settings.PREDICTION_SVM_RANDOM_STATE
        )
        
        svm_engine.fit(self.historical_data, self.historical_data_classification)
       
        current_data_classification = svm_engine.predict(self.current_data)
        stat_logger.info('SVMAlgorithm.calculate(): current_data_classification: %s'
                         % current_data_classification.__str__())

        probability_array = svm_engine.predict_proba([self.analyzed_item]).tolist()
        stat_logger.info('SVMAlgorithm.calculate(): probability_array: %s' % probability_array.__str__())

        probability = probability_array[0][1]
        stat_logger.info('SVMAlgorithm.calculate(): probability: %s' % probability.__str__())
        
        if settings.PREDICTION_NEIGHBORS:
            neighbors = self.find_neighbors(current_data_classification,
                                            settings.PREDICTION_NEIGHBORS_THRESHOLD,
                                            settings.PREDICTION_NEIGHBORS_WIN_ONLY
                                            )

            neighbors_number = len(neighbors)
            try:
                probability_coefficient = (1.0 - float(neighbors_number) / float(len(self.current_data)))
            except ZeroDivisionError:
                probability_coefficient = 1.0

            probability *= probability_coefficient

            stat_logger.info('SVMAlgorithm.calculate(): neighbors: %s' % str(neighbors))
            stat_logger.info('SVMAlgorithm.calculate(): neighbors_number: %s' % str(neighbors_number))
            stat_logger.info('SVMAlgorithm.calculate(): probability_coefficient: %s' % str(probability_coefficient))
            stat_logger.info('SVMAlgorithm.calculate(): probability: %s' % str(probability))
       
        return probability 
