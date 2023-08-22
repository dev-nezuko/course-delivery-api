from django.urls import path
from django.urls import include, path
from . import views

urlpatterns = [
  path('signin', views.signin, name='signin'),
  path('greeting', views.greetingendpoint, name='greetingendpoint'),
  path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
]