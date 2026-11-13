import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "eval_set.jsonl")

# 1. Single Table Aggregations (~96 items)
# 2. Multi-Table Joins (~60 items)
# 3. Window Functions (~20 items)
# 4. Date Math (~24 items)
# 5. Unanswerable / Refusal (~24 items)
# Total: 224 questions

questions = []

def add_q(category, question, sql):
    questions.append({
        "id": len(questions) + 1,
        "category": category,
        "question": question,
        "gold_sql": sql,
        "result_hash": None
    })

# ==========================================
# CATEGORY 1: SINGLE-TABLE AGGREGATIONS (~96)
# ==========================================

# Orders table
add_q("aggregation", "How many total orders are in the database?", "SELECT COUNT(*) FROM orders;")
add_q("aggregation", "What is the total number of delivered orders?", "SELECT COUNT(*) FROM orders WHERE order_status = 'delivered';")
add_q("aggregation", "How many orders have been canceled?", "SELECT COUNT(*) FROM orders WHERE order_status = 'canceled';")
add_q("aggregation", "How many orders are currently in unavailable status?", "SELECT COUNT(*) FROM orders WHERE order_status = 'unavailable';")
add_q("aggregation", "How many orders are in shipped status?", "SELECT COUNT(*) FROM orders WHERE order_status = 'shipped';")
add_q("aggregation", "How many orders are in invoiced status?", "SELECT COUNT(*) FROM orders WHERE order_status = 'invoiced';")
add_q("aggregation", "How many orders are in processing status?", "SELECT COUNT(*) FROM orders WHERE order_status = 'processing';")
add_q("aggregation", "How many orders are in created status?", "SELECT COUNT(*) FROM orders WHERE order_status = 'created';")
add_q("aggregation", "What are all the distinct order statuses available in orders?", "SELECT DISTINCT order_status FROM orders ORDER BY order_status;")
add_q("aggregation", "What is the total count of distinct customers who have placed an order?", "SELECT COUNT(DISTINCT customer_id) FROM orders;")

# Order Items table
add_q("aggregation", "What is the total count of order items sold?", "SELECT COUNT(*) FROM order_items;")
add_q("aggregation", "What is the total sum of price across all order items?", "SELECT SUM(price) FROM order_items;")
add_q("aggregation", "What is the average price of an item sold?", "SELECT AVG(price) FROM order_items;")
add_q("aggregation", "What is the minimum item price in order_items?", "SELECT MIN(price) FROM order_items;")
add_q("aggregation", "What is the maximum item price in order_items?", "SELECT MAX(price) FROM order_items;")
add_q("aggregation", "What is the total freight value paid across all order items?", "SELECT SUM(freight_value) FROM order_items;")
add_q("aggregation", "What is the average freight value per order item?", "SELECT AVG(freight_value) FROM order_items;")
add_q("aggregation", "What is the maximum freight value recorded for a single item?", "SELECT MAX(freight_value) FROM order_items;")
add_q("aggregation", "What is the minimum freight value recorded for an item?", "SELECT MIN(freight_value) FROM order_items;")
add_q("aggregation", "How many distinct products have been ordered in order_items?", "SELECT COUNT(DISTINCT product_id) FROM order_items;")
add_q("aggregation", "How many distinct sellers have sold at least one item in order_items?", "SELECT COUNT(DISTINCT seller_id) FROM order_items;")
add_q("aggregation", "What is the count of items with price greater than 500?", "SELECT COUNT(*) FROM order_items WHERE price > 500;")
add_q("aggregation", "What is the count of items with price less than or equal to 50?", "SELECT COUNT(*) FROM order_items WHERE price <= 50;")
add_q("aggregation", "What is the average price of items where freight value is greater than 20?", "SELECT AVG(price) FROM order_items WHERE freight_value > 20;")

# Customers table
add_q("aggregation", "How many total customer records exist in customers?", "SELECT COUNT(*) FROM customers;")
add_q("aggregation", "How many distinct unique customer IDs exist?", "SELECT COUNT(DISTINCT customer_unique_id) FROM customers;")
add_q("aggregation", "How many distinct customer states exist?", "SELECT COUNT(DISTINCT customer_state) FROM customers;")
add_q("aggregation", "How many distinct customer cities exist?", "SELECT COUNT(DISTINCT customer_city) FROM customers;")
add_q("aggregation", "How many customers are located in the state of SP?", "SELECT COUNT(*) FROM customers WHERE customer_state = 'SP';")
add_q("aggregation", "How many customers are located in the state of RJ?", "SELECT COUNT(*) FROM customers WHERE customer_state = 'RJ';")
add_q("aggregation", "How many customers are located in the state of MG?", "SELECT COUNT(*) FROM customers WHERE customer_state = 'MG';")
add_q("aggregation", "How many customers are located in the state of RS?", "SELECT COUNT(*) FROM customers WHERE customer_state = 'RS';")
add_q("aggregation", "How many customers are located in the state of PR?", "SELECT COUNT(*) FROM customers WHERE customer_state = 'PR';")
add_q("aggregation", "How many customers are in the city of sao paulo?", "SELECT COUNT(*) FROM customers WHERE customer_city = 'sao paulo';")
add_q("aggregation", "How many customers are in the city of rio de janeiro?", "SELECT COUNT(*) FROM customers WHERE customer_city = 'rio de janeiro';")
add_q("aggregation", "List the top 5 customer states by total number of customers.", "SELECT customer_state, COUNT(*) as cnt FROM customers GROUP BY customer_state ORDER BY cnt DESC LIMIT 5;")
add_q("aggregation", "List the top 5 customer cities by total customer count.", "SELECT customer_city, COUNT(*) as cnt FROM customers GROUP BY customer_city ORDER BY cnt DESC LIMIT 5;")
add_q("aggregation", "How many customer states have more than 1000 customers?", "SELECT COUNT(*) FROM (SELECT customer_state FROM customers GROUP BY customer_state HAVING COUNT(*) > 1000) sub;")

# Products table
add_q("aggregation", "How many total products exist in the catalog?", "SELECT COUNT(*) FROM products;")
add_q("aggregation", "How many distinct product categories exist in products?", "SELECT COUNT(DISTINCT product_category_name) FROM products;")
add_q("aggregation", "How many products have a missing category name?", "SELECT COUNT(*) FROM products WHERE product_category_name IS NULL;")
add_q("aggregation", "What is the average product weight in grams?", "SELECT AVG(product_weight_g) FROM products WHERE product_weight_g IS NOT NULL;")
add_q("aggregation", "What is the maximum product weight in grams in products?", "SELECT MAX(product_weight_g) FROM products;")
add_q("aggregation", "What is the minimum product weight in grams in products?", "SELECT MIN(product_weight_g) FROM products;")
add_q("aggregation", "What is the average number of photos per product?", "SELECT AVG(product_photos_qty) FROM products WHERE product_photos_qty IS NOT NULL;")
add_q("aggregation", "What is the maximum photo quantity for any product?", "SELECT MAX(product_photos_qty) FROM products;")
add_q("aggregation", "What is the average product length in centimeters?", "SELECT AVG(product_length_cm) FROM products WHERE product_length_cm IS NOT NULL;")
add_q("aggregation", "What is the average product height in centimeters?", "SELECT AVG(product_height_cm) FROM products WHERE product_height_cm IS NOT NULL;")
add_q("aggregation", "What is the average product width in centimeters?", "SELECT AVG(product_width_cm) FROM products WHERE product_width_cm IS NOT NULL;")
add_q("aggregation", "How many products belong to the cama_mesa_banho category?", "SELECT COUNT(*) FROM products WHERE product_category_name = 'cama_mesa_banho';")
add_q("aggregation", "How many products belong to the beleza_saude category?", "SELECT COUNT(*) FROM products WHERE product_category_name = 'beleza_saude';")
add_q("aggregation", "How many products belong to the esporte_lazer category?", "SELECT COUNT(*) FROM products WHERE product_category_name = 'esporte_lazer';")
add_q("aggregation", "List the top 5 product categories by number of products.", "SELECT product_category_name, COUNT(*) as cnt FROM products WHERE product_category_name IS NOT NULL GROUP BY product_category_name ORDER BY cnt DESC LIMIT 5;")

