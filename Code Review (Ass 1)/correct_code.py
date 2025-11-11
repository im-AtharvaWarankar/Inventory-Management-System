from flask import Flask, request, jsonify
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.exceptions import BadRequest

app = Flask(__name__)

@app.route('/api/products', methods=['POST'])
def create_product():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        required_fields = ['name', 'sku', 'price', 'warehouse_id']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                "error": "Missing required fields",
                "missing": missing_fields
            }), 400
        
        name = data.get('name', '').strip()
        sku = data.get('sku', '').strip()
        
        if not name or not sku:
            return jsonify({"error": "Name and SKU cannot be empty"}), 400
        
        try:
            price = float(data['price'])
            if price < 0:
                return jsonify({"error": "Price cannot be negative"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid price format"}), 400
        
        warehouse_id = data.get('warehouse_id')
        if not isinstance(warehouse_id, int) or warehouse_id <= 0:
            return jsonify({"error": "Invalid warehouse ID"}), 400
        
        initial_quantity = data.get('initial_quantity', 0)
        try:
            initial_quantity = int(initial_quantity)
            if initial_quantity < 0:
                return jsonify({"error": "Initial quantity cannot be negative"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid initial quantity format"}), 400
        
        existing_product = Product.query.filter_by(sku=sku).first()
        
        if existing_product:
            existing_inventory = Inventory.query.filter_by(
                product_id=existing_product.id,
                warehouse_id=warehouse_id
            ).first()
            
            if existing_inventory:
                return jsonify({
                    "error": "Product with this SKU already exists in this warehouse",
                    "product_id": existing_product.id
                }), 409
            
            inventory = Inventory(
                product_id=existing_product.id,
                warehouse_id=warehouse_id,
                quantity=initial_quantity
            )
            
            db.session.add(inventory)
            db.session.commit()
            
            return jsonify({
                "message": "Product already exists, inventory added for new warehouse",
                "product_id": existing_product.id,
                "warehouse_id": warehouse_id
            }), 201
        
        product = Product(
            name=name,
            sku=sku,
            price=price,
            warehouse_id=warehouse_id
        )
        
        db.session.add(product)
        db.session.flush()
        
        inventory = Inventory(
            product_id=product.id,
            warehouse_id=warehouse_id,
            quantity=initial_quantity
        )
        
        db.session.add(inventory)
        db.session.commit()
        
        return jsonify({
            "message": "Product created successfully",
            "product_id": product.id,
            "sku": product.sku,
            "warehouse_id": warehouse_id
        }), 201
        
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({
            "error": "Database integrity error",
            "details": "SKU might already exist or foreign key constraint violated"
        }), 409
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            "error": "Database error occurred",
            "details": str(e)
        }), 500
        
    except BadRequest:
        return jsonify({"error": "Invalid JSON data"}), 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "An unexpected error occurred",
            "details": str(e)
        }), 500
