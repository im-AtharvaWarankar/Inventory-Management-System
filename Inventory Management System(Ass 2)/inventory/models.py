from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "companies"
        managed = False


class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_email = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=64, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "suppliers"
        managed = False


class Warehouse(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, null=True, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "warehouses"
        managed = False
        unique_together = ("company", "name")


class Product(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    sku = models.CharField(max_length=64)
    name = models.CharField(max_length=255)
    is_bundle = models.BooleanField(default=False)
    threshold = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "products"
        managed = False
        unique_together = ("company", "sku")


class ProductSupplier(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)

    class Meta:
        db_table = "product_suppliers"
        managed = False
        unique_together = ("company", "product", "supplier")


class BundleComponent(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    bundle_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="bundle_components")
    component_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="component_of_bundles")
    quantity_per_bundle = models.DecimalField(max_digits=18, decimal_places=4)

    class Meta:
        db_table = "bundle_components"
        managed = False
        unique_together = ("company", "bundle_product", "component_product")


class Inventory(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_on_hand = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "inventory"
        managed = False
        unique_together = ("warehouse", "product")
        indexes = [
            models.Index(fields=["company", "product"], name="idx_inventory_company_product"),
            models.Index(fields=["company", "warehouse"], name="idx_inventory_company_warehouse"),
        ]


class InventoryTransaction(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    change_qty = models.IntegerField()
    change_type = models.CharField(max_length=32)
    reference = models.CharField(max_length=255, null=True, blank=True)
    occurred_at = models.DateTimeField()

    class Meta:
        db_table = "inventory_transactions"
        managed = False
        indexes = [
            models.Index(fields=["company", "product", "occurred_at"], name="idx_tx_company_product_date"),
            models.Index(fields=["company", "warehouse", "occurred_at"], name="idx_tx_company_warehouse_date"),
        ]


class Sale(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_sold = models.IntegerField()
    sale_date = models.DateTimeField()

    class Meta:
        db_table = "sales"
        managed = False
        indexes = [
            models.Index(fields=["company", "product", "sale_date"], name="idx_sales_company_product_date"),
            models.Index(fields=["company", "warehouse", "sale_date"], name="idx_sales_company_warehouse_date"),
        ]
