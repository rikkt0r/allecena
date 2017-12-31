# coding: utf-8

from django.core.management import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    def handle(self, *args, **options):
        from suds.client import Client

        c = Client('https://webapi.allegro.pl/service.php?wsdl')
        countries = c.service.doGetCountries(countryCode=1, webapiKey=settings.ALLEGRO_KEY)
        for ct in countries.item:
            print("ID: %d Name: %s" % (ct.countryId, ct.countryName))
