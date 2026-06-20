CREATE SCHEMA IF NOT EXISTS analytics;

-- store this salt somewhere safe, e.g. in your audit bucket
-- for now: \set pii_salt 'ecom-v1-2026-change-me'
CREATE TABLE analytics.users AS
SELECT
  uim.analytics_user_id,
  users.city,
  users.state,
  users.country,
  users.created_at
FROM
  ecommerce.users users
  join ecommerce.user_id_map uim on (users.user_id = uim.user_id)
where
  deleted_at IS NULL;

CREATE TABLE analytics.orders_clean AS
SELECT
  order_id,
  uim.analytics_user_id,
  order_date,
  order_status,
  payment_method,
  total_amount,
  shipping_city,
  o.created_at
FROM
  ecommerce.orders o
  join ecommerce.user_id_map uim on (o.user_id = uim.user_id);

CREATE TABLE analytics.order_items_clean AS
SELECT
  *
FROM
  ecommerce.order_items;

CREATE TABLE analytics.products_clean AS
SELECT
  *
FROM
  ecommerce.products;

commit;