# coding: utf-8
from ac_common.exceptions import AllecenaException
from ac_common.loggers import stat_logger, api_logger


class AbstractDataLoader(object):

    SOURCE = None

    @staticmethod
    def get_api_class():
        raise NotImplementedError()
    
    @staticmethod
    def get_hint_input_current_quantity():
        raise NotImplementedError()
    
    @staticmethod
    def get_hint_input_ended_quantity():
        raise NotImplementedError()
    
    @staticmethod
    def get_prediction_input_current_quantity():
        raise NotImplementedError()
    
    @staticmethod
    def get_prediction_input_ended_quantity():
        raise NotImplementedError()

    @classmethod
    def get_data(cls, input_params):

        a = cls.get_api_class()(input_params['analysis']['advanced'])

        offers_current = a.search(
            name=input_params['item']['name'],
            quantity=cls.get_hint_input_current_quantity(),
            buy_now_only=True,
            category_id=input_params['item']['category_id'],
            used=not bool(input_params['item']['used']),  # we ask user if it is new, so... negation
            guarantee=bool(input_params['item']['guarantee'])
        )

        offers_ended = a.search(
            name=input_params['item']['name'],
            quantity=cls.get_hint_input_ended_quantity(),
            finished=True,
            buy_now_only=True,
            category_id=input_params['item']['category_id'],
            used=not bool(input_params['item']['used']),
            guarantee=bool(input_params['item']['guarantee'])
        )

        offers = offers_ended + offers_current
        account_id = a.get_user_id(input_params['account'][cls.SOURCE])
        user_data = a.get_user_data(account_id)

        stat_logger.info("DataLoader.get_data(): len(offers_current): {}".format(len(offers_current)))
        stat_logger.info("DataLoader.get_data(): len(offers_ended): {}".format(len(offers_ended)))
        stat_logger.info("DataLoader.get_data(): user_data: {}".format(str(user_data)))

        if len(offers_current) == 0 or len(offers_ended) == 0 or user_data is None:
            raise AllecenaException('Error occurred: Getting data')

        elif len(offers_current) < cls.get_hint_input_ended_quantity()/2:
            api_logger.error('Error occurred: Got not enough data')

        return {
            'offers': offers,
            'offers_current': offers_current,
            'offers_ended': offers_ended,
            'user_data': user_data
        }
