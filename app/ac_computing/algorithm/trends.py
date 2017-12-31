# coding: utf-8
from datetime import datetime
from django.conf import settings


class Trends(object):

    def __init__(self, offers):
        self.offers = offers

    def calculate(self):

        from collections import OrderedDict

        daily_offers = {}

        dates = []
        meanPrices = []
        amountSold = []

        for offer in self.offers:
            date = datetime.fromtimestamp(int(offer.endingDate))
            date_formatted = date.strftime('%Y-%m-%d')

            if (datetime.now() - date).total_seconds() < settings.TRENDS_INTERVAL:
                if date_formatted in daily_offers:
                    daily_offers[date_formatted].append(offer)
                else:
                    daily_offers[date_formatted] = [offer]

        daily_offers = OrderedDict(sorted(daily_offers.iteritems(), key=lambda x: x[0]))
                
        for date in daily_offers:
            dates.append(date)
            
            price_sum = 0.0
            amount = 0
            
            for offer in daily_offers[date]:
                price_sum = price_sum + offer.price
                amount = amount + (offer.amountStart - offer.amountLeft)
                
            meanPrices.append(price_sum / len(daily_offers[date]))
            amountSold.append(amount)

        return {
            'dates': dates,
            'meanPrices': meanPrices,
            'amountSold': amountSold
        }