# Order Payments table
add_q("aggregation", "How many total payment records are in order_payments?", "SELECT COUNT(*) FROM order_payments;")
add_q("aggregation", "What is the total payment value across all orders?", "SELECT SUM(payment_value) FROM order_payments;")
add_q("aggregation", "What is the average payment value per transaction?", "SELECT AVG(payment_value) FROM order_payments;")
add_q("aggregation", "What is the maximum single payment value recorded?", "SELECT MAX(payment_value) FROM order_payments;")
add_q("aggregation", "What is the minimum payment value recorded?", "SELECT MIN(payment_value) FROM order_payments;")
add_q("aggregation", "What are all the distinct payment types used?", "SELECT DISTINCT payment_type FROM order_payments ORDER BY payment_type;")
add_q("aggregation", "How many payments were made using credit_card?", "SELECT COUNT(*) FROM order_payments WHERE payment_type = 'credit_card';")
add_q("aggregation", "How many payments were made using boleto?", "SELECT COUNT(*) FROM order_payments WHERE payment_type = 'boleto';")
add_q("aggregation", "How many payments were made using voucher?", "SELECT COUNT(*) FROM order_payments WHERE payment_type = 'voucher';")
add_q("aggregation", "How many payments were made using debit_card?", "SELECT COUNT(*) FROM order_payments WHERE payment_type = 'debit_card';")
add_q("aggregation", "What is the total payment value collected via credit card?", "SELECT SUM(payment_value) FROM order_payments WHERE payment_type = 'credit_card';")
add_q("aggregation", "What is the total payment value collected via boleto?", "SELECT SUM(payment_value) FROM order_payments WHERE payment_type = 'boleto';")
add_q("aggregation", "What is the average number of payment installments for credit card transactions?", "SELECT AVG(payment_installments) FROM order_payments WHERE payment_type = 'credit_card';")
add_q("aggregation", "What is the maximum number of payment installments recorded?", "SELECT MAX(payment_installments) FROM order_payments;")
add_q("aggregation", "What is the count of payments that used more than 10 installments?", "SELECT COUNT(*) FROM order_payments WHERE payment_installments > 10;")
add_q("aggregation", "What is the count of distinct orders in order_payments?", "SELECT COUNT(DISTINCT order_id) FROM order_payments;")
add_q("aggregation", "List each payment type and the total payment value for each.", "SELECT payment_type, SUM(payment_value) as total_val FROM order_payments GROUP BY payment_type ORDER BY total_val DESC;")
add_q("aggregation", "List each payment type and its transaction count.", "SELECT payment_type, COUNT(*) as txn_count FROM order_payments GROUP BY payment_type ORDER BY txn_count DESC;")

# Order Reviews table
add_q("aggregation", "How many total reviews were submitted in order_reviews?", "SELECT COUNT(*) FROM order_reviews;")
add_q("aggregation", "What is the overall average review score?", "SELECT AVG(review_score) FROM order_reviews;")
add_q("aggregation", "How many reviews received a 5-star score?", "SELECT COUNT(*) FROM order_reviews WHERE review_score = 5;")
add_q("aggregation", "How many reviews received a 1-star score?", "SELECT COUNT(*) FROM order_reviews WHERE review_score = 1;")
add_q("aggregation", "How many reviews received a 4-star score?", "SELECT COUNT(*) FROM order_reviews WHERE review_score = 4;")
add_q("aggregation", "How many reviews received a 3-star score?", "SELECT COUNT(*) FROM order_reviews WHERE review_score = 3;")
add_q("aggregation", "How many reviews received a 2-star score?", "SELECT COUNT(*) FROM order_reviews WHERE review_score = 2;")
add_q("aggregation", "How many reviews have a comment message provided?", "SELECT COUNT(*) FROM order_reviews WHERE review_comment_message IS NOT NULL;")
add_q("aggregation", "How many reviews have a comment title provided?", "SELECT COUNT(*) FROM order_reviews WHERE review_comment_title IS NOT NULL;")
add_q("aggregation", "What is the count of reviews grouped by review score?", "SELECT review_score, COUNT(*) as cnt FROM order_reviews GROUP BY review_score ORDER BY review_score DESC;")
add_q("aggregation", "What is the count of distinct orders that have a review in order_reviews?", "SELECT COUNT(DISTINCT order_id) FROM order_reviews;")

# Sellers table
add_q("aggregation", "How many total sellers are registered?", "SELECT COUNT(*) FROM sellers;")
add_q("aggregation", "How many distinct seller states exist?", "SELECT COUNT(DISTINCT seller_state) FROM sellers;")
add_q("aggregation", "How many distinct seller cities exist?", "SELECT COUNT(DISTINCT seller_city) FROM sellers;")
add_q("aggregation", "How many sellers are located in the state of SP?", "SELECT COUNT(*) FROM sellers WHERE seller_state = 'SP';")
add_q("aggregation", "How many sellers are located in the state of PR?", "SELECT COUNT(*) FROM sellers WHERE seller_state = 'PR';")
add_q("aggregation", "How many sellers are located in the state of MG?", "SELECT COUNT(*) FROM sellers WHERE seller_state = 'MG';")
add_q("aggregation", "How many sellers are located in the state of RJ?", "SELECT COUNT(*) FROM sellers WHERE seller_state = 'RJ';")
add_q("aggregation", "How many sellers are located in the state of SC?", "SELECT COUNT(*) FROM sellers WHERE seller_state = 'SC';")
add_q("aggregation", "List the top 5 seller states by seller count.", "SELECT seller_state, COUNT(*) as cnt FROM sellers GROUP BY seller_state ORDER BY cnt DESC LIMIT 5;")
add_q("aggregation", "List the top 5 seller cities by seller count.", "SELECT seller_city, COUNT(*) as cnt FROM sellers GROUP BY seller_city ORDER BY cnt DESC LIMIT 5;")

