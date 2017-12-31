# coding: utf-8

import json
from django.db import IntegrityError
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from rest_framework import viewsets, generics, exceptions
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView as _APIView
from rest_framework.response import Response

from ac_api import serializers_request
from ac_common.drf import AllecenaTokenAuth
from ac_common.models import TaskScheduler, Category, User
from ac_common.utils import reverse_key_val_choice_from_tuple, send_mail, create_token

from ac_common.loggers import api_logger, stat_logger
from ac_api.serializers import CategorySerializer, TriggerSerializer, TriggerListSerializer, \
    ResultListSerializer, PollingSerializer
from ac_engine.models import Results, Triggers
from ac_engine.tasks import ComputingTask


class NoAuthMixin(object):
    authentication_classes = ()
    permission_classes = (AllowAny,)


class AbstractAPIView(_APIView):
    """
    Base class for future use.
    authentication_classes and permission_classes defaulting to settings
    """
    pass


class IndexApi(NoAuthMixin, AbstractAPIView):
    def get(self, request):
        return Response({'version': settings.VERSION})

    post = get
    put = get
    delete = get
    options = get


class CategoryView(generics.ListAPIView):
    model = Category
    serializer_class = CategorySerializer
    authentication_classes = ()
    permission_classes = ()

    def get_queryset(self):
        category_name = self.kwargs['categoryName']
        if len(category_name) < 2:
            return Category.objects.none()
        return Category.objects.filter(name__icontains=category_name)


class ComputingComputeApi(AbstractAPIView):
    def post(self, request):
        api_logger.info('ComputingComputeApi', extra={'data': request.data})
        serializer = serializers_request.ComputingComputeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        stat_logger.info('Running: %s @ %s' % (serializer.validated_data['actions'], serializer.validated_data['sources']))

        task = ComputingTask().delay(input_data=serializer.validated_data, user_id=request.user.id)
        return Response({'computingHash': task.task_id})


class ComputingPollingApi(AbstractAPIView):
    def post(self, request):
        api_logger.info('ComputingPollingApi', extra={'data': request.data})

        serializer = serializers_request.ComputingPollingApiSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result = Results.objects.get(user=request.user.id, computing_hash=serializer.validated_data['computingHash'])
        except ObjectDoesNotExist:
            return Response(status=204)

        if result.error:
            return Response(status=500)

        return Response(PollingSerializer(result).data)


class UserLoginApi(NoAuthMixin, AbstractAPIView):

    def post(self, request, **kwargs):

        if kwargs.get('source', None) == 'facebook':
            serializer = serializers_request.FacebookAuthenticationSerializer(data=request.data)
        else:
            serializer = serializers_request.AllecenaAuthenticationSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        user = authenticate(email=serializer.validated_data['username'], password=serializer.validated_data['password'])

        if user is None:
            return Response(status=401)

        date, token = create_token(user.email)

        user.auth_token = token
        user.auth_expiry_date = date
        user.save(force_update=True)

        return Response({
            'token': token,
            'accounts': {
                'allegro': {
                    'id': user.allegro_user_id,
                    'name': user.allegro_user_name
                },
                'ebay': {
                    'id': user.ebay_user_id,
                    'name': user.ebay_user_name
                }
            },
            'user': {
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        })


class UserLogoutApi(NoAuthMixin, AbstractAPIView):
    def get(self, request):
        try:
            user = AllecenaTokenAuth().authenticate(request)[0]
            user.auth_token = ''
            user.save()
        except exceptions.AuthenticationFailed:
            pass

        return Response(status=200)


class UserRegisterApi(NoAuthMixin, AbstractAPIView):
    def post(self, request):
        serializer = serializers_request.UserCreationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            User.objects.create_user(serializer.validated_data['email'], serializer.validated_data['new_password'])
        except IntegrityError:
            return Response(status=409)

        return Response(status=200)


class UserPasswordResetApi(NoAuthMixin, AbstractAPIView):
    def post(self, request):
        serializer = serializers_request.UserPasswordResetEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = User.objects.get(email=serializer.validated_data['email'])
        except User.DoesNotExist:
            return Response(status=400)

        current_site = get_current_site(request._request)
        site_name = current_site.name
        domain = current_site.domain

        token_expiry, token = create_token(user.email)

        context = {
            'email': user.email,
            'domain': domain,
            'site_name': site_name,
            'uid': urlsafe_base64_encode(force_bytes(user.id)),
            'user_id': user.id,
            'token': token,
            'protocol': 'http'
        }

        user.reset_token = token
        user.reset_token_expiry_date = token_expiry
        user.save()

        send_mail("AlleCena password reset", 'email_password_reset.html', user.email, context)

        return Response(status=200)


class UserPasswordResetUrlApi(NoAuthMixin, AbstractAPIView):
    def post(self, request, uidb64=None, token=None):
        serializer = serializers_request.UserPasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=uid, reset_token=token, reset_token_expiry_date__gt=timezone.now())
        except (StandardError, User.DoesNotExist):
            return Response(status=401)

        user.set_password(serializer.validated_data['new_password'])
        user.reset_token_expiry_date = None
        user.reset_token = None
        user.save()

        return Response(status=200)


