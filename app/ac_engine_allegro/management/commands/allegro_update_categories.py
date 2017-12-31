# coding: utf-8
from django.conf import settings
from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        from ac_engine_allegro.data.data_grabber import DataGrabber as AllegroDataGrabber
        from ac_common.models import Category

        ald = AllegroDataGrabber()

        Category.objects.all().delete()
        cats = ald.get_categories()
        print('Categories found: %d' % len(cats))
        error_counter = 0

        for cat in cats:
            try:
                c = Category(
                    id=cat['id'],
                    name=unicode(cat['name']),
                    parent_id=cat['parent_id'],
                    parent_name=unicode(cat['parent_name']),
                    provider=settings.PROVIDER_ALLEGRO
                )
                c.save()

            except Exception as e:
                error_counter += 1
                print(e)

        print('Errors occurred %d' % error_counter)
