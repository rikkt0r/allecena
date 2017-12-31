# coding: utf-8

from ac_engine.data.data_container import AbstractDataContainer


# TODO ebay
class DataContainerSimple(AbstractDataContainer):
    FIELDS = ('id', 'field', 'names', 'for', 'ebay')


# TODO ebay
class DataContainerDetailed(AbstractDataContainer):
    FIELDS = ('id', 'field', 'names', 'for', 'ebay')
