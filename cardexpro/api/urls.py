from django.urls import path, include

urlpatterns = [
    path('auth/', include(('cardexpro.authentication.urls', 'auth')))
]
