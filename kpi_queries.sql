-- ================================================
-- QUERY 1: Overall Business KPIs
-- ================================================
SELECT
    COUNT(DISTINCT o.order_id)              AS total_orders,
    COUNT(DISTINCT o.customer_id)           AS total_customers,
    ROUND(SUM(oi.price), 2)                 AS total_revenue,
    ROUND(AVG(oi.price), 2)                 AS avg_order_value,
    ROUND(SUM(oi.freight_value), 2)         AS total_freight
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered';


-- ================================================
-- QUERY 2: Revenue by State
-- ================================================
SELECT
    c.customer_state                        AS state,
    COUNT(DISTINCT o.order_id)              AS total_orders,
    ROUND(SUM(oi.price), 2)                 AS revenue,
    ROUND(AVG(oi.price), 2)                 AS avg_order_value
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN customers c    ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_state
ORDER BY revenue DESC;


-- ================================================
-- QUERY 3: Delivery Delay vs Review Score (KEY INSIGHT)
-- ================================================
SELECT
    r.review_score,
    COUNT(*)                                AS total_orders,
    ROUND(AVG(
        JULIANDAY(o.order_delivered_customer_date) -
        JULIANDAY(o.order_purchase_timestamp)
    ), 1)                                   AS avg_delivery_days
FROM orders o
JOIN reviews r ON o.order_id = r.order_id
WHERE o.order_delivered_customer_date IS NOT NULL
GROUP BY r.review_score
ORDER BY r.review_score;


-- ================================================
-- QUERY 4: Top 10 Product Categories by Revenue
-- ================================================
SELECT
    COALESCE(cat.english, p.product_category_name, 'Unknown') AS category,
    COUNT(DISTINCT oi.order_id)             AS total_orders,
    ROUND(SUM(oi.price), 2)                 AS revenue,
    ROUND(AVG(oi.price), 2)                 AS avg_price,
    ROUND(AVG(r.review_score), 2)           AS avg_review_score
FROM order_items oi
JOIN products p    ON oi.product_id = p.product_id
JOIN orders o      ON oi.order_id = o.order_id
JOIN reviews r     ON o.order_id = r.order_id
LEFT JOIN categories cat
    ON p.product_category_name = cat.product_category_name
WHERE o.order_status = 'delivered'
GROUP BY category
ORDER BY revenue DESC
LIMIT 10;


-- ================================================
-- QUERY 5: Seller Performance
-- ================================================
SELECT
    oi.seller_id,
    s.seller_state,
    COUNT(DISTINCT oi.order_id)             AS total_orders,
    ROUND(SUM(oi.price), 2)                 AS total_revenue,
    ROUND(AVG(r.review_score), 2)           AS avg_review_score
FROM order_items oi
JOIN sellers s ON oi.seller_id = s.seller_id
JOIN orders o  ON oi.order_id = o.order_id
JOIN reviews r ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
GROUP BY oi.seller_id, s.seller_state
ORDER BY total_revenue DESC;