# Category Translation
add_q("aggregation", "How many translations exist in category_translation?", "SELECT COUNT(*) FROM category_translation;")
add_q("aggregation", "What is the English name for the category relogios_presentes?", "SELECT product_category_name_english FROM category_translation WHERE product_category_name = 'relogios_presentes';")
add_q("aggregation", "What is the Portuguese category name for bed_bath_table?", "SELECT product_category_name FROM category_translation WHERE product_category_name_english = 'bed_bath_table';")
add_q("aggregation", "What is the English name for beleza_saude in category_translation?", "SELECT product_category_name_english FROM category_translation WHERE product_category_name = 'beleza_saude';")

# Additional aggregations
add_q("aggregation", "What is the average review score for reviews that contain a comment message?", "SELECT AVG(review_score) FROM order_reviews WHERE review_comment_message IS NOT NULL;")
add_q("aggregation", "What is the total number of orders placed in 2017?", "SELECT COUNT(*) FROM orders WHERE order_purchase_timestamp >= '2017-01-01 00:00:00' AND order_purchase_timestamp < '2018-01-01 00:00:00';")
add_q("aggregation", "What is the total number of orders placed in 2018?", "SELECT COUNT(*) FROM orders WHERE order_purchase_timestamp >= '2018-01-01 00:00:00' AND order_purchase_timestamp < '2019-01-01 00:00:00';")
add_q("aggregation", "How many orders were placed in 2016?", "SELECT COUNT(*) FROM orders WHERE order_purchase_timestamp >= '2016-01-01 00:00:00' AND order_purchase_timestamp < '2017-01-01 00:00:00';")

# ==========================================
# CATEGORY 2: MULTI-TABLE JOINS (~60)
# ==========================================

add_q("join", "What is the total net revenue from delivered orders in the state of SP?", 
      "SELECT SUM(oi.price) FROM order_items oi JOIN orders o ON oi.order_id = o.order_id JOIN customers c ON o.customer_id = c.customer_id WHERE o.order_status = 'delivered' AND c.customer_state = 'SP';")
add_q("join", "What is the total net revenue from delivered orders in the state of RJ?", 
      "SELECT SUM(oi.price) FROM order_items oi JOIN orders o ON oi.order_id = o.order_id JOIN customers c ON o.customer_id = c.customer_id WHERE o.order_status = 'delivered' AND c.customer_state = 'RJ';")
add_q("join", "What is the total net revenue from delivered orders in the state of MG?", 
      "SELECT SUM(oi.price) FROM order_items oi JOIN orders o ON oi.order_id = o.order_id JOIN customers c ON o.customer_id = c.customer_id WHERE o.order_status = 'delivered' AND c.customer_state = 'MG';")
add_q("join", "What is the total freight value paid by customers in SP for delivered orders?", 
      "SELECT SUM(oi.freight_value) FROM order_items oi JOIN orders o ON oi.order_id = o.order_id JOIN customers c ON o.customer_id = c.customer_id WHERE o.order_status = 'delivered' AND c.customer_state = 'SP';")
add_q("join", "What is the total order value including freight for delivered orders in SP?", 
      "SELECT SUM(oi.price + oi.freight_value) FROM order_items oi JOIN orders o ON oi.order_id = o.order_id JOIN customers c ON o.customer_id = c.customer_id WHERE o.order_status = 'delivered' AND c.customer_state = 'SP';")
add_q("join", "How many delivered orders were made by customers in the city of sao paulo?", 
      "SELECT COUNT(DISTINCT o.order_id) FROM orders o JOIN customers c ON o.customer_id = c.customer_id WHERE o.order_status = 'delivered' AND c.customer_city = 'sao paulo';")
add_q("join", "How many delivered orders were made by customers in the city of rio de janeiro?", 
      "SELECT COUNT(DISTINCT o.order_id) FROM orders o JOIN customers c ON o.customer_id = c.customer_id WHERE o.order_status = 'delivered' AND c.customer_city = 'rio de janeiro';")
add_q("join", "What is the total net revenue generated by sellers located in SP?", 
      "SELECT SUM(oi.price) FROM order_items oi JOIN orders o ON oi.order_id = o.order_id JOIN sellers s ON oi.seller_id = s.seller_id WHERE o.order_status = 'delivered' AND s.seller_state = 'SP';")
add_q("join", "What is the total net revenue generated by sellers located in PR?", 
      "SELECT SUM(oi.price) FROM order_items oi JOIN orders o ON oi.order_id = o.order_id JOIN sellers s ON oi.seller_id = s.seller_id WHERE o.order_status = 'delivered' AND s.seller_state = 'PR';")
add_q("join", "What is the total net revenue generated by sellers located in MG?", 
      "SELECT SUM(oi.price) FROM order_items oi JOIN orders o ON oi.order_id = o.order_id JOIN sellers s ON oi.seller_id = s.seller_id WHERE o.order_status = 'delivered' AND s.seller_state = 'MG';")
add_q("join", "How many active sellers are in the state of SP?", 
      "SELECT COUNT(DISTINCT s.seller_id) FROM sellers s JOIN order_items oi ON s.seller_id = oi.seller_id JOIN orders o ON oi.order_id = o.order_id WHERE o.order_status = 'delivered' AND s.seller_state = 'SP';")
add_q("join", "What is the overall average review score for delivered orders?", 
      "SELECT AVG(r.review_score) FROM order_reviews r JOIN orders o ON r.order_id = o.order_id WHERE o.order_status = 'delivered';")
add_q("join", "What is the average review score for canceled orders?", 
      "SELECT AVG(r.review_score) FROM order_reviews r JOIN orders o ON r.order_id = o.order_id WHERE o.order_status = 'canceled';")
add_q("join", "What is the average review score for customers in the state of SP?", 
      "SELECT AVG(r.review_score) FROM order_reviews r JOIN orders o ON r.order_id = o.order_id JOIN customers c ON o.customer_id = c.customer_id WHERE c.customer_state = 'SP';")
add_q("join", "What is the average review score for customers in the state of RJ?", 
      "SELECT AVG(r.review_score) FROM order_reviews r JOIN orders o ON r.order_id = o.order_id JOIN customers c ON o.customer_id = c.customer_id WHERE c.customer_state = 'RJ';")
add_q("join", "What is the average review score for orders with payment type credit_card?", 
      "SELECT AVG(r.review_score) FROM order_reviews r JOIN order_payments p ON r.order_id = p.order_id WHERE p.payment_type = 'credit_card';")
add_q("join", "What is the average review score for orders with payment type boleto?", 
      "SELECT AVG(r.review_score) FROM order_reviews r JOIN order_payments p ON r.order_id = p.order_id WHERE p.payment_type = 'boleto';")
add_q("join", "What is the total net revenue for the product category beleza_saude on delivered orders?", 
      "SELECT SUM(oi.price) FROM order_items oi JOIN orders o ON oi.order_id = o.order_id JOIN products p ON oi.product_id = p.product_id WHERE o.order_status = 'delivered' AND p.product_category_name = 'beleza_saude';")
add_q("join", "What is the total net revenue for the product category cama_mesa_banho on delivered orders?", 
      "SELECT SUM(oi.price) FROM order_items oi JOIN orders o ON oi.order_id = o.order_id JOIN products p ON oi.product_id = p.product_id WHERE o.order_status = 'delivered' AND p.product_category_name = 'cama_mesa_banho';")
