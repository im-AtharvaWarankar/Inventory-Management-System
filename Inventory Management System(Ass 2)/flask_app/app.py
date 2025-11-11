import os
from datetime import datetime, timedelta
from decimal import Decimal

from flask import Flask, jsonify
from flask import request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

# Use DATABASE_URL if provided, else default to an in-memory sqlite for demo purposes.
db_url = os.getenv("DATABASE_URL")
if not db_url:
    db_url = "sqlite:///:memory:"
app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# SQLAlchemy models mirroring the PostgreSQL schema
class Company(db.Model):
    __tablename__ = "companies"
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(255), nullable=False)


class Supplier(db.Model):
    __tablename__ = "suppliers"
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    contact_email = db.Column(db.String(255))


class Warehouse(db.Model):
    __tablename__ = "warehouses"
    id = db.Column(db.BigInteger, primary_key=True)
    company_id = db.Column(db.BigInteger, db.ForeignKey("companies.id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255))
    active = db.Column(db.Boolean, default=True, nullable=False)


class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.BigInteger, primary_key=True)
    company_id = db.Column(db.BigInteger, db.ForeignKey("companies.id"), nullable=False)
    supplier_id = db.Column(db.BigInteger, db.ForeignKey("suppliers.id"))
    sku = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    is_bundle = db.Column(db.Boolean, default=False, nullable=False)
    threshold = db.Column(db.Integer, default=0, nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)


class ProductSupplier(db.Model):
    __tablename__ = "product_suppliers"
    company_id = db.Column(db.BigInteger, primary_key=True)
    product_id = db.Column(db.BigInteger, primary_key=True)
    supplier_id = db.Column(db.BigInteger, primary_key=True)


class BundleComponent(db.Model):
    __tablename__ = "bundle_components"
    company_id = db.Column(db.BigInteger, primary_key=True)
    bundle_product_id = db.Column(db.BigInteger, primary_key=True)
    component_product_id = db.Column(db.BigInteger, primary_key=True)
    quantity_per_bundle = db.Column(db.Numeric(18, 4), nullable=False)


class Inventory(db.Model):
    __tablename__ = "inventory"
    id = db.Column(db.BigInteger, primary_key=True)
    company_id = db.Column(db.BigInteger, nullable=False)
    warehouse_id = db.Column(db.BigInteger, nullable=False)
    product_id = db.Column(db.BigInteger, nullable=False)
    quantity_on_hand = db.Column(db.Integer, default=0, nullable=False)


class InventoryTransaction(db.Model):
    __tablename__ = "inventory_transactions"
    id = db.Column(db.BigInteger, primary_key=True)
    company_id = db.Column(db.BigInteger, nullable=False)
    warehouse_id = db.Column(db.BigInteger, nullable=False)
    product_id = db.Column(db.BigInteger, nullable=False)
    change_qty = db.Column(db.Integer, nullable=False)
    change_type = db.Column(db.String(32), nullable=False)
    reference = db.Column(db.String(255))
    occurred_at = db.Column(db.DateTime, nullable=False)


class Sale(db.Model):
    __tablename__ = "sales"
    id = db.Column(db.BigInteger, primary_key=True)
    company_id = db.Column(db.BigInteger, nullable=False)
    warehouse_id = db.Column(db.BigInteger, nullable=False)
    product_id = db.Column(db.BigInteger, nullable=False)
    quantity_sold = db.Column(db.Integer, nullable=False)
    sale_date = db.Column(db.DateTime, nullable=False)


def seed_demo_data():
    # Seed only if using sqlite memory DB
    if not db_url.startswith("sqlite"):
        return
    db.create_all()

    c = Company(id=1, name="Demo Co")
    s = Supplier(id=1, name="Supplier Corp", contact_email="orders@supplier.com")
    w = Warehouse(id=1, company_id=1, name="Main Warehouse", active=True)
    p1 = Product(id=101, company_id=1, supplier_id=1, sku="WID-001", name="Widget A", threshold=20, active=True)
    p2 = Product(id=102, company_id=1, supplier_id=1, sku="BUNDLE-01", name="Bundle Pack", is_bundle=True, threshold=5, active=True)

    db.session.add_all([c, s, w, p1, p2])
    db.session.commit()

    db.session.add(Inventory(company_id=1, warehouse_id=1, product_id=101, quantity_on_hand=5))
    db.session.add(Inventory(company_id=1, warehouse_id=1, product_id=102, quantity_on_hand=0))
    db.session.commit()

    # Sales in last 30 days
    now_dt = datetime.utcnow()
    for d in range(1, 6):
        db.session.add(Sale(company_id=1, warehouse_id=1, product_id=101, quantity_sold=2, sale_date=now_dt - timedelta(days=d)))
    db.session.commit()


@app.route("/api/companies/<int:company_id>/alerts/low-stock", methods=["GET"])
def low_stock_alerts(company_id: int):
    try:
        window_days = int(request.args.get("days", "30"))
        if window_days <= 0:
            window_days = 30
    except ValueError:
        window_days = 30

    window_start = datetime.utcnow() - timedelta(days=window_days)

    company = db.session.get(Company, company_id)
    if not company:
        return jsonify({"detail": "Company not found"}), 404

    # Recent sales totals per product+warehouse
    rs = (
        db.session.query(Sale.product_id, Sale.warehouse_id, db.func.sum(Sale.quantity_sold).label("total_sold"))
        .filter(Sale.company_id == company_id, Sale.sale_date >= window_start)
        .group_by(Sale.product_id, Sale.warehouse_id)
        .all()
    )
    sales_map = {(r.product_id, r.warehouse_id): int(r.total_sold or 0) for r in rs}

    alerts = []

    # Simple products
    inv_rows = (
        db.session.query(Inventory, Product, Warehouse)
        .join(Product, Product.id == Inventory.product_id)
        .join(Warehouse, Warehouse.id == Inventory.warehouse_id)
        .filter(Inventory.company_id == company_id, Product.active == True, Warehouse.active == True, Product.is_bundle == False)
        .all()
    )
    for inv, product, warehouse in inv_rows:
        total_sold = sales_map.get((product.id, warehouse.id), 0)
        if total_sold <= 0:
            continue
        if inv.quantity_on_hand >= product.threshold:
            continue
        avg_daily = Decimal(total_sold) / Decimal(window_days)
        days_until = int(Decimal(inv.quantity_on_hand) / avg_daily) if avg_daily > 0 else None

        sup = db.session.get(Supplier, product.supplier_id) if product.supplier_id else None
        supplier_info = {
            "id": sup.id if sup else None,
            "name": sup.name if sup else None,
            "contact_email": sup.contact_email if sup else None,
        }
        alerts.append({
            "product_id": product.id,
            "product_name": product.name,
            "sku": product.sku,
            "warehouse_id": warehouse.id,
            "warehouse_name": warehouse.name,
            "current_stock": int(inv.quantity_on_hand),
            "threshold": int(product.threshold),
            "days_until_stockout": days_until,
            "supplier": supplier_info,
        })

    return jsonify({"alerts": alerts, "total_alerts": len(alerts)})


if __name__ == "__main__":
    seed_demo_data()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))