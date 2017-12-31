# coding: utf-8
from ac_engine.data.data_container import AbstractDataContainer
from ac_common.loggers import stat_logger


class DataContainerSimple(AbstractDataContainer):
    FIELDS = ('id', 'name', 'hasPhotos', 'allegroStandard', 'shipmentFree', 'isBuyNow', 'priceBuyNow',
              'priceHighestBid', 'minPriceNotReached', 'minPriceSet', 'featurePromotion', 'featureHighlight',
              'featureBold', 'amountStart', 'amountLeft', 'used', 'offerInfinite', 'endingDate', 'success')

    def __init__(self, item=None):

        super(DataContainerSimple, self).__init__()

        if not item:
            stat_logger.info("DataContainerSimple: Using default constructor")

        else:
            self.id = item.itemId
            self.name = item.itemTitle

            try:
                self.hasPhotos = bool(item.photosInfo.item)
            except AttributeError:
                self.hasPhotos = True  # If only main photo exists

            additional_info = str(bin(item.additionalInfo)[2:]).ljust(5, '0')
            self.allegroStandard = bool(int(additional_info[0]))
            self.shipmentFree = bool(int(additional_info[1]))

            self.sellerRating = item.sellerInfo.userRating

            for price in item.priceInfo.item:
                if price.priceType == 'buyNow':
                    self.isBuyNow = True
                    self.priceBuyNow = price.priceValue
                if price.priceType == 'bidding' or price.priceType == 'withDelivery':
                    self.priceHighestBid = price.priceValue

            features = str(bin(item.promotionInfo)[2:]).ljust(5, '0')

            self.featurePromotion = bool(int(features[0]))
            self.featureHighlight = bool(int(features[1]))
            self.featureBold = bool(int(features[2]))

            self.amountStart = item.bidsCount + item.leftCount
            self.amountLeft = item.leftCount

            # priceBuyNow for auction type is the minimum price
            self.minPriceNotReached = True if (not self.isBuyNow and self.priceHighestBid < self.priceBuyNow) else False
            self.minPriceSet = True if (self.isBuyNow or (not self.isBuyNow and self.priceBuyNow > 0)) else False

            self.success = True if (self.amountStart > self.amountLeft or (not self.isBuyNow and item.biddersCount > 0)) else False

            self.used = False if item.conditionInfo == 'new' else True

            self.offerInfinite = True if item.timeToEnd == u'do wyczerpania przedmiotów' else False
            if not self.offerInfinite:
                self.endingDate = item.endingTime


# http://allegro.pl/webapi/documentation.php/show/id,52
# http://allegro.pl/webapi/faq.php#faq_5
class DataContainerDetailed(AbstractDataContainer):
    FIELDS = ('id', 'name', 'isBuyNow', 'priceBuyNow', 'priceHighestBid', 'hasPhotos', 'sellerRating', 'sellerShop',
              'sellerSuper', 'payuInstallment', 'allegroStandard', 'timeEnds', 'shipmentFree', 'minShipmentPrice',
              'minShipmentTime', 'isProduct', 'isBrandZone', 'isForGuests', 'featureHighlight', 'featurePromotion',
              'featureBold', 'amountStart', 'amountLeft', 'views', 'used', 'offerInfinite', 'minPriceNotReached',
              'minPriceSet', 'invoice', 'guarantee', 'paymentPayu', 'paymentOnDelivery', 'paymentTransfer', 'success',
              'endingDate')

    def __init__(self, item=None):
        super(DataContainerDetailed, self).__init__()

        if not item:
            stat_logger.info("DataContainerDetailed: Using default constructor")

        else:
            item_info = item.itemInfo
            item_payment = item.itemPaymentOptions
            item_postage_options = item.itemPostageOptions.item

            self.id = item_info.itId
            self.name = item_info.itName

            try:
                self.hasPhotos = bool(item_info.itFotoCount)
            except AttributeError:
                self.hasPhotos = True

            self.shipmentFree = False
            self.minShipmentPrice = 0.0

            for p in item_postage_options:
                if p.postageFreeShipping:
                    self.shipment_free = True
                    break

            # binary mask: http://allegro.pl/webapi/faq.php#faq_5
            features = str(bin(item.itemInfo.itOptions)[2:])
            self.featureBold = bool(int(features[0]))
            self.featureHighlight = bool(int(features[1]))
            self.featurePromotion = bool(int(features[2]))

            self.sellerRating = item_info.itSellerRating
            self.sellerShop = bool(int(features[3]))
            self.sellerSuper = False

            self.isBuyNow = bool(item_info.itBuyNowActive)
            self.priceBuyNow = float(item_info.itBuyNowPrice)
            self.priceHighestBid = float(item_info.itPrice)
            self.endingDate = item_info.itEndingTime
            self.allegroStandard = bool(item_info.itIsAllegroStandard)
            self.minShipmentTime = item_info.itOrderFulfillmentTime

            self.isProduct = bool(item_info.itHasProduct)
            self.isBrandZone = bool(item_info.itIsBrandZone)
            self.isForGuests = bool(item_info.itIsForGuests)

            self.amountStart = item_info.itStartingQuantity
            self.amountLeft = item_info.itQuantity
            self.views = item_info.itHitCount
            self.used = False if item_info.itIsNewUsed == 1 else True
            self.offerInfinite = True if item_info.itDurationInfo.durationType == 2 else False

            self.minPriceNotReached = True if float(item_info.itReservePrice) == -2.0 else False
            self.minPriceSet = True if float(item_info.itReservePrice) == 0.0 else False
            self.invoice = bool(item_info.itVatInvoice)

            self.paymentPayu = bool(item_payment.payOptionAllegroPay)
            self.paymentOnDelivery = bool(item_payment.payOptionOnDelivery)
            self.paymentTransfer = bool(item_payment.payOptionTransfer)

            if item_info.itEndingInfo in (1, 2) and (
                            self.amountLeft < self.amountStart or (not self.isBuyNow and item_info.itBidCount > 0)):
                self.success = True
            else:
                self.success = False

            try:
                for attr in item.itemAttribs.item:
                    if attr.attribName == 'Gwarancja' and \
                            (attr.attribValues.item[0] == 'Serwisowa' or attr.attribValues.item[0] == 'Producenta'):
                        self.guarantee = True
            except (TypeError, AttributeError):
                self.guarantee = False
