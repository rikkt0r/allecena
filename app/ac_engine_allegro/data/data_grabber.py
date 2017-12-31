# coding: utf-8
import itertools
from math import ceil
from django.conf import settings
from suds.client import Client, WebFault

from ac_common.exceptions import AllecenaException
from ac_common.loggers import api_logger, exception_logger
from ac_common.utils import maintain_api_session, grabber_exception_fallback, chunks

from ac_engine.data.data_grabber import AbstractDataGrabber
from ac_engine_allegro.data.data_container import DataContainerSimple, DataContainerDetailed


class DataGrabber(AbstractDataGrabber):

    FAULTS = {
        'version_expired': 'ERR_INVALID_VERSION_CAT_SELL_FIELDS',
        'session_expired': ('ERR_NO_SESSION', 'ERR_SESSION_EXPIRED'),
        'api_is_dead': 'ERR_WEBAPI_NOT_AVAIL',
        'user_not_found': 'ERR_USER_NOT_FOUND'
    }

    def __init__(self, advanced_mode=False):
        from suds.cache import DocumentCache

        self.c = Client(url=settings.ALLEGRO_SOAP_WSDL, location=settings.ALLEGRO_SOAP_URL, cache=DocumentCache(hours=2))
        self.version = self._get_version()
        self.token = self._get_session()
        self.ADVANCED_MODE = advanced_mode

    @grabber_exception_fallback
    def _set_version(self):
        # http://allegro.pl/webapi/documentation.php/show/id,61
        version = self.c.service.doQuerySysStatus(
            sysvar=1,
            countryId=settings.ALLEGRO_COUNTRY,
            webapiKey=settings.ALLEGRO_KEY
        ).verKey

        if not version:
            raise Exception()

        with open(settings.ALLEGRO_VERSION_FILE, 'w') as f:
            f.write(str(version))

        self.version = version

    def _get_version(self):
        try:
            with open(settings.ALLEGRO_VERSION_FILE, 'r') as f:
                return f.read()
        except Exception as e:
            api_logger.warning(e)
            self._set_version()
            return self.version

    def _get_session(self):
        try:
            with open(settings.ALLEGRO_SESSION_FILE, 'r') as f:
                return f.read()
        except Exception as e:
            exception_logger.warning(e)
            self.set_user_token()
            return self.token

    @grabber_exception_fallback
    def set_user_token(self, stop=False):
        # http://allegro.pl/webapi/documentation.php/show/id,83
        try:
            token = self.c.service.doLoginEnc(
                userLogin=settings.ALLEGRO_LOGIN,
                userHashPassword=settings.ALLEGRO_PASSWORD_HASH,
                countryCode=settings.ALLEGRO_COUNTRY,
                webapiKey=settings.ALLEGRO_KEY,
                localVersion=self.version
            ).sessionHandlePart

            if not token:
                raise Exception()

            with open(settings.ALLEGRO_SESSION_FILE, 'w') as f:
                f.write(str(token))

            self.token = token

        except WebFault as e:
            if e.fault.faultcode == self.FAULTS['version_expired']:
                api_logger.warning('API version key expired, pinging API for new')
                self._set_version()
                if not stop:
                    self.set_user_token(stop=True)
            else:
                raise e

    @grabber_exception_fallback
    def get_user_id(self, login, fresh=False):
        # http://allegro.pl/webapi/documentation.php/show/id,102
        from ac_common.models import User

        user = None

        try:
            user = User.objects.get(allegro_user_name=login)
            if not fresh and user.allegro_user_id:
                return user.allegro_user_id

        except (User.DoesNotExist, User.MultipleObjectsReturned):
            pass

        try:
            user_id = self.c.service.doGetUserID(
                countryId=settings.ALLEGRO_COUNTRY,
                userLogin=login,
                userEmail='',
                webapiKey=settings.ALLEGRO_KEY
            )
        except WebFault as e:
            if e.fault.faultcode == self.FAULTS['user_not_found']:
                api_logger.error('User %s not found' % login)
                raise AllecenaException('Error occurred: User not found')
            raise e

        if user:
            user.allegro_user_id = user_id
            user.save()

        return user_id

    @grabber_exception_fallback
    def get_user_data(self, user_id):
        user = self.c.service.doShowUser(
            webapiKey=settings.ALLEGRO_KEY,
            countryId=settings.ALLEGRO_COUNTRY,
            userId=user_id
        )

        try:
            rating = user.userRating
            shop = bool(user.userHasShop)
            super_seller = bool(user.userIsSseller)
        except TypeError:
            rating = 0
            shop = False
            super_seller = False

        return {
            'rating': rating,
            'shop': shop,
            'super_seller': super_seller
        }

    def get_categories(self):

        self._set_version()

        cat_list = self.c.service.doGetCatsData(
            webapiKey=settings.ALLEGRO_KEY,
            countryId=settings.ALLEGRO_COUNTRY,
            localVersion=self.version,
        ).catsList.item

        cats = []

        # >24k categories O(n^2) :-)
        for cat in cat_list:
            parent_name = ""
            if cat.catParent:
                for c in cat_list:
                    if c.catId == cat.catParent:
                        parent_name = c.catName
            cats.append({
                'id': cat.catId,
                'name': cat.catName,
                'parent_id': cat.catParent,
                'parent_name': parent_name
            })

        # return sorted(cats, key=lambda k: k['id'])
        return cats

    @grabber_exception_fallback
    def get_user_auctions(self, user_name):

        user_id = self.get_user_id(user_name)

        sort_options = self.c.factory.create('SortOptionsType')
        sort_options.sortType = 'endingTime'
        sort_options.sortOrder = 'asc'
        filter_options = self.c.factory.create('ArrayOfFilteroptionstype')

        opt = self.c.factory.create('FilterOptionsType')
        opt.filterId = 'userId'
        opt.filterValueId = self.c.factory.create('ArrayOfString')
        opt.filterValueId.item.append(str(user_id))
        filter_options.item.append(opt)

        items = self.c.service.doGetItemsList(
            webapiKey=settings.ALLEGRO_KEY,
            countryId=settings.ALLEGRO_COUNTRY,
            resultSize=120,
            resultScope=2,
            sortOptions=sort_options,
            filterOptions=filter_options
        )

        if not items.itemsCount and not items.itemsFeaturedCount:
            return []

        ids = [item.itemId for item in items.itemsList.item]
        api_logger.info("get_user_auctions ID's: %s" % str(ids))

        items_detailed = self._get_items_detailed(ids)

        objs = []

        for item in items_detailed:
            cats = item.itemCats.item

            objs.append({
                'id': item.itemInfo.itId,
                'name': item.itemInfo.itName,
                'categoryId': cats[-2].catId if len(cats) > 1 else cats[-1].catId,
                'categoryName': cats[-2].catName + " w kategorii " + cats[-1].catName if len(cats) > 1 else cats[-1].catName,
                'url': "http://allegro.pl/hello-allegro-i{item_id}.html".format(item_id=item.itemInfo.itId)
            })

        return objs

    @grabber_exception_fallback
    @maintain_api_session
    def get_offer_by_id(self, offerId):

        offer_id = self.c.factory.create('ArrayOfLong')
        offer_id.item = [offerId]

        tmp = self.c.service.doGetItemsInfo(
            sessionHandle=self.token,
            itemsIdArray=offer_id,
            getDesc=0,
            getImageUrl=0,
            getAttribs=1,
            getPostageOptions=1,
            getCompanyInfo=1,
        )

        item = tmp.arrayItemListInfo.item[0]
        category = item.itemCats.item[-1].catId

        obj = DataContainerDetailed(item=item)

        return [obj, category]

    def __get_sort_options(self):
        sort_options = self.c.factory.create('SortOptionsType')
        sort_options.sortType = 'popularity'
        sort_options.sortOrder = 'desc'
        return sort_options

    def __build_filter_list(self, category_id, name, buy_now_only=False, finished=False, similar=False, **kwargs):
        filter_options = self.c.factory.create('ArrayOfFilteroptionstype')

        if category_id:
            opt = self.c.factory.create('FilterOptionsType')
            opt.filterId = 'category'
            opt.filterValueId = self.c.factory.create('ArrayOfString')
            opt.filterValueId.item.append(str(category_id))
            filter_options.item.append(opt)

        if len(name) > 0:
            opt = self.c.factory.create('FilterOptionsType')
            opt.filterId = 'search'
            opt.filterValueId = self.c.factory.create('ArrayOfString')
            opt.filterValueId.item.append(name)
            filter_options.item.append(opt)

        if buy_now_only:
            opt = self.c.factory.create('FilterOptionsType')
            opt.filterId = 'offerType'
            opt.filterValueId = self.c.factory.create('ArrayOfString')
            opt.filterValueId.item.append('buyNow')
            filter_options.item.append(opt)

        if finished:
            opt = self.c.factory.create('FilterOptionsType')
            opt.filterId = 'closed'
            opt.filterValueId = self.c.factory.create('ArrayOfString')
            opt.filterValueId.item.append('true')
            filter_options.item.append(opt)

        if similar:
            opt = self.c.factory.create('FilterOptionsType')
            opt.filterId = 'similar'
            opt.filterValueId = self.c.factory.create('ArrayOfString')
            opt.filterValueId.item.append('true')
            filter_options.item.append(opt)

        if 'used' in kwargs:
            opt = self.c.factory.create('FilterOptionsType')
            opt.filterId = 'condition'
            opt.filterValueId = self.c.factory.create('ArrayOfString')
            opt.filterValueId.item.append('used' if kwargs['used'] else 'new')
            filter_options.item.append(opt)

        if 'guarantee' in kwargs:
            opt = self.c.factory.create('FilterOptionsType')
            opt.filterId = '1954'
            opt.filterValueId = self.c.factory.create('ArrayOfString')
            if kwargs['guarantee']:
                opt.filterValueId.item.append('1')  # factory guarantee
                opt.filterValueId.item.append('2')  # service guarantee
            else:
                opt.filterValueId.item.append('3')  # no guarantee
            filter_options.item.append(opt)

        return filter_options

    def _get_items_general(self, quantity, category_id, name, buy_now_only, finished=False, **kwargs):
        items = self.c.service.doGetItemsList(
            webapiKey=settings.ALLEGRO_KEY,
            countryId=settings.ALLEGRO_COUNTRY,
            resultSize=quantity,
            resultScope=2,
            sortOptions=self.__get_sort_options(),
            filterOptions=self.__build_filter_list(category_id, name, buy_now_only, finished, **kwargs)
        ).itemsList.item

        if not items:
            items = self.c.service.doGetItemsList(
                webapiKey=settings.ALLEGRO_KEY,
                countryId=settings.ALLEGRO_COUNTRY,
                resultSize=quantity,
                resultScope=2,
                sortOptions=self.__get_sort_options(),
                filterOptions=self.__build_filter_list(category_id, name, buy_now_only, finished, similar=True, **kwargs)
            ).itemsList.item

        return items

    @maintain_api_session
    def _get_items_detailed(self, ids):
        # using python threads
        from multiprocessing.pool import ThreadPool
        # thread emulation using processes
        # from multiprocessing.dummy import Pool as ThreadPool

        pool_size = int(ceil(len(ids)/25.0))
        pool_size = pool_size if pool_size < 8 else 8
        pool = ThreadPool(pool_size)

        api_logger.info('THREAD POOL SIZE: %d' % pool_size)

        def _get_data(idz):

            ids_soap = self.c.factory.create('ArrayOfLong')
            ids_soap.item = idz

            tmp = self.c.service.doGetItemsInfo(
                sessionHandle=self.token,
                itemsIdArray=ids_soap,
                getDesc=0,
                getImageUrl=0,
                getAttribs=1,
                getPostageOptions=1,
                getCompanyInfo=0,
            )

            return tmp.arrayItemListInfo.item

        items = pool.map(_get_data, chunks(ids, 25))
        return list(itertools.chain.from_iterable(items))

    @grabber_exception_fallback
    def search(self, name="", quantity=100, finished=False, buy_now_only=False, category_id=None, **kwargs):

        from time import time
        time_start = time()

        items = self._get_items_general(quantity, category_id, name, buy_now_only, finished, **kwargs)
        ids = [item.itemId for item in items]

        api_logger.info(str(ids))

        objects = []

        if self.ADVANCED_MODE:
            items_detailed = self._get_items_detailed(ids)

            for item in items_detailed:
                objects.append(DataContainerDetailed(item))
        else:
            items_detailed = items

            for item in items_detailed:
                objects.append(DataContainerSimple(item))

        api_logger.info("ITEMS AFTER FILTRATION: {} (from: {}) TYPE: {}".format(
            len(items_detailed),
            quantity,
            'historic' if finished else 'current')
        )

        if objects[-1] is None:
            raise AllecenaException('Something is seriously wrong with introductory data processing')

        api_logger.info('Time spent on downloading {} items: {}s\n'.format(quantity, round(time() - time_start, 2)))

        return objects
