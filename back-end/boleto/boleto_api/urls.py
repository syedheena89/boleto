from django.urls import path
from .views import *
urlpatterns = [
     path("user/signup",SignupView.as_view(),name='sign-up'),
    path("user/login",SigninView.as_view(),name='sign-in'),
]