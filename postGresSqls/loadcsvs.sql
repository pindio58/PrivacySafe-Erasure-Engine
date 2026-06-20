-- productsc

docker exec -i \
-e PGPASSWORD='hurbu4-xongeP-fahmuf' \
pg-client psql \
-h privacysafeerasuredatabase.c9egc6syiesb.ap-south-1.rds.amazonaws.com \
-U ecom_admin \
-d postgres \
-p 5432 \
-c "\copy ecommerce.products(product_id,product_name,category,brand,price) FROM STDIN DELIMITER ',' CSV HEADER" \
< /Users/bhupinderjitsingh/airflwstudy/Projects/PrivacySafe-Erasure-Engine/data/products.csv


-- users 

docker exec -i \
-e PGPASSWORD='hurbu4-xongeP-fahmuf' \
pg-client psql \
-h privacysafeerasuredatabase.c9egc6syiesb.ap-south-1.rds.amazonaws.com \
-U ecom_admin \
-d postgres \
-p 5432 \
-c "\copy ecommerce.users(user_id,first_name,last_name,email,phone,address_line1,city,state,pincode,country,created_at,deleted_at
) FROM STDIN DELIMITER ',' CSV HEADER" \
< /Users/bhupinderjitsingh/airflwstudy/Projects/PrivacySafe-Erasure-Engine/data/users.csv

-- orders
docker exec -i \
-e PGPASSWORD='hurbu4-xongeP-fahmuf' \
pg-client psql \
-h privacysafeerasuredatabase.c9egc6syiesb.ap-south-1.rds.amazonaws.com \
-U ecom_admin \
-d postgres \
-p 5432 \
-c "\copy ecommerce.orders(order_id,user_id,order_date,order_status,payment_method,total_amount,shipping_city,created_at) FROM STDIN DELIMITER ',' CSV HEADER" \
< /Users/bhupinderjitsingh/airflwstudy/Projects/PrivacySafe-Erasure-Engine/data/orders.csv


-- order Items
docker exec -i \
-e PGPASSWORD='hurbu4-xongeP-fahmuf' \
pg-client psql \
-h privacysafeerasuredatabase.c9egc6syiesb.ap-south-1.rds.amazonaws.com \
-U ecom_admin \
-d postgres \
-p 5432 \
-c "\copy ecommerce.order_items(order_item_id,order_id,product_id,quantity,unit_price,line_total) FROM STDIN DELIMITER ',' CSV HEADER" \
< /Users/bhupinderjitsingh/airflwstudy/Projects/PrivacySafe-Erasure-Engine/data/order_items.csv

-- user_id_map

INSERT INTO ecommerce.user_id_map (user_id)
SELECT user_id FROM ecommerce.users
ON CONFLICT (user_id) DO NOTHING;
