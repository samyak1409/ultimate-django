from django.urls import path
from . import views


# URLConf:
urlpatterns = [
    path("home/", views.home),
    path("test-mail/", views.test_mail),
    path("test-celery/", views.test_celery),
    path("test-cache1/", views.test_cache1),
    path("test-cache2/", views.test_cache2),
    path("test-cache3/", views.TestCache3.as_view()),
]
