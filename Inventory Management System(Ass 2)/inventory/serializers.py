from rest_framework import serializers


class SupplierInfoSerializer(serializers.Serializer):
    id = serializers.IntegerField(allow_null=True)
    name = serializers.CharField(allow_blank=True, allow_null=True)
    contact_email = serializers.CharField(allow_null=True)


class LowStockAlertSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    product_name = serializers.CharField()
    sku = serializers.CharField()
    warehouse_id = serializers.IntegerField()
    warehouse_name = serializers.CharField()
    current_stock = serializers.IntegerField()
    threshold = serializers.IntegerField()
    days_until_stockout = serializers.IntegerField(allow_null=True)
    supplier = SupplierInfoSerializer()


class LowStockAlertsResponseSerializer(serializers.Serializer):
    alerts = LowStockAlertSerializer(many=True)
    total_alerts = serializers.IntegerField()
