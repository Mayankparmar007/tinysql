# Olist Business Metrics & Semantic Rules (Source of Truth)

1. **Delivered Order**: `order_status = 'delivered'`. All revenue/delivery queries filter by this status unless explicitly stated otherwise.
2. **Net Revenue**: `SUM(price)` from `order_items` for delivered orders (excludes freight).
3. **Total Order Value**: `SUM(price + freight_value)` from `order_items`.
4. **Late Delivery**: `order_delivered_customer_date > order_estimated_delivery_date`.
5. **Delivery Duration (Days)**: `EXTRACT(DAY FROM (order_delivered_customer_date - order_purchase_timestamp))`.
6. **Active Seller**: A seller associated with at least one delivered order.

### Table Keys & Grain
- `orders`: 1 row per order (`order_id`)
- `order_items`: 1 row per item within an order (`order_id`, `order_item_id`)
- `customers`: 1 row per customer session (`customer_id`; `customer_unique_id` identifies real repeat buyers)
- `products`: 1 row per product (`product_id`)
- `sellers`: 1 row per seller (`seller_id`)
- `order_payments`: 1 row per payment instalment/method (`order_id`, `payment_sequential`)
- `order_reviews`: 1 row per review (`review_id`, `order_id`)
- `geolocation`: zip code prefix coordinate mapping (`geolocation_zip_code_prefix`)
- `category_translation`: Portuguese to English product category mapping
