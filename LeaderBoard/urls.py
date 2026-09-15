from django.urls import path, include

urlpatterns = [
    path('', include('LeaderBoard.api.urls')),
]