from practice import views
from django.urls import include, path

urlpatterns = [
    path('', views.main),
    path('link', views.link),
    path('input', views.input),
    path('status', views.status),
    path('drop', views.drop),
    path('extract', views.extract),
    path('crawl', views.crawl),
    path('getnodelist', views.getnodelist),
    path('evaluategraph', views.evaluategraph),
]

