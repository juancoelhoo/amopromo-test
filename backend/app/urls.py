from django.contrib import admin
from django.urls import path
from amo.views.views import AirportView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('airports/', AirportView.as_view(), name='airports'),
]
