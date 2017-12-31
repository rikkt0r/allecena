# coding: utf-8
from django.conf import settings
from rest_framework import serializers

from ac_common.models import Category
from ac_engine.models import Triggers, Results, TriggerValues


class UserAuctionsSerializer(serializers.Serializer):
    class AuctionSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        name = serializers.CharField()
        categoryId = serializers.IntegerField()
        categoryName = serializers.CharField()
        url = serializers.CharField()

    allegroAuctions = AuctionSerializer(many=True)
    ebayAuctions = AuctionSerializer(many=True, allow_null=True, required=False)


class TriggerValueSerializer(serializers.ModelSerializer):
    time = serializers.DateTimeField(format='%Y-%m-%d %H:%M', source='date_created')
    value = serializers.FloatField()

    class Meta:
        model = TriggerValues
        fields = ('time', 'value')


class TriggerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Triggers
        fields = ('id', 'name', 'mode', 'mode_value', 'finished', 'provider', 'date_created', 'date_finished', 'mode', 'time', 'data')

    provider = serializers.SerializerMethodField()
    date_created = serializers.DateTimeField(format='%Y-%m-%d %H:%M')
    date_finished = serializers.DateTimeField(format='%Y-%m-%d %H:%M')
    data = TriggerValueSerializer(many=True, source='trigger_values', read_only=True)

    def get_provider(self, obj):
        return obj.get_provider_display()


class TriggerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Triggers
        fields = ('id', 'name', 'mode', 'mode_value', 'finished', 'provider', 'date_created', 'date_finished')

    provider = serializers.SerializerMethodField()
    date_created = serializers.DateTimeField(format='%Y-%m-%d %H:%M')
    date_finished = serializers.DateTimeField(format='%Y-%m-%d %H:%M')

    def get_provider(self, obj):
        return obj.get_provider_display()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'parent_name')


class ResultListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Results
        fields = ('id', 'name', 'advanced', 'provider', 'statistics', 'hint', 'prediction', 'histogram', 'trends', 'category', 'date_created')

    category = serializers.SerializerMethodField()
    provider = serializers.SerializerMethodField()
    date_created = serializers.DateTimeField(format='%Y-%m-%d %H:%M')

    def get_category(self, obj):
        if obj.category.parent_name:
            return '%s > %s' % (obj.category.parent_name, obj.category.name)
        return obj.category.name

    def get_provider(self, obj):
        return obj.get_provider_display()


class PollingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Results
        fields = ('id', 'name', 'provider', 'modes')

    provider = serializers.SerializerMethodField()
    modes = serializers.SerializerMethodField()

    def get_provider(self, obj):
        return obj.get_provider_display()

    def get_modes(self, obj):
        modes = []
        for mode in Results.MODES:
            if getattr(obj, mode, False):
                modes.append(mode)
        return modes