add_q("join", "What is the total net revenue for the product category relogios_presentes on delivered orders?", 
      "SELECT SUM(oi.price) FROM order_items oi JOIN orders o ON oi.order_id = o.order_id JOIN products p ON oi.product_id = p.product_id WHERE o.order_status = 'delivered' AND p.product_category_name = 'relogios_presentes';")
add_q("join", "What is the total net revenue for the product category esporte_lazer on delivered orders?", 
      "SELECT SUM(oi.price) FROM order_items oi JOIN orders o ON oi.order_id = o.order_id JOIN products p ON oi.product_id = p.product_id WHERE o.order_status = 'delivered' AND p.product_category_name = 'esporte_lazer';")
add_q("join", "What is the total net revenue for the product category informatica_acessorios on delivered orders?", 
      "SELECT SUM(oi.price) FROM order_items oi JOIN orders o ON oi.order_id = o.order_id JOIN products p ON oi.product_id = p.product_id WHERE o.order_status = 'delivered' AND p.product_category_name = 'informatica_acessorios';")
add_q("join", "List top 5 product categories by net revenue for delivered orders.", 
      "SELECT p.product_category_name, SUM(oi.price) as rev FROM order_items oi JOIN orders o ON oi.order_id = o.order_id JOIN products p ON oi.product_id = p.product_id WHERE o.order_status = 'delivered' AND p.product_category_name IS NOT NULL GROUP BY p.product_category_name ORDER BY rev DESC LIMIT 5;")
add_q("join", "List top 5 English product categories by net revenue for delivered orders.", 
      "SELECT t.product_category_name_english, SUM(oi.price) as rev FROM order_items oi JOIN orders o ON oi.order_id = o.order_id JOIN products p ON oi.product_id = p.product_id JOIN category_translation t ON p.product_category_name = t.product_category_name WHERE o.order_status = 'delivered' GROUP BY t.product_category_name_english ORDER BY rev DESC LIMIT 5;")
add_q("join", "List top 5 English product categories by total item volume sold on delivered orders.", 
      "SELECT t.product_category_name_english, COUNT(*) as items_sold FROM order_items oi JOIN orders o ON oi.order_id = o.order_id JOIN products p ON oi.product_id = p.product_id JOIN category_translation t ON p.product_category_name = t.product_category_name WHERE o.order_status = 'delivered' GROUP BY t.product_category_name_english ORDER BY items_sold DESC LIMIT 5;")
add_q("join", "What is the average review score for the product category beleza_saude?", 
      "SELECT AVG(r.review_score) FROM order_reviews r JOIN order_items oi ON r.order_id = oi.order_id JOIN products p ON oi.product_id = p.product_id WHERE p.product_category_name = 'beleza_saude';")
add_q("join", "What is the average review score for the product category cama_mesa_banho?", 
      "SELECT AVG(r.review_score) FROM order_reviews r JOIN order_items oi ON r.order_id = oi.order_id JOIN products p ON oi.product_id = p.product_id WHERE p.product_category_name = 'cama_mesa_banho';")
add_q("join", "What is the average review score for the product category telefonia?", 
      "SELECT AVG(r.review_score) FROM order_reviews r JOIN order_items oi ON r.order_id = oi.order_id JOIN products p ON oi.product_id = p.product_id WHERE p.product_category_name = 'telefonia';")
add_q("join", "What is the average review score for the product category informatica_acessorios?", 
      "SELECT AVG(r.review_score) FROM order_reviews r JOIN order_items oi ON r.order_id = oi.order_id JOIN products p ON oi.product_id = p.product_id WHERE p.product_category_name = 'informatica_acessorios';")
add_q("join", "How many items of category perfumaria were sold in delivered orders?", 
      "SELECT COUNT(*) FROM order_items oi JOIN orders o ON oi.order_id = o.order_id JOIN products p ON oi.product_id = p.product_id WHERE o.order_status = 'delivered' AND p.product_category_name = 'perfumaria';")
add_q("join", "What is the average price of products in the utilidades_domesticas category sold in delivered orders?", 
      "SELECT AVG(oi.price) FROM order_items oi JOIN orders o ON oi.order_id = o.order_id JOIN products p ON oi.product_id = p.product_id WHERE o.order_status = 'delivered' AND p.product_category_name = 'utilidades_domesticas';")
add_q("join", "List top 5 customer states by total net revenue on delivered orders.", 
      "SELECT c.customer_state, SUM(oi.price) as total_rev FROM order_items oi JOIN orders o ON oi.order_id = o.order_id JOIN customers c ON o.customer_id = c.customer_id WHERE o.order_status = 'delivered' GROUP BY c.customer_state ORDER BY total_rev DESC LIMIT 5;")
add_q("join", "List top 5 seller states by total net revenue on delivered orders.", 
      "SELECT s.seller_state, SUM(oi.price) as total_rev FROM order_items oi JOIN orders o ON oi.order_id = o.order_id JOIN sellers s ON oi.seller_id = s.seller_id WHERE o.order_status = 'delivered' GROUP BY s.seller_state ORDER BY total_rev DESC LIMIT 5;")
add_q("join", "How many delivered orders involved both customer and seller residing in the same state SP?", 
      "SELECT COUNT(DISTINCT o.order_id) FROM orders o JOIN customers c ON o.customer_id = c.customer_id JOIN order_items oi ON o.order_id = oi.order_id JOIN sellers s ON oi.seller_id = s.seller_id WHERE o.order_status = 'delivered' AND c.customer_state = 'SP' AND s.seller_state = 'SP';")
add_q("join", "How many delivered orders involved a customer in RJ and a seller in SP?", 
      "SELECT COUNT(DISTINCT o.order_id) FROM orders o JOIN customers c ON o.customer_id = c.customer_id JOIN order_items oi ON o.order_id = oi.order_id JOIN sellers s ON oi.seller_id = s.seller_id WHERE o.order_status = 'delivered' AND c.customer_state = 'RJ' AND s.seller_state = 'SP';")
add_q("join", "What is the average freight value paid for orders where customer and seller are both in SP?", 
      "SELECT AVG(oi.freight_value) FROM order_items oi JOIN orders o ON oi.order_id = o.order_id JOIN customers c ON o.customer_id = c.customer_id JOIN sellers s ON oi.seller_id = s.seller_id WHERE o.order_status = 'delivered' AND c.customer_state = 'SP' AND s.seller_state = 'SP';")
add_q("join", "What is the average freight value for orders where customer is in RJ and seller is in SP?", 
      "SELECT AVG(oi.freight_value) FROM order_items oi JOIN orders o ON oi.order_id = o.order_id JOIN customers c ON o.customer_id = c.customer_id JOIN sellers s ON oi.seller_id = s.seller_id WHERE o.order_status = 'delivered' AND c.customer_state = 'RJ' AND s.seller_state = 'SP';")
add_q("join", "What is the total number of delivered orders paid via credit card?", 
      "SELECT COUNT(DISTINCT o.order_id) FROM orders o JOIN order_payments p ON o.order_id = p.order_id WHERE o.order_status = 'delivered' AND p.payment_type = 'credit_card';")
