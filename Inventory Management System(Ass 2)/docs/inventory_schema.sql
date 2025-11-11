

CREATE TABLE IF NOT EXISTS companies (
    id            BIGSERIAL PRIMARY KEY,
    name          VARCHAR(255) NOT NULL UNIQUE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS suppliers (
    id            BIGSERIAL PRIMARY KEY,
    name          VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255),
    phone         VARCHAR(64),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS warehouses (
    id            BIGSERIAL PRIMARY KEY,
    company_id    BIGINT NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    name          VARCHAR(255) NOT NULL,
    location      VARCHAR(255),
    active        BOOLEAN NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (company_id, name)
);
CREATE INDEX IF NOT EXISTS i

dx_warehouses_company ON warehouses(company_id);

CREATE TABLE IF NOT EXISTS products (
    id             BIGSERIAL PRIMARY KEY,
    company_id     BIGINT NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    supplier_id    BIGINT REFERENCES suppliers(id) ON DELETE SET NULL,
    sku            VARCHAR(64) NOT NULL,
    name           VARCHAR(255) NOT NULL,
    is_bundle      BOOLEAN NOT NULL DEFAULT FALSE,
    threshold      INTEGER NOT NULL DEFAULT 0 CHECK (threshold >= 0),
    active         BOOLEAN NOT NULL DEFAULT TRUE,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (company_id, sku)
);
CREATE INDEX IF NOT EXISTS idx_products_company ON products(company_id);
CREATE INDEX IF NOT EXISTS idx_products_supplier ON products(supplier_id);
-- Convenience unique for composite FKs
CREATE UNIQUE INDEX IF NOT EXISTS ux_products_company_id_id ON products(company_id, id);

-- Many-to-many: products can have multiple suppliers
CREATE TABLE IF NOT EXISTS product_suppliers (
    company_id   BIGINT NOT NULL,
    product_id   BIGINT NOT NULL,
    supplier_id  BIGINT NOT NULL,
    PRIMARY KEY (company_id, product_id, supplier_id),
    FOREIGN KEY (company_id, product_id) REFERENCES products(company_id, id) ON DELETE CASCADE,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_product_suppliers_supplier ON product_suppliers(supplier_id);

-- Bundle composition: a bundle product contains component products with defined quantity
CREATE TABLE IF NOT EXISTS bundle_components (
    company_id            BIGINT NOT NULL,
    bundle_product_id     BIGINT NOT NULL,
    component_product_id  BIGINT NOT NULL,
    quantity_per_bundle   NUMERIC(18,4) NOT NULL CHECK (quantity_per_bundle > 0),
    PRIMARY KEY (company_id, bundle_product_id, component_product_id),
    FOREIGN KEY (company_id, bundle_product_id) REFERENCES products(company_id, id) ON DELETE CASCADE,
    FOREIGN KEY (company_id, component_product_id) REFERENCES products(company_id, id) ON DELETE CASCADE
);

-- Inventory per warehouse per product, enforced to same company via composite FKs
CREATE TABLE IF NOT EXISTS inventory (
    id               BIGSERIAL PRIMARY KEY,
    company_id       BIGINT NOT NULL,
    warehouse_id     BIGINT NOT NULL,
    product_id       BIGINT NOT NULL,
    quantity_on_hand INTEGER NOT NULL DEFAULT 0 CHECK (quantity_on_hand >= 0),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (warehouse_id, product_id),
    FOREIGN KEY (company_id, warehouse_id) REFERENCES warehouses(company_id, id) ON DELETE CASCADE,
    FOREIGN KEY (company_id, product_id) REFERENCES products(company_id, id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_inventory_company_product ON inventory(company_id, product_id);
CREATE INDEX IF NOT EXISTS idx_inventory_company_warehouse ON inventory(company_id, warehouse_id);

-- Inventory transactions history
CREATE TABLE IF NOT EXISTS inventory_transactions (
    id            BIGSERIAL PRIMARY KEY,
    company_id    BIGINT NOT NULL,
    warehouse_id  BIGINT NOT NULL,
    product_id    BIGINT NOT NULL,
    change_qty    INTEGER NOT NULL, -- positive for addition, negative for deduction
    change_type   VARCHAR(32) NOT NULL CHECK (change_type IN ('sale','restock','adjustment','transfer_in','transfer_out','bundle_assembly','bundle_disassembly')),
    reference     VARCHAR(255),
    occurred_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    FOREIGN KEY (company_id, warehouse_id) REFERENCES warehouses(company_id, id) ON DELETE CASCADE,
    FOREIGN KEY (company_id, product_id) REFERENCES products(company_id, id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_tx_company_product_date ON inventory_transactions(company_id, product_id, occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_tx_company_warehouse_date ON inventory_transactions(company_id, warehouse_id, occurred_at DESC);

-- Sales activity (used for alert logic)
CREATE TABLE IF NOT EXISTS sales (
    id             BIGSERIAL PRIMARY KEY,
    company_id     BIGINT NOT NULL,
    warehouse_id   BIGINT NOT NULL,
    product_id     BIGINT NOT NULL,
    quantity_sold  INTEGER NOT NULL CHECK (quantity_sold > 0),
    sale_date      TIMESTAMPTZ NOT NULL,
    FOREIGN KEY (company_id, warehouse_id) REFERENCES warehouses(company_id, id) ON DELETE CASCADE,
    FOREIGN KEY (company_id, product_id) REFERENCES products(company_id, id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_sales_company_product_date ON sales(company_id, product_id, sale_date DESC);
CREATE INDEX IF NOT EXISTS idx_sales_company_warehouse_date ON sales(company_id, warehouse_id, sale_date DESC);

-- Optional: ensure bundles are flagged correctly (not enforced via constraint, but recommended)
-- Application should set products.is_bundle = TRUE for bundle_product_id rows present in bundle_components.

-- Prevent inconsistent data: optional trigger example (commented)
-- You may add triggers to assert inventory.company_id matches referenced company on warehouses/products. Composite FKs already enforce this.

-- End of schema