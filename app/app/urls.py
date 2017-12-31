from django.conf.urls import include, url
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='index'),
    url(r'^api/', include('ac_api.urls', namespace='api')),
    url(r'^docs/', include('ac_docs.urls', namespace='docs')),
]

handler404 = "ac_common.views.handler404"
handler500 = "ac_common.views.handler500"