add_q("join", "What is the total number of delivered orders paid via boleto?", 
      "SELECT COUNT(DISTINCT o.order_id) FROM orders o JOIN order_payments p ON o.order_id = p.order_id WHERE o.order_status = 'delivered' AND p.payment_type = 'boleto';")
add_q("join", "What is the total payment value collected from customers in SP?", 
      "SELECT SUM(p.payment_value) FROM order_payments p JOIN orders o ON p.order_id = o.order_id JOIN customers c ON o.customer_id = c.customer_id WHERE c.customer_state = 'SP';")
add_q("join", "What is the total payment value collected from customers in RJ?", 
      "SELECT SUM(p.payment_value) FROM order_payments p JOIN orders o ON p.order_id = o.order_id JOIN customers c ON o.customer_id = c.customer_id WHERE c.customer_state = 'RJ';")
add_q("join", "What is the average payment value for delivered orders in SP?", 
      "SELECT AVG(p.payment_value) FROM order_payments p JOIN orders o ON p.order_id = o.order_id JOIN customers c ON o.customer_id = c.customer_id WHERE o.order_status = 'delivered' AND c.customer_state = 'SP';")
add_q("join", "List top 3 sellers by total net revenue on delivered orders.", 
      "SELECT seller_id, SUM(price) as total_rev FROM order_items oi JOIN orders o ON oi.order_id = o.order_id WHERE o.order_status = 'delivered' GROUP BY seller_id ORDER BY total_rev DESC LIMIT 3;")
add_q("join", "List top 3 sellers by total item count sold on delivered orders.", 
      "SELECT seller_id, COUNT(*) as items_sold FROM order_items oi JOIN orders o ON oi.order_id = o.order_id WHERE o.order_status = 'delivered' GROUP BY seller_id ORDER BY items_sold DESC LIMIT 3;")
add_q("join", "What is the average review score for the top seller by items sold?", 
      "SELECT AVG(r.review_score) FROM order_reviews r JOIN order_items oi ON r.order_id = oi.order_id WHERE oi.seller_id = (SELECT seller_id FROM order_items GROUP BY seller_id ORDER BY COUNT(*) DESC LIMIT 1);")
add_q("join", "How many unique customers have placed more than 1 delivered order?", 
      "SELECT COUNT(*) FROM (SELECT c.customer_unique_id FROM customers c JOIN orders o ON c.customer_id = o.customer_id WHERE o.order_status = 'delivered' GROUP BY c.customer_unique_id HAVING COUNT(o.order_id) > 1) sub;")
add_q("join", "What is the maximum number of delivered orders placed by a single unique customer?", 
      "SELECT MAX(order_count) FROM (SELECT COUNT(o.order_id) as order_count FROM customers c JOIN orders o ON c.customer_id = o.customer_id WHERE o.order_status = 'delivered' GROUP BY c.customer_unique_id) sub;")
add_q("join", "What is the total net revenue from repeat customers (more than 1 order)?", 
      "SELECT SUM(oi.price) FROM order_items oi JOIN orders o ON oi.order_id = o.order_id JOIN customers c ON o.customer_id = c.customer_id WHERE o.order_status = 'delivered' AND c.customer_unique_id IN (SELECT c2.customer_unique_id FROM customers c2 JOIN orders o2 ON c2.customer_id = o2.customer_id WHERE o2.order_status = 'delivered' GROUP BY c2.customer_unique_id HAVING COUNT(o2.order_id) > 1);")
add_q("join", "How many delivered orders contain more than 1 item?", 
      "SELECT COUNT(*) FROM (SELECT order_id FROM order_items GROUP BY order_id HAVING COUNT(*) > 1) oi JOIN orders o ON oi.order_id = o.order_id WHERE o.order_status = 'delivered';")
add_q("join", "What is the average number of items per delivered order?", 
      "SELECT AVG(item_count) FROM (SELECT COUNT(oi.order_item_id) as item_count FROM orders o JOIN order_items oi ON o.order_id = oi.order_id WHERE o.order_status = 'delivered' GROUP BY o.order_id) sub;")
add_q("join", "What is the count of distinct products sold by sellers in the state of SP?", 
      "SELECT COUNT(DISTINCT oi.product_id) FROM order_items oi JOIN sellers s ON oi.seller_id = s.seller_id WHERE s.seller_state = 'SP';")
add_q("join", "What is the total freight value received by sellers in SP for delivered orders?", 
      "SELECT SUM(oi.freight_value) FROM order_items oi JOIN orders o ON oi.order_id = o.order_id JOIN sellers s ON oi.seller_id = s.seller_id WHERE o.order_status = 'delivered' AND s.seller_state = 'SP';")
add_q("join", "What is the average item price for delivered orders delivered to Rio de Janeiro city?", 
      "SELECT AVG(oi.price) FROM order_items oi JOIN orders o ON oi.order_id = o.order_id JOIN customers c ON o.customer_id = c.customer_id WHERE o.order_status = 'delivered' AND c.customer_city = 'rio de janeiro';")
add_q("join", "How many 5-star reviews were given for delivered orders in SP?", 
      "SELECT COUNT(*) FROM order_reviews r JOIN orders o ON r.order_id = o.order_id JOIN customers c ON o.customer_id = c.customer_id WHERE o.order_status = 'delivered' AND c.customer_state = 'SP' AND r.review_score = 5;")
add_q("join", "How many 1-star reviews were given for delivered orders in SP?", 
      "SELECT COUNT(*) FROM order_reviews r JOIN orders o ON r.order_id = o.order_id JOIN customers c ON o.customer_id = c.customer_id WHERE o.order_status = 'delivered' AND c.customer_state = 'SP' AND r.review_score = 1;")
add_q("join", "What is the average review score for delivered orders with freight value higher than 50?", 
      "SELECT AVG(r.review_score) FROM order_reviews r JOIN orders o ON r.order_id = o.order_id JOIN order_items oi ON o.order_id = oi.order_id WHERE o.order_status = 'delivered' AND oi.freight_value > 50;")
add_q("join", "What is the total payment value for orders that had a 1-star review score?", 
      "SELECT SUM(p.payment_value) FROM order_payments p JOIN order_reviews r ON p.order_id = r.order_id WHERE r.review_score = 1;")
add_q("join", "What is the total payment value for orders that had a 5-star review score?", 
      "SELECT SUM(p.payment_value) FROM order_payments p JOIN order_reviews r ON p.order_id = r.order_id WHERE r.review_score = 5;")
add_q("join", "How many delivered orders were paid using multiple payment methods or installments?", 
      "SELECT COUNT(*) FROM (SELECT order_id FROM order_payments GROUP BY order_id HAVING COUNT(*) > 1) p JOIN orders o ON p.order_id = o.order_id WHERE o.order_status = 'delivered';")
add_q("join", "What is the average item weight in grams for items sold in the auto category?", 
      "SELECT AVG(p.product_weight_g) FROM products p JOIN order_items oi ON p.product_id = oi.product_id WHERE p.product_category_name = 'auto';")

# ==========================================
# CATEGORY 3: WINDOW FUNCTIONS (~20)
# ==========================================

