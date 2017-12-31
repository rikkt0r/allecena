# coding: utf-8


class AbstractDataGrabber(object):

    ADVANCED_MODE = False

    def __init__(self, advanced_mode=False):
        # Api Version
        # Token auth
        raise NotImplementedError()

    def get_user_id(self, login):
        # User Id based on login
        raise NotImplementedError()

    def get_user_data(self, user_id):
        # user data (rating, isShop, isSuperSeller)
        raise NotImplementedError()

    def get_categories(self):
        # download categories from api
        # return in the list of dict(id, name, parent_id, parent_name)
        raise NotImplementedError()

    def get_user_auctions(self, user_name):
        # download user auction from api
        # return in the list of dict(auction_id, auction_name, auction_cat_id, auction_cat_name)
        raise NotImplementedError()

    def get_offer_by_id(self, offerId):
        # single offer by auctionId
        raise NotImplementedError()

    def __get_sort_options(self):
        raise NotImplementedError()

    def __build_filter_list(self, category_id, name, buy_now_only=False, finished=False, similar=False, **kwargs):
        raise NotImplementedError()

    def _get_items_general(self, quantity, category_id, name, buy_now_only, finished=False, **kwargs):
        raise NotImplementedError()

    def _get_items_detailed(self, ids):
        raise NotImplementedError()

    def search(self, name="", quantity=100, finished=False, buy_now_only=False, category_id=None, **kwargs):
        raise NotImplementedError()