class UserPasswordChangeApi(AbstractAPIView):
    def post(self, request):
        serializer = serializers_request.UserPasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save(force_update=True)

        return Response(status=200)


class UserResultsApi(viewsets.ReadOnlyModelViewSet):
    queryset = Results.objects.select_related('category').all()
    serializer_class = ResultListSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response(json.loads(instance.json_dump))

    def get_queryset(self):
        return super(UserResultsApi, self).get_queryset().filter(user=self.request.user)


class UserTriggersApi(AbstractAPIView):
    def get(self, request, *args, **kwargs):
        api_logger.info('UserTriggersApi get', extra={'kwargs': kwargs})
        if kwargs.get('trigger_id'):
            try:
                result = Triggers.objects.get(pk=kwargs['trigger_id'])
                return Response(TriggerSerializer(result).data)

            except Triggers.DoesNotExist:
                raise exceptions.NotFound()
        else:
            results = Triggers.objects.filter(user=request.user.id, error=False)
            return Response({'triggers': TriggerListSerializer(results, many=True).data})

    def post(self, request, *args, **kwargs):
        api_logger.info('UserTriggersApi post', extra={'data': request.data})

        serializer = serializers_request.UserTriggersSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        api_logger.info('Adding Trigger for user ID %d' % request.user.id)

        trigger = Triggers()
        trigger.user = request.user
        trigger.auction_id = data['auction_id']
        trigger.time = reverse_key_val_choice_from_tuple(Triggers.TIMES, data['time'])
        trigger.mode = reverse_key_val_choice_from_tuple(Triggers.MODES, data['mode'])
        trigger.mode_value = data['mode_value']
        trigger.provider = reverse_key_val_choice_from_tuple(settings.PROVIDERS, data['provider'])
        trigger.save()

        TaskScheduler.schedule('ac_engine.tasks.TriggerTask', minutes=trigger.task_interval,
                               task_name=trigger.task_name, kwargs=json.dumps({'trigger_id': trigger.id}))

        return Response({'triggerId': trigger.id}, 201)

    def delete(self, request, *args, **kwargs):
        api_logger.info('UserTriggersApi delete', extra={'kwargs': kwargs})
        if 'trigger_id' not in kwargs:
            raise exceptions.NotFound()
        TaskScheduler.terminate_by_task_name(Triggers.objects.get(id=kwargs.get('trigger_id')).task_name)
        Triggers.objects.filter(id=kwargs.get('trigger_id')).delete()
        return Response(status=200)


class UserAuctionsApi(AbstractAPIView):
    def get(self, request):
        api_logger.info('UserAuctionsApi called', extra={'user_id': request.user.id})
        auctions = []
        if request.user.allegro_user_name:
            from ac_engine_allegro.data.data_grabber import DataGrabber as Allegro
            from ac_engine_ebay.data.data_grabber import DataGrabber as Ebay
            a = Allegro()
            auctions = a.get_user_auctions(request.user.allegro_user_name)
        return Response(auctions)


class UserDataApi(AbstractAPIView):
    def put(self, request):
        api_logger.info('UserDataApi', extra={'data': request.data})

        serializer = serializers_request.UserDataSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        for f in ('first_name', 'last_name'):
            if data[f]:
                setattr(request.user, f, data[f])

        if data['allegro_login']:
            from ac_engine_allegro.data.data_grabber import DataGrabber
            request.user.allegro_user_name = data["allegro_login"]
            request.user.allegro_user_id = DataGrabber().get_user_id(data["allegro_login"], fresh=True)

        if data['ebay_login']:
            request.user.ebay_user_name = data["ebay_login"]
            request.user.ebay_user_id = 1  # TODO ebay

        request.user.save()
        return Response(status=200)