add_q("window", "Rank the top 3 sellers by total net revenue on delivered orders using DENSE_RANK.", 
      "SELECT seller_id, total_rev, DENSE_RANK() OVER (ORDER BY total_rev DESC) as rnk FROM (SELECT oi.seller_id, SUM(oi.price) as total_rev FROM order_items oi JOIN orders o ON oi.order_id = o.order_id WHERE o.order_status = 'delivered' GROUP BY oi.seller_id) sub LIMIT 3;")
add_q("window", "Rank the top 3 customer states by number of delivered orders using RANK.", 
      "SELECT customer_state, order_count, RANK() OVER (ORDER BY order_count DESC) as rnk FROM (SELECT c.customer_state, COUNT(o.order_id) as order_count FROM customers c JOIN orders o ON c.customer_id = o.customer_id WHERE o.order_status = 'delivered' GROUP BY c.customer_state) sub LIMIT 3;")
add_q("window", "Assign a row number to each customer in SP ordered by their zip code prefix and customer ID.", 
      "SELECT customer_id, customer_zip_code_prefix, ROW_NUMBER() OVER (ORDER BY customer_zip_code_prefix, customer_id) as rn FROM customers WHERE customer_state = 'SP' ORDER BY customer_zip_code_prefix, customer_id LIMIT 5;")
add_q("window", "What is the running total of item prices for order items of seller '3440f050428407457b0d106b54429de5'?", 
      "SELECT order_id, order_item_id, price, SUM(price) OVER (ORDER BY shipping_limit_date, order_id, order_item_id) as running_total FROM order_items WHERE seller_id = '3440f050428407457b0d106b54429de5' LIMIT 5;")
add_q("window", "Show the price difference between each order item and the average price of items in the same product category for delivered orders, ordered by order ID and item ID.", 
      "SELECT oi.order_id, p.product_category_name, oi.price, oi.price - AVG(oi.price) OVER (PARTITION BY p.product_category_name) as diff_from_cat_avg FROM order_items oi JOIN orders o ON oi.order_id = o.order_id JOIN products p ON oi.product_id = p.product_id WHERE o.order_status = 'delivered' AND p.product_category_name IS NOT NULL ORDER BY oi.order_id, oi.order_item_id LIMIT 5;")
add_q("window", "Rank product categories by total net revenue on delivered orders.", 
      "SELECT product_category_name, rev, RANK() OVER (ORDER BY rev DESC) as rank_num FROM (SELECT p.product_category_name, SUM(oi.price) as rev FROM order_items oi JOIN orders o ON oi.order_id = o.order_id JOIN products p ON oi.product_id = p.product_id WHERE o.order_status = 'delivered' AND p.product_category_name IS NOT NULL GROUP BY p.product_category_name) sub LIMIT 5;")
add_q("window", "For each customer state, rank the top customer city by customer count.", 
      "SELECT customer_state, customer_city, cnt FROM (SELECT customer_state, customer_city, COUNT(*) as cnt, ROW_NUMBER() OVER (PARTITION BY customer_state ORDER BY COUNT(*) DESC) as rn FROM customers GROUP BY customer_state, customer_city) sub WHERE rn = 1 ORDER BY cnt DESC LIMIT 5;")
add_q("window", "What is the cumulative sum of monthly delivered order count in 2017?", 
      "SELECT m, cnt, SUM(cnt) OVER (ORDER BY m) as cumulative_cnt FROM (SELECT DATE_TRUNC('month', order_purchase_timestamp) as m, COUNT(*) as cnt FROM orders WHERE order_status = 'delivered' AND order_purchase_timestamp >= '2017-01-01 00:00:00' AND order_purchase_timestamp < '2018-01-01 00:00:00' GROUP BY m) sub ORDER BY m;")
add_q("window", "What is the cumulative monthly net revenue on delivered orders in 2017?", 
      "SELECT m, rev, SUM(rev) OVER (ORDER BY m) as cumulative_rev FROM (SELECT DATE_TRUNC('month', o.order_purchase_timestamp) as m, SUM(oi.price) as rev FROM orders o JOIN order_items oi ON o.order_id = oi.order_id WHERE o.order_status = 'delivered' AND o.order_purchase_timestamp >= '2017-01-01 00:00:00' AND o.order_purchase_timestamp < '2018-01-01 00:00:00' GROUP BY m) sub ORDER BY m;")
add_q("window", "Show the lead next payment value for order payments of order '00010242fe8c59d542421444b163776e'.", 
      "SELECT payment_sequential, payment_value, LEAD(payment_value) OVER (ORDER BY payment_sequential) as next_val FROM order_payments WHERE order_id = '00010242fe8c59d542421444b163776e';")
add_q("window", "Show the lag previous payment value for order payments of order '00010242fe8c59d542421444b163776e'.", 
      "SELECT payment_sequential, payment_value, LAG(payment_value) OVER (ORDER BY payment_sequential) as prev_val FROM order_payments WHERE order_id = '00010242fe8c59d542421444b163776e';")
add_q("window", "Rank payment types by total collected payment value using DENSE_RANK.", 
      "SELECT payment_type, total_val, DENSE_RANK() OVER (ORDER BY total_val DESC) as rnk FROM (SELECT payment_type, SUM(payment_value) as total_val FROM order_payments GROUP BY payment_type) sub;")
add_q("window", "For each review score, show the percentage of total reviews it represents using a window sum.", 
      "SELECT review_score, COUNT(*) as cnt, COUNT(*)::float / SUM(COUNT(*)) OVER () as ratio FROM order_reviews GROUP BY review_score ORDER BY review_score DESC;")
add_q("window", "Rank sellers in the state of SP by net revenue on delivered orders.", 
      "SELECT s.seller_id, SUM(oi.price) as rev, RANK() OVER (ORDER BY SUM(oi.price) DESC) as seller_rank FROM order_items oi JOIN orders o ON oi.order_id = o.order_id JOIN sellers s ON oi.seller_id = s.seller_id WHERE o.order_status = 'delivered' AND s.seller_state = 'SP' GROUP BY s.seller_id LIMIT 5;")
add_q("window", "For each product category, find the top 1 heaviest product using ROW_NUMBER.", 
      "SELECT product_category_name, product_id, product_weight_g FROM (SELECT product_category_name, product_id, product_weight_g, ROW_NUMBER() OVER (PARTITION BY product_category_name ORDER BY product_weight_g DESC) as rn FROM products WHERE product_category_name IS NOT NULL AND product_weight_g IS NOT NULL) sub WHERE rn = 1 ORDER BY product_weight_g DESC LIMIT 5;")
add_q("window", "What is the dense rank of sellers in MG based on total items sold in delivered orders?", 
      "SELECT s.seller_id, COUNT(*) as item_cnt, DENSE_RANK() OVER (ORDER BY COUNT(*) DESC) as rnk FROM order_items oi JOIN orders o ON oi.order_id = o.order_id JOIN sellers s ON oi.seller_id = s.seller_id WHERE o.order_status = 'delivered' AND s.seller_state = 'MG' GROUP BY s.seller_id LIMIT 5;")
