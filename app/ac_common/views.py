# coding: utf-8

from django.http import JsonResponse
from django.shortcuts import render_to_response
from django.template import RequestContext


def handler404(request):
    if request.is_ajax():
        response = JsonResponse({'error': 'Endpoint doesnt exist'})
    else:
        response = render_to_response('errors/404.html', {}, context_instance=RequestContext(request))
    response.status_code = 404
    return response


def handler500(request):
    if request.is_ajax():
        response = JsonResponse({'error': 'Endpoint doesnt exist'})
    else:
        response = render_to_response('errors/500.html', {}, context_instance=RequestContext(request))
    response.status_code = 500
    return response
