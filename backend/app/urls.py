from django.contrib import admin
from django.urls import path
from amo.views.AirportView import AirportView
from amo.views.MockAirlinesView import MockAirlinesView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('airports/', AirportView.as_view(), name='airports'),
    path('search/', MockAirlinesView.as_view(), name='flight-search'),
]
