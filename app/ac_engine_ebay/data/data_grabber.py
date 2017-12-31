# coding: utf-8

from ac_engine.data.data_grabber import AbstractDataGrabber


class DataGrabber(AbstractDataGrabber):
    def get_offer_by_id(self, offerId):
        pass

    def get_user_auctions(self, user_name):
        pass

    def _get_items_general(self, quantity, category_id, name, buy_now_only, finished=False, **kwargs):
        pass

    def search(self, name="", quantity=100, finished=False, buy_now_only=False, category_id=None, **kwargs):
        pass

    def get_user_id(self, login):
        pass

    def _get_items_detailed(self, ids):
        pass

    def get_user_data(self, user_id):
        pass

    def __init__(self, advanced_mode=False):
        pass

    def get_categories(self):
        pass
