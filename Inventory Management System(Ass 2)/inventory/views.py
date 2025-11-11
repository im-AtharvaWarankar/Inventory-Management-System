from datetime import timedelta
from decimal import Decimal

from django.db import DatabaseError
from django.db.models import Sum
from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .models import (
    Company, Warehouse, Product, Inventory, Sale, ProductSupplier, Supplier, BundleComponent
)
from .serializers import LowStockAlertsResponseSerializer


class LowStockAlertsView(APIView):
   

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, company_id: int):
        try:
            window_days = int(request.query_params.get("days", "30"))
            if window_days <= 0:
                window_days = 30
        except ValueError:
            window_days = 30

        window_start = now() - timedelta(days=window_days)

        company = Company.objects.filter(id=company_id).first()
        if not company:
            return Response({"detail": "Company not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            def get(self, request, company_id: int):
                try:
                    window_days = int(request.query_params.get("days", "30"))
                    if window_days <= 0:
                        window_days = 30
                except ValueError:
                    window_days = 30

                window_start = now() - timedelta(days=window_days)

                company = Company.objects.filter(id=company_id).first()
                if not company:
                    return Response({"detail": "Company not found"}, status=status.HTTP_404_NOT_FOUND)

                try:
                    recent_sales = (
                        Sale.objects
                        .filter(company_id=company_id, sale_date__gte=window_start)
                        .values("product_id", "warehouse_id")
                        .annotate(total_sold=Sum("quantity_sold"))
                    )

                    sales_map = {}
                    for rs in recent_sales:
                        key = (rs["product_id"], rs["warehouse_id"])
                        sales_map[key] = rs["total_sold"] or 0

                    low_stock_candidates = (
                        Inventory.objects
                        .filter(company_id=company_id)
                        .select_related("product", "warehouse")
                    )

                    alerts = []

                    def supplier_info_for_product(product: Product):
                        if product.supplier_id:
                            sup = Supplier.objects.filter(id=product.supplier_id).first()
                            if sup:
                                return {"id": sup.id, "name": sup.name, "contact_email": sup.contact_email}
                        ps = ProductSupplier.objects.filter(product_id=product.id).select_related("supplier").first()
                        if ps and ps.supplier:
                            return {"id": ps.supplier.id, "name": ps.supplier.name, "contact_email": ps.supplier.contact_email}
                        return {"id": None, "name": None, "contact_email": None}

                    for inv in low_stock_candidates:
                        product = inv.product
                        warehouse = inv.warehouse

                        if product.company_id != company_id or warehouse.company_id != company_id:
                            continue

                        if not product.active or not warehouse.active:
                            continue

                        total_sold = sales_map.get((product.id, warehouse.id), 0)
                        if total_sold <= 0:
                            continue

                        current_stock = inv.quantity_on_hand
                        threshold = product.threshold

                        if current_stock >= threshold:
                            continue

                        avg_daily = Decimal(total_sold) / Decimal(window_days)
                        days_until = int(Decimal(current_stock) / avg_daily) if avg_daily > 0 else None

                        alerts.append({
                            "product_id": product.id,
                            "product_name": product.name,
                            "sku": product.sku,
                            "warehouse_id": warehouse.id,
                            "warehouse_name": warehouse.name,
                            "current_stock": int(current_stock),
                            "threshold": int(threshold),
                            "days_until_stockout": days_until,
                            "supplier": supplier_info_for_product(product)
                        })

                    bundle_products = (
                        Product.objects.filter(company_id=company_id, is_bundle=True, active=True)
                    )
                    for bp in bundle_products:
                        comps = BundleComponent.objects.filter(company_id=company_id, bundle_product_id=bp.id)
                        if not comps.exists():
                            continue

                        warehouses = Warehouse.objects.filter(company_id=company_id, active=True)
                        for wh in warehouses:
                            total_sold = sales_map.get((bp.id, wh.id), 0)
                            if total_sold <= 0:
                                continue

                            component_limits = []
                            for comp in comps:
                                inv = Inventory.objects.filter(company_id=company_id, warehouse_id=wh.id, product_id=comp.component_product_id).first()
                                qty_on_hand = inv.quantity_on_hand if inv else 0
                                if comp.quantity_per_bundle > 0:
                                    component_limits.append(int(Decimal(qty_on_hand) / Decimal(comp.quantity_per_bundle)))
                                else:
                                    component_limits.append(0)

                            if not component_limits:
                                continue

                            bundle_stock = min(component_limits)
                            threshold = bp.threshold

                            if bundle_stock >= threshold:
                                continue

                            avg_daily = Decimal(total_sold) / Decimal(window_days)
                            days_until = int(Decimal(bundle_stock) / avg_daily) if avg_daily > 0 else None

                            alerts.append({
                                "product_id": bp.id,
                                "product_name": bp.name,
                                "sku": bp.sku,
                                "warehouse_id": wh.id,
                                "warehouse_name": wh.name,
                                "current_stock": int(bundle_stock),
                                "threshold": int(threshold),
                                "days_until_stockout": days_until,
                                "supplier": supplier_info_for_product(bp)
                            })

                    alerts.sort(key=lambda a: (a["warehouse_id"], a["product_id"]))

                    resp = {"alerts": alerts, "total_alerts": len(alerts)}
                    ser = LowStockAlertsResponseSerializer(data=resp)
                    ser.is_valid(raise_exception=True)
                    return Response(ser.data, status=status.HTTP_200_OK)
                except DatabaseError:
                    return Response({"detail": "Database error while processing request"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({"detail": "Database error while processing request"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