add_q("window", "Show the average review score per customer state alongside each state's customer count using window functions.", 
      "SELECT DISTINCT c.customer_state, AVG(r.review_score) OVER (PARTITION BY c.customer_state) as state_avg_score, COUNT(c.customer_id) OVER (PARTITION BY c.customer_state) as state_cust_cnt FROM customers c JOIN orders o ON c.customer_id = o.customer_id JOIN order_reviews r ON o.order_id = r.order_id ORDER BY state_cust_cnt DESC, c.customer_state LIMIT 5;")
add_q("window", "Rank the top 5 products by total net revenue on delivered orders using DENSE_RANK.", 
      "SELECT product_id, rev, DENSE_RANK() OVER (ORDER BY rev DESC) as product_rank FROM (SELECT product_id, SUM(price) as rev FROM order_items oi JOIN orders o ON oi.order_id = o.order_id WHERE o.order_status = 'delivered' GROUP BY product_id) sub ORDER BY rev DESC, product_id LIMIT 5;")
add_q("window", "For each payment type, rank the payment installments by transaction count.", 
      "SELECT payment_type, payment_installments, cnt, RANK() OVER (PARTITION BY payment_type ORDER BY cnt DESC) as installment_rank FROM (SELECT payment_type, payment_installments, COUNT(*) as cnt FROM order_payments GROUP BY payment_type, payment_installments) sub ORDER BY payment_type, cnt DESC LIMIT 5;")
add_q("window", "Calculate the difference between each seller's net revenue and the average seller net revenue in SP.", 
      "SELECT seller_id, rev, rev - AVG(rev) OVER () as diff_from_avg FROM (SELECT s.seller_id, SUM(oi.price) as rev FROM sellers s JOIN order_items oi ON s.seller_id = oi.seller_id JOIN orders o ON oi.order_id = o.order_id WHERE o.order_status = 'delivered' AND s.seller_state = 'SP' GROUP BY s.seller_id) sub ORDER BY rev DESC, seller_id LIMIT 5;")

# ==========================================
# CATEGORY 4: DATE ARITHMETIC (~24)
# ==========================================

add_q("date_math", "How many delivered orders were purchased in September 2017?", 
      "SELECT COUNT(*) FROM orders WHERE order_status = 'delivered' AND order_purchase_timestamp >= '2017-09-01 00:00:00' AND order_purchase_timestamp < '2017-10-01 00:00:00';")
add_q("date_math", "How many delivered orders were purchased in October 2017?", 
      "SELECT COUNT(*) FROM orders WHERE order_status = 'delivered' AND order_purchase_timestamp >= '2017-10-01 00:00:00' AND order_purchase_timestamp < '2017-11-01 00:00:00';")
add_q("date_math", "How many delivered orders were purchased in November 2017 (Black Friday month)?", 
      "SELECT COUNT(*) FROM orders WHERE order_status = 'delivered' AND order_purchase_timestamp >= '2017-11-01 00:00:00' AND order_purchase_timestamp < '2017-12-01 00:00:00';")
add_q("date_math", "How many delivered orders were purchased in December 2017?", 
      "SELECT COUNT(*) FROM orders WHERE order_status = 'delivered' AND order_purchase_timestamp >= '2017-12-01 00:00:00' AND order_purchase_timestamp < '2018-01-01 00:00:00';")
add_q("date_math", "What is the total net revenue from delivered orders purchased in Q1 2018 (Jan-Mar)?", 
      "SELECT SUM(oi.price) FROM order_items oi JOIN orders o ON oi.order_id = o.order_id WHERE o.order_status = 'delivered' AND o.order_purchase_timestamp >= '2018-01-01 00:00:00' AND o.order_purchase_timestamp < '2018-04-01 00:00:00';")
add_q("date_math", "What is the total net revenue from delivered orders purchased in Q2 2018 (Apr-Jun)?", 
      "SELECT SUM(oi.price) FROM order_items oi JOIN orders o ON oi.order_id = o.order_id WHERE o.order_status = 'delivered' AND o.order_purchase_timestamp >= '2018-04-01 00:00:00' AND o.order_purchase_timestamp < '2018-07-01 00:00:00';")
add_q("date_math", "What is the average delivery duration in days for delivered orders?", 
      "SELECT AVG(EXTRACT(DAY FROM (order_delivered_customer_date - order_purchase_timestamp))) FROM orders WHERE order_status = 'delivered' AND order_delivered_customer_date IS NOT NULL;")
add_q("date_math", "What is the maximum delivery duration in days recorded for a delivered order?", 
      "SELECT MAX(EXTRACT(DAY FROM (order_delivered_customer_date - order_purchase_timestamp))) FROM orders WHERE order_status = 'delivered' AND order_delivered_customer_date IS NOT NULL;")
add_q("date_math", "What is the minimum delivery duration in days for a delivered order?", 
      "SELECT MIN(EXTRACT(DAY FROM (order_delivered_customer_date - order_purchase_timestamp))) FROM orders WHERE order_status = 'delivered' AND order_delivered_customer_date IS NOT NULL AND order_delivered_customer_date >= order_purchase_timestamp;")
add_q("date_math", "How many delivered orders arrived late past the estimated delivery date?", 
      "SELECT COUNT(*) FROM orders WHERE order_status = 'delivered' AND order_delivered_customer_date > order_estimated_delivery_date;")
add_q("date_math", "How many delivered orders arrived on or before the estimated delivery date?", 
      "SELECT COUNT(*) FROM orders WHERE order_status = 'delivered' AND order_delivered_customer_date <= order_estimated_delivery_date;")
add_q("date_math", "What percentage of delivered orders were delivered late?", 
      "SELECT COUNT(CASE WHEN order_delivered_customer_date > order_estimated_delivery_date THEN 1 END)::float / COUNT(*) FROM orders WHERE order_status = 'delivered' AND order_delivered_customer_date IS NOT NULL;")
add_q("date_math", "What is the average delay in days for orders that were delivered late?", 
      "SELECT AVG(EXTRACT(DAY FROM (order_delivered_customer_date - order_estimated_delivery_date))) FROM orders WHERE order_status = 'delivered' AND order_delivered_customer_date > order_estimated_delivery_date;")
add_q("date_math", "What is the average delivery duration in days for customers in SP on delivered orders?", 
      "SELECT AVG(EXTRACT(DAY FROM (o.order_delivered_customer_date - o.order_purchase_timestamp))) FROM orders o JOIN customers c ON o.customer_id = c.customer_id WHERE o.order_status = 'delivered' AND c.customer_state = 'SP' AND o.order_delivered_customer_date IS NOT NULL;")
add_q("date_math", "What is the average delivery duration in days for customers in RJ on delivered orders?", 
      "SELECT AVG(EXTRACT(DAY FROM (o.order_delivered_customer_date - o.order_purchase_timestamp))) FROM orders o JOIN customers c ON o.customer_id = c.customer_id WHERE o.order_status = 'delivered' AND c.customer_state = 'RJ' AND o.order_delivered_customer_date IS NOT NULL;")
