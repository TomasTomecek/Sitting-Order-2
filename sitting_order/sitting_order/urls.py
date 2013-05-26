from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from sit.views import IndexView, AjaxView, AjaxAllView

urlpatterns = patterns('',
    # Examples:
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^ajax/$', AjaxView.as_view(), name='ajax'),
    url(r'^ajax/all/$', AjaxAllView.as_view(), name='ajax/all'),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
