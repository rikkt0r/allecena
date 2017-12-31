# coding: utf-8
from django.conf import settings

from ac_common.loggers import stat_logger
from ac_engine.actions.abstract import AbstractAction
from ac_computing.algorithm.Statistics import Statistics
from ac_computing.algorithm.svm_algorithm import SVMAlgorithm


class AbstractPrediction(AbstractAction):

    def __init__(self, input_params, data):

        super(AbstractPrediction, self).__init__(input_params, data)

        self.offers_current_price = []
        self.offers_current_data = []

        self.offers_ended_price = []
        self.offers_ended_data = []
        self.offers_ended_classification = []

        self.selling_probability = 0.0

        if self.input_params['analysis']['advanced']:
            from ac_engine_allegro.data.data_container import DataContainerDetailed
            self.user_offer = DataContainerDetailed()
        else:
            from ac_engine_allegro.data.data_container import DataContainerSimple
            self.user_offer = DataContainerSimple()

    def prepare_data(self):
        self.offers_ended_classification = self.data_processor_class.get_classification(self.offers_ended)

        stat_logger.info('Prediction.prepare_data(): offers_ended_classification: %s'
                         % [str(offer) for offer in self.offers_ended_classification])

        for offer in self.offers:
            self.offers_data.append(offer.to_array(self.EXCLUSION_SET))
            self.offers_price.append(offer.price)

        self.offers_data_keys = self.offers[0].get_param_names(settings.PREDICTION_EXCLUSION_SET)

        for offer in self.offers_current:
            self.offers_current_data.append(offer.to_array(self.EXCLUSION_SET))
            self.offers_current_price.append(offer.price)

        for offer in self.offers_ended:
            self.offers_ended_data.append(offer.to_array(self.EXCLUSION_SET))
            self.offers_ended_price.append(offer.price)

        os = Statistics(
            self.offers_data,
            self.offers_data_keys,
            self.offers_price
        )

        self.correlations = os.get_correlations()
        stat_logger.info('Prediction.prepare_data(): correlations: %s' % (str(self.correlations)))

        self.statistics = os.get_statistics(settings.PREDICTION_CORRELATIONS_RESULT_NUMBER)
        stat_logger.info('Prediction.prepare_data(): statistics: %s' % (str(self.statistics)))

        buyNowImportant = False
        for corr in self.statistics['correlations']:
            setattr(self.user_offer, corr[0], 1.0)
            if corr[0] == 'isBuyNow':
                buyNowImportant = True

        if buyNowImportant:
            self.user_offer.priceBuyNow = round(self.statistics['median'], 2)
        else:
            self.user_offer.priceHighestBid = round(self.statistics['median'], 2)

        self.user_offer_data = self.user_offer.to_array(self.EXCLUSION_SET)

        stat_logger.info('Prediction.prepare_data(): offers_data: %s'
                         % (str(self.offers_data)))
        stat_logger.info('Prediction.prepare_data(): offers_data_keys: %s'
                         % (str(self.offers_data_keys)))
        stat_logger.info('Prediction.prepare_data(): offers_current_data: %s'
                         % (str(self.offers_current_data)))
        stat_logger.info('Prediction.prepare_data(): offers_ended_data: %s'
                         % (str(self.offers_ended_data)))
        stat_logger.info('Prediction.prepare_data(): offers_price: %s'
                         % (str(self.offers_price)))
        stat_logger.info('Prediction.prepare_data(): offers_current_price: %s'
                         % (str(self.offers_current_price)))
        stat_logger.info('Prediction.prepare_data(): offers_ended_price: %s'
                         % (str(self.offers_ended_price)))

        stat_logger.info('Prediction.prepare_data(): user_offer_data: %s' % (str(self.user_offer_data)))

        if settings.PREDICTION_CORRELATIONS_FILTERING:
            self.offers_data = self.data_processor_class.correlations_filter(
                self.offers_data,
                self.correlations,
                settings.PREDICTION_CORRELATIONS_FILTERING_MODE,
                settings.PREDICTION_CORRELATIONS_FILTERING_THRESHOLD
                if settings.PREDICTION_CORRELATIONS_FILTERING_MODE == 'threshold'
                else settings.PREDICTION_CORRELATIONS_FILTERING_NUMBER
            )

            self.offers_current_data = self.data_processor_class.correlations_filter(
                self.offers_current_data,
                self.correlations,
                settings.PREDICTION_CORRELATIONS_FILTERING_MODE,
                settings.PREDICTION_CORRELATIONS_FILTERING_THRESHOLD
                if settings.PREDICTION_CORRELATIONS_FILTERING_MODE == 'threshold'
                else settings.PREDICTION_CORRELATIONS_FILTERING_NUMBER
            )

            self.offers_ended_data = self.data_processor_class.correlations_filter(
                self.offers_ended_data,
                self.correlations,
                settings.PREDICTION_CORRELATIONS_FILTERING_MODE,
                settings.PREDICTION_CORRELATIONS_FILTERING_THRESHOLD
                if settings.PREDICTION_CORRELATIONS_FILTERING_MODE == 'threshold'
                else settings.PREDICTION_CORRELATIONS_FILTERING_NUMBER
            )

            user_offer_data_temp = self.data_processor_class.correlations_filter(
                [self.user_offer_data],
                self.correlations,
                settings.PREDICTION_CORRELATIONS_FILTERING_MODE,
                settings.PREDICTION_CORRELATIONS_FILTERING_THRESHOLD
                if settings.PREDICTION_CORRELATIONS_FILTERING_MODE == 'threshold'
                else settings.PREDICTION_CORRELATIONS_FILTERING_NUMBER
            )

            self.user_offer_data = user_offer_data_temp[0]

            self.correlations = self.data_processor_class.correlations_filter_update(
                self.correlations,
                settings.PREDICTION_CORRELATIONS_FILTERING_MODE,
                settings.PREDICTION_CORRELATIONS_FILTERING_THRESHOLD
                if settings.PREDICTION_CORRELATIONS_FILTERING_MODE == 'threshold'
                else settings.PREDICTION_CORRELATIONS_FILTERING_NUMBER
            )

            stat_logger.info('Prediction.prepare_data(): after correlations filtering: offers_data: %s'
                             % str(self.offers_data))
            stat_logger.info('Prediction.prepare_data(): after correlations filtering: offers_current_data: %s'
                             % str(self.offers_current_data))
            stat_logger.info('Prediction.prepare_data(): after correlations filtering: offers_ended_data: %s'
                             % str(self.offers_ended_data))
            stat_logger.info('Prediction.prepare_data(): after correlations filtering: user_offer_data: %s'
                             % str(self.user_offer_data))
            stat_logger.info('Prediction.prepare_data(): after correlations filtering: correlations: %s'
                             % str(self.correlations))

    def calculate(self):

        if settings.PREDICTION_NORMALIZE:
            self.offers_current_data = self.data_processor_class.normalize(self.offers_current_data)
            self.offers_ended_data = self.data_processor_class.normalize(self.offers_ended_data)
            self.user_offer_data = self.data_processor_class.normalize([self.user_offer_data])[0]

            stat_logger.info('Prediction.calculate(): offers_current_data normalized: %s'
                             % (str(self.offers_current_data)))
            stat_logger.info('Prediction.calculate(): offers_ended_data normalized: %s'
                             % (str(self.offers_ended_data)))
            stat_logger.info('Prediction.calculate(): user_offer_data normalized: %s'
                             % (str(self.user_offer_data)))

        if settings.PREDICTION_CORRELATIONS:
            self.offers_current_data = self.data_processor_class.multiply_by_correlations(
                self.offers_current_data,
                self.correlations
            )
            self.offers_ended_data = self.data_processor_class.multiply_by_correlations(
                self.offers_ended_data,
                self.correlations
            )
            self.user_offer_data = self.data_processor_class.multiply_by_correlations(
                [self.user_offer_data],
                self.correlations
            )[0]

            stat_logger.info('Prediction.calculate(): offers_current_data after multiplication by correlations: %s'
                             % str(self.offers_current_data))
            stat_logger.info('Prediction.calculate(): offers_ended_data after multiplication by correlations: %s'
                             % str(self.offers_ended_data))
            stat_logger.info('Prediction.calculate(): user_offer_data after multiplication by correlations: %s'
                             % str(self.user_offer_data))

        algorithm = SVMAlgorithm(
            self.offers_ended_data,
            self.offers_ended_classification,
            self.offers_current_data,
            self.user_offer_data
        )

        self.selling_probability = algorithm.calculate
        stat_logger.info('Prediction.calculate(): selling_probability: %f' % self.selling_probability)

    def execute(self):
        self.prepare_data()
        self.calculate()

        self.result = {
            "selling_probability": self.selling_probability,
            "statistics": self.statistics
        }

    @property
    def serialize(self):

        return {
            "sellingProbability": round(float(self.result['selling_probability']), 4)
        }