add_q("date_math", "What is the average delivery duration in days for customers in AM (Amazonas) on delivered orders?", 
      "SELECT AVG(EXTRACT(DAY FROM (o.order_delivered_customer_date - o.order_purchase_timestamp))) FROM orders o JOIN customers c ON o.customer_id = c.customer_id WHERE o.order_status = 'delivered' AND c.customer_state = 'AM' AND o.order_delivered_customer_date IS NOT NULL;")
add_q("date_math", "How many orders were approved more than 48 hours after purchase?", 
      "SELECT COUNT(*) FROM orders WHERE order_approved_at > order_purchase_timestamp + INTERVAL '48 hours';")
add_q("date_math", "How many orders were purchased on weekends (Saturday or Sunday)?", 
      "SELECT COUNT(*) FROM orders WHERE EXTRACT(DOW FROM order_purchase_timestamp) IN (0, 6);")
add_q("date_math", "How many orders were purchased on weekdays (Monday through Friday)?", 
      "SELECT COUNT(*) FROM orders WHERE EXTRACT(DOW FROM order_purchase_timestamp) BETWEEN 1 AND 5;")
add_q("date_math", "List the total count of delivered orders per year.", 
      "SELECT EXTRACT(YEAR FROM order_purchase_timestamp)::int as yr, COUNT(*) as cnt FROM orders WHERE order_status = 'delivered' GROUP BY yr ORDER BY yr;")
add_q("date_math", "List the monthly count of delivered orders in 2017.", 
      "SELECT EXTRACT(MONTH FROM order_purchase_timestamp)::int as mo, COUNT(*) as cnt FROM orders WHERE order_status = 'delivered' AND order_purchase_timestamp >= '2017-01-01 00:00:00' AND order_purchase_timestamp < '2018-01-01 00:00:00' GROUP BY mo ORDER BY mo;")
add_q("date_math", "What was the average review score for orders that were delivered late?", 
      "SELECT AVG(r.review_score) FROM order_reviews r JOIN orders o ON r.order_id = o.order_id WHERE o.order_status = 'delivered' AND o.order_delivered_customer_date > o.order_estimated_delivery_date;")
add_q("date_math", "What was the average review score for orders delivered on time or early?", 
      "SELECT AVG(r.review_score) FROM order_reviews r JOIN orders o ON r.order_id = o.order_id WHERE o.order_status = 'delivered' AND o.order_delivered_customer_date <= o.order_estimated_delivery_date;")
add_q("date_math", "How many reviews were answered more than 7 days after the review creation date?", 
      "SELECT COUNT(*) FROM order_reviews WHERE review_answer_timestamp > review_creation_date + INTERVAL '7 days';")

# ==========================================
# CATEGORY 5: UNANSWERABLE / REFUSALS (~24)
# ==========================================

add_q("unanswerable", "What is the average age of customers who bought pet products?", "REFUSE")
add_q("unanswerable", "What is the gender distribution of customers in Sao Paulo?", "REFUSE")
add_q("unanswerable", "Which product had the highest return rate?", "REFUSE")
add_q("unanswerable", "What was the discount code applied to order 00010242fe8c59d542421444b163776e?", "REFUSE")
add_q("unanswerable", "What is the name and email address of customer 06b8999e2fba1a1fbc88172c00ba8bc7?", "REFUSE")
add_q("unanswerable", "What is the phone number of seller 3440f050428407457b0d106b54429de5?", "REFUSE")
add_q("unanswerable", "What was the profit margin for products sold in 2018?", "REFUSE")
add_q("unanswerable", "What is the inventory stock count remaining for product 4244733e06e7ecb49c54057ccd6d10ee?", "REFUSE")
add_q("unanswerable", "Which marketing campaign generated the highest number of orders in 2017?", "REFUSE")
add_q("unanswerable", "What was the return reason for canceled orders?", "REFUSE")
add_q("unanswerable", "What is the salary or commission rate of sellers in Rio de Janeiro?", "REFUSE")
add_q("unanswerable", "How many customers used a coupon or promo voucher code?", "REFUSE")
add_q("unanswerable", "What is the delivery driver name for order 00010242fe8c59d542421444b163776e?", "REFUSE")
add_q("unanswerable", "What warehouse was product 4244733e06e7ecb49c54057ccd6d10ee shipped from?", "REFUSE")
add_q("unanswerable", "What is the cost of goods sold (COGS) for each item in order_items?", "REFUSE")
add_q("unanswerable", "Which customer visited the website most frequently without buying?", "REFUSE")
add_q("unanswerable", "What is the IP address of the customer who made order 00010242fe8c59d542421444b163776e?", "REFUSE")
add_q("unanswerable", "What is the manufacturing cost of products in the telefonia category?", "REFUSE")
add_q("unanswerable", "How many clicks did the cama_mesa_banho product page receive?", "REFUSE")
add_q("unanswerable", "What is the credit card number or CVV used for order payments?", "REFUSE")
add_q("unanswerable", "Which shipping carrier (FedEx, UPS, Correios) handled order 00010242fe8c59d542421444b163776e?", "REFUSE")
add_q("unanswerable", "What is the reorder rate of customers after 30 days?", "REFUSE")
add_q("unanswerable", "What was the customer service chat transcript for review 7bc24e225da01b7ac7f561825f696ed8?", "REFUSE")
add_q("unanswerable", "What is the net profit of Olist after deducting server and cloud costs?", "REFUSE")

def assign_splits():
    # Stratified split: 170 train, 30 dev, 40 test
    # By category proportions:
    # Aggregation (~96): 68 train, 12 dev, 16 test
    # Join (~60): 42 train, 8 dev, 10 test
    # Window (~20): 14 train, 3 dev, 3 test
    # Date Math (~24): 17 train, 3 dev, 4 test
    # Unanswerable (~24): 17 train, 4 dev, 7 test (or 17, 3, 4)
    # Total: ~224 items
    import collections
    by_cat = collections.defaultdict(list)
    for q in questions:
        by_cat[q["category"]].append(q)

    # Deterministic assignment
    for cat, items in by_cat.items():
        n = len(items)
        n_test = int(round(n * (40.0 / len(questions))))
        n_dev = int(round(n * (30.0 / len(questions))))
        n_train = n - n_dev - n_test

        for i, itm in enumerate(items):
            if i < n_train:
                itm["split"] = "train"
            elif i < n_train + n_dev:
                itm["split"] = "dev"
            else:
                itm["split"] = "test"

    # Exact adjustment to guarantee 40 test and 30 dev
    while sum(1 for q in questions if q["split"] == "test") > 40:
        for q in questions:
            if q["split"] == "test":
                q["split"] = "train"
                break

    while sum(1 for q in questions if q["split"] == "dev") > 30:
        for q in questions:
            if q["split"] == "dev":
                q["split"] = "train"
                break

    test_cnt = sum(1 for q in questions if q["split"] == "test")
    dev_cnt = sum(1 for q in questions if q["split"] == "dev")
    train_cnt = sum(1 for q in questions if q["split"] == "train")
    print(f"Final split: {train_cnt} train, {dev_cnt} dev, {test_cnt} test (Total: {len(questions)})")

def save():
    assign_splits()
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for q in questions:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")
    print(f"Saved {len(questions)} questions to {OUTPUT_FILE}")

if __name__ == "__main__":
    save()
