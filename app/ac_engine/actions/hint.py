# coding: utf-8
from django.conf import settings

from ac_common.loggers import stat_logger
from ac_engine.actions.abstract import AbstractAction
from ac_computing.algorithm.shepard_algorithm import ShepardAlgorithm
from ac_computing.algorithm.Statistics import Statistics


class AbstractHint(AbstractAction):

    def __init__(self, input_params, data):
        super(AbstractHint, self).__init__(input_params, data)
        self.predicted_price = 0.0

    def prepare_data(self):
        for offer in self.offers:

            if offer:
                self.offers_data.append(offer.to_array(self.EXCLUSION_SET))
                self.offers_price.append(offer.price)

        self.offers_data_keys = self.offers[0].get_param_names(self.EXCLUSION_SET)

        os = Statistics(
            self.offers_data,
            self.offers_data_keys,
            self.offers_price
        )
        self.correlations = os.get_correlations()

        self.user_offer = self.data_container_class()
        self.user_offer.build_from_user_data(
            guarantee=self.input_params['item']['guarantee'],
            used=self.input_params['item']['used'],
            sellerShop=self.user_data['shop'],
            sellerRating=self.user_data['rating']
        )

        self.user_offer_data = self.user_offer.to_array(self.EXCLUSION_SET)

        stat_logger.info('Hint.prepare_data(): offers_data: %s' % (self.offers_data.__str__()))
        stat_logger.info('Hint.prepare_data(): offers_data_keys: %s' % (self.offers_data_keys.__str__()))
        stat_logger.info('Hint.prepare_data(): offers_price: %s' % (self.offers_price.__str__()))
        stat_logger.info('Hint.prepare_data(): user_offer_data: %s' % (self.user_offer_data.__str__()))
        stat_logger.info('Hint.prepare_data(): correlations: %s' % (self.correlations.__str__()))

        self.statistics = os.get_statistics(settings.HINT_CORRELATIONS_RESULT_NUMBER)
        stat_logger.info('Hint.prepare_data(): statistics: %s' % (self.statistics.__str__()))

        if settings.HINT_CORRELATIONS_FILTERING:
            self.offers_data = self.data_processor_class.correlations_filter(
                self.offers_data,
                self.correlations,
                settings.HINT_CORRELATIONS_FILTERING_MODE,
                settings.HINT_CORRELATIONS_FILTERING_THRESHOLD
                if settings.HINT_CORRELATIONS_FILTERING_MODE == 'threshold'
                else settings.HINT_CORRELATIONS_FILTERING_NUMBER
            )

            user_offer_data_temp = self.data_processor_class.correlations_filter(
                [self.user_offer_data],
                self.correlations,
                settings.HINT_CORRELATIONS_FILTERING_MODE,
                settings.HINT_CORRELATIONS_FILTERING_THRESHOLD
                if settings.HINT_CORRELATIONS_FILTERING_MODE == 'threshold'
                else settings.HINT_CORRELATIONS_FILTERING_NUMBER
            )

            self.user_offer_data = user_offer_data_temp[0]

            self.correlations = self.data_processor_class.correlations_filter_update(
                self.correlations,
                settings.HINT_CORRELATIONS_FILTERING_MODE,
                settings.HINT_CORRELATIONS_FILTERING_THRESHOLD
                if settings.HINT_CORRELATIONS_FILTERING_MODE == 'threshold'
                else settings.HINT_CORRELATIONS_FILTERING_NUMBER
            )

            stat_logger.info('Hint.prepare_data(): after correlations filtering: offers_data: %s'
                             % (str(self.offers_data)))
            stat_logger.info('Hint.prepare_data(): after correlations filtering: user_offer_data: %s'
                             % (str(self.user_offer_data)))
            stat_logger.info('Hint.prepare_data(): after correlations filtering: correlations: %s'
                             % (str(self.correlations)))

    def calculate(self):

        if settings.HINT_NORMALIZE:
            self.offers_data = self.data_processor_class.normalize(self.offers_data)

            stat_logger.info('Hint.calculate(): offers_data normalized: %s' % (str(self.offers_data)))

        if settings.HINT_CORRELATIONS:
            self.offers_data = self.data_processor_class.multiply_by_correlations(
                self.offers_data,
                self.correlations
            )

            stat_logger.info('Hint.calculate(): offers_data after multiplication by correlations: %s'
                             % (str(self.offers_data)))

        self.predicted_price = ShepardAlgorithm(
            self.offers_data,
            self.user_offer_data,
            self.offers_price
        ).calculate

        stat_logger.info('Hint.calculate(): predicted_price: %f' % self.predicted_price)

    def execute(self):

        self.prepare_data()
        self.calculate()

        self.result = {
            'predicted_price': self.predicted_price,
            'statistics': self.statistics
        }

    @property
    def serialize(self):
        return {
            "itemPrice": round(self.result['predicted_price'], 2)
        }
