from django.urls import path, include

urlpatterns = [
    path('auth/', include(('cardexpro.authentication.urls', 'auth'))),
    path('users/', include(('cardexpro.users.urls', 'users'))),
]
