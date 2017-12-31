# coding: utf-8
import os
from django.test.runner import DiscoverRunner
from django.conf import settings


class AcTestRunner(DiscoverRunner):

    def __init__(self, **kwargs):
        super(AcTestRunner, self).__init__(**kwargs)

        self.no_db = kwargs.get('no_db', None) if kwargs.get('no_db', None) is not None else False
        os.environ['DJANGO_LIVE_TEST_SERVER_ADDRESS'] = settings.DJANGO_LIVE_TEST_SERVER_ADDRESS

    def setup_databases(self, **kwargs):
        if self.no_db:
            pass
        else:
            return super(AcTestRunner, self).setup_databases(**kwargs)

    def teardown_databases(self, old_config, **kwargs):
        if self.no_db:
            pass
        else:
            return super(AcTestRunner, self).teardown_databases(old_config, **kwargs)

    @classmethod
    def add_arguments(cls, parser):
        super(AcTestRunner, cls).add_arguments(parser)

        parser.add_argument('-n', '--no-db', action='store_true', dest='no_db', default=False,
                            help='Do not use DB for testing')
