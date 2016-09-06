from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

import hello.views

# Examples:
# url(r'^$', 'gettingstarted.views.home', name='home'),
# url(r'^blog/', include('blog.urls')),

urlpatterns = [
    url(r'^$', hello.views.index, name='index'),
    url(r'^tree/1', hello.views.showTree1, name='showTree1'),
    url(r'^tree/2', hello.views.showTree2, name='showTree2'),
    url(r'^tree/3', hello.views.showTree3, name='showTree3'),
    url(r'^tree/4', hello.views.showTree4, name='showTree4'),
    url(r'^data', hello.views.showData, name='showData'),
    url(r'^real-data', hello.views.showDataLive, name='showDataLive'),
    url(r'^db', hello.views.db, name='db'),
    url(r'^admin/', include(admin.site.urls)),
]
