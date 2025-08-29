from django.urls import path
from . import views


# URLConf:
urlpatterns = [
    path("home/", views.home),
    path("test-mail/", views.test_mail),
    path("test-celery/", views.test_celery),
]
