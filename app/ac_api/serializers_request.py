# coding: utf-8
from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ac_common.fields import Base64SerializerField, FacebookTokenSerializerField


class ComputingComputeSerializer(serializers.Serializer):

    class DataSerializer(serializers.Serializer):

        class ItemSerializer(serializers.Serializer):
            name = serializers.CharField()
            guarantee = serializers.BooleanField()
            used = serializers.BooleanField()
            category_id = serializers.IntegerField()
            product_id = serializers.IntegerField()

        class AccountSerializer(serializers.Serializer):
            allegro = serializers.CharField(required=False, allow_blank=True)
            ebay = serializers.CharField(required=False, allow_blank=True)

        class AnalysisSerializer(serializers.Serializer):
            advanced = serializers.BooleanField()

        auction = serializers.CharField(required=False, allow_blank=True)
        item = ItemSerializer()
        account = AccountSerializer()
        analysis = AnalysisSerializer()
        countries = serializers.ListField(child=serializers.CharField())

    actions = serializers.MultipleChoiceField(choices=('hint', 'prediction', 'statistics', 'histogram', 'trends'))
    sources = serializers.MultipleChoiceField(choices=('allegro', 'ebay'))
    data = DataSerializer()

    def validate(self, attrs):
        data = super(ComputingComputeSerializer, self).validate(attrs)
        if not data['data']['analysis']['advanced'] and 'trends' in data['actions']:
            raise ValidationError('Trends analysis only for advanced mode')
        # Instead of custom encoder for celery..
        data['actions'] = list(data['actions'])
        data['sources'] = list(data['sources'])
        return data


class ComputingPollingApiSerializer(serializers.Serializer):
    computingHash = serializers.CharField()


class UserDataSerializer(serializers.Serializer):
    allegro_login = serializers.CharField(required=False, allow_blank=True)
    ebay_login = serializers.CharField(required=False, allow_blank=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)


class UserTriggersSerializer(serializers.Serializer):
    auction_id = serializers.IntegerField()
    provider = serializers.ChoiceField(choices=settings.PROVIDERS_KEYS)
    mode_value = serializers.IntegerField()
    mode = serializers.CharField()  # ---> ChoiceField ?
    time = serializers.CharField()  # ---> ChoiceField ?


class UserPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=settings.AUTH_USERNAME_MAX_LENGTH)


class BasePasswordSerializer(serializers.Serializer):
    new_password = Base64SerializerField(min_length=settings.AUTH_PASSWORD_MIN_LENGTH)
    new_password_repeat = Base64SerializerField(min_length=settings.AUTH_PASSWORD_MIN_LENGTH)

    def validate(self, attrs):
        if attrs.get('new_password') != attrs.get('new_password_repeat'):
            raise ValidationError('Passwords are not equal', code='password_mismatch')
        return attrs


class UserPasswordChangeSerializer(BasePasswordSerializer):
    pass


class UserCreationSerializer(BasePasswordSerializer):
    email = serializers.EmailField(max_length=settings.AUTH_USERNAME_MAX_LENGTH)


class AllecenaAuthenticationSerializer(serializers.Serializer):
    username = serializers.EmailField(max_length=settings.AUTH_USERNAME_MAX_LENGTH)
    password = Base64SerializerField(min_length=settings.AUTH_PASSWORD_MIN_LENGTH)


class FacebookAuthenticationSerializer(serializers.Serializer):
    username = serializers.EmailField(max_length=settings.AUTH_USERNAME_MAX_LENGTH)
    password = FacebookTokenSerializerField()
