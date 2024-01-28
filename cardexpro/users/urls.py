from django.urls import path
from cardexpro.users import apis

urlpatterns = [
    path('register/', apis.RegisterApi.as_view(), name="register"),
    path('activities/', apis.ActivitiesApi.as_view(), name="activities"),
]
