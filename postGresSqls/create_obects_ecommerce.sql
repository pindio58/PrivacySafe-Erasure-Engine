-- Create the dedicated schema
CREATE SCHEMA IF NOT EXISTS ecommerce;

SET search_path TO ecommerce;

-- 1. PRODUCTS TABLE (Zero PII, catalog baseline)
-- product_id,product_name,category,brand,price
CREATE TABLE ecommerce.products(
    product_id integer PRIMARY KEY,
    product_name varchar(255) NOT NULL,
    category varchar(50) NOT NULL,
    brand varchar(50) NOT NULL,
    price numeric(10, 2) NOT NULL
);

-- 2. USERS TABLE (The PII Hotspot with Soft-Delete Tracking)
-- user_id,first_name,last_name,email,phone,address_line1,city,state,pincode,country,created_at,deleted_at
CREATE TABLE ecommerce.users(
    user_id uuid PRIMARY KEY,
    first_name varchar(50) NOT NULL,
    last_name varchar(50) NOT NULL,
    email varchar(255) NOT NULL UNIQUE,
    phone varchar(20) NOT NULL,
    address_line1 varchar(255) NOT NULL,
    city varchar(100) NOT NULL,
    state varchar(50) NOT NULL,
    pincode varchar(10) NOT NULL,
    country varchar(50) NOT NULL DEFAULT 'India',
    created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at timestamp with time zone, -- NULL means active; timestamp indicates soft-delete event
    -- Safety check constraint to ensure deletion timestamp isn't set in the past
    CONSTRAINT check_deleted_after_created CHECK (deleted_at IS NULL OR deleted_at >= created_at)
);

-- 3. ORDERS TABLE (Privacy-Optimized: Tracks City, No PII Street Address)
-- order_id,user_id,order_date,order_status,payment_method,total_amount,shipping_city,created_at
CREATE TABLE ecommerce.orders(
    order_id uuid PRIMARY KEY,
    user_id uuid NOT NULL,
    order_date timestamp with time zone NOT NULL,
    order_status varchar(20) NOT NULL,
    payment_method varchar(30) NOT NULL,
    total_amount numeric(12, 2) NOT NULL,
    shipping_city varchar(100) NOT NULL,
    created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP, -- CDC tracking timestamp
    -- Hard cascade on delete to support direct erasure flows when bypassing soft-deletes
    CONSTRAINT fk_orders_user_id FOREIGN KEY (user_id) REFERENCES ecommerce.users(user_id) ON DELETE CASCADE
);

-- 4. ORDER_ITEMS TABLE (Pure Analytics Engine)
CREATE TABLE ecommerce.order_items(
    order_item_id uuid PRIMARY KEY,
    order_id uuid NOT NULL,
    product_id integer NOT NULL,
    quantity integer NOT NULL CHECK (quantity > 0),
    unit_price numeric(10, 2) NOT NULL,
    -- Automatically calculated stored column to eliminate calculation drift during Snowflake syncs
    line_total numeric(10, 2), --GENERATED ALWAYS AS (quantity * unit_price) STORED,
    CONSTRAINT fk_items_order_id FOREIGN KEY (order_id) REFERENCES ecommerce.orders(order_id) ON DELETE CASCADE,
    CONSTRAINT fk_items_product_id FOREIGN KEY (product_id) REFERENCES ecommerce.products(product_id)
);

-- 5. THE PRIVACY BRIDGE MAP (Keep this highly restricted!)
-- This is the ONLY table that connects real users to analytics IDs.
CREATE TABLE ecommerce.user_id_map(
    user_id uuid PRIMARY KEY REFERENCES ecommerce.users(user_id) ON DELETE CASCADE,
    analytics_user_id uuid NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE ecommerce.users
    ALTER COLUMN first_name TYPE VARCHAR(64),
    ALTER COLUMN last_name TYPE VARCHAR(64),
    ALTER COLUMN phone TYPE VARCHAR(64);

COMMIT;

