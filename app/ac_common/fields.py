# coding: utf-8
import base64
import binascii
from rest_framework import serializers, exceptions


class Base64SerializerField(serializers.CharField):
    def to_internal_value(self, val):
        value = super(Base64SerializerField, self).to_internal_value(val)
        try:
            return base64.b64decode(value)
        except binascii.Error:
            raise exceptions.ValidationError('Invalid base64 value: %s' % value, code='INVALID_BASE64')


class FacebookTokenSerializerField(serializers.RegexField):

    def __init__(self, **kwargs):
        super(FacebookTokenSerializerField, self).__init__(r'^[\w\d]{1,255}$', **kwargs)
