# coding: utf-8
import logging

stat_logger = logging.getLogger('statistics')
exception_logger = logging.getLogger('exception')
api_logger = logging.getLogger('api')

logging.getLogger('suds.client').setLevel(logging.CRITICAL)
