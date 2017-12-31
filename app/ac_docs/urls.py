# coding: utf-8
from django.conf.urls import url
from django.shortcuts import render


def view(request, template=None):
    if not template:
        template = 'index'
    return render(request, 'ac_docs/%s.html' % template)

urlpatterns = [
    url(r'^(?:(?P<template>\w+)/)?$', view, name='doc'),
]
