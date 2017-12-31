# coding: utf-8

from ac_common.loggers import stat_logger


class AbstractDataContainer(object):

    FIELDS = ()

    def __init__(self):
        for key in self.FIELDS:
            setattr(self, key, 0.0)

    def build_from_user_data(self, **kwargs):
        for key, val in kwargs.iteritems():
            if key in self.FIELDS:
                setattr(self, key, val)

    def __str__(self):
        return str((k, getattr(self, k, None)) for k in self.FIELDS)

    @property
    def price(self):
        return self.priceBuyNow if self.priceBuyNow > self.priceHighestBid else self.priceHighestBid

    def to_array(self, exclusion_set):
        result = []
        keys = set(self.FIELDS) - set(exclusion_set)

        for key in keys:
            try:
                result.append(float(getattr(self, key, None)))
            except (ValueError, TypeError):
                from ac_common.loggers import stat_logger
                stat_logger.error("DataContainer.toArray()", "Exception during conversion to array, param: %s" % str(key))
                result.append(0.0)

        return result

    def get_param_names(self, exclusion_set):
        return [key for key in self.FIELDS if key not in exclusion_set]
