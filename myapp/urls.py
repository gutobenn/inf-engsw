from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views

from . import views
from myapp.views import ItemView

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^items/$', views.items, name='items'),
    url(r'^items/new/$', views.item_new, name='item_new'),
    url(r'^items/(?P<pk>[0-9]+)/$', views.item_detail, name='item_detail'),
    url(r'^items/(?P<pk>[0-9]+)/edit/$', views.item_edit, name='item_edit'),
    url(r'^search', ItemView.as_view(), name="search"),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': 'index'}, name='logout'),
    url(r'^admin/', admin.site.urls),
]
