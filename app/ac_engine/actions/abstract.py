# coding: utf-8
from ac_common.loggers import stat_logger


class AbstractAction(object):

    EXCLUSION_SET = ()
    ADVANCED_MODE = False

    @property
    def data_processor_class(self):
        raise NotImplemented()

    @property
    def data_container_class(self):
        raise NotImplemented()

    @property
    def get_api_name(self):
        raise NotImplemented()

    def prepare_data(self):
        raise NotImplemented()

    def calculate(self):
        raise NotImplemented()

    def execute(self):
        raise NotImplemented()

    @property
    def serialize(self):
        raise NotImplemented()

    def __init__(self, input_params, data):
        stat_logger.info('Action.__init__(), input_params: %s' % (input_params.__str__()))
        self.input_params = input_params

        self.ADVANCED_MODE = input_params['analysis']['advanced']

        self.offers = data['offers']
        self.offers_current = data['offers_current']
        self.offers_ended = data['offers_ended']
        self.user_data = data['user_data']

        self.offers_price = []
        self.offers_data = []
        self.offers_data_keys = []

        self.user_offer = []
        self.user_offer_data = {}

        self.correlations = []
        self.statistics = {}

        self.result = {}
