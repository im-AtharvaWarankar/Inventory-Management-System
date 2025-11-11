from django.urls import path
from .views import LowStockAlertsView


urlpatterns = [
    path('api/companies/<int:company_id>/alerts/low-stock', LowStockAlertsView.as_view(), name='low-stock-alerts'),
]
