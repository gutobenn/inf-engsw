from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from django.conf.urls import include

from . import views
from .views import ItemView

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^favicon.ico$',
        RedirectView.as_view(
            url=staticfiles_storage.url('favicon.ico'), permanent=False),
        name="favicon"),
    url(r'^items/$', views.items_my, name='items_my'),
    url(r'^items/new/$', views.item_new, name='item_new'),
    url(r'^items/(?P<pk>[0-9]+)/$', views.item_detail, name='item_detail'),
    url(r'^items/(?P<pk>[0-9]+)/edit/$', views.item_edit, name='item_edit'),
    url(r'^rents/$', views.rents, name='rents'),
    url(r'^rents/(?P<pk>[0-9]+)/cancel/$',
        views.rent_cancel,
        name='rent_cancel'),
    url(r'^rents/(?P<pk>[0-9]+)/accept/$',
        views.rent_accept,
        name='rent_accept'),
    url(r'^rents/(?P<pk>[0-9]+)/reject/$',
        views.rent_reject,
        name='rent_reject'),
    url(r'^search', ItemView.as_view(), name="search"),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': 'index'},
        name='logout'),
    url(r'^ratings/', include('star_ratings.urls', namespace='ratings', app_name='ratings')),
]
