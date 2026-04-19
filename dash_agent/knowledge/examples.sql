-- Example 1: Analysis of revenue by product category
SELECT 
    c.name AS category_name, 
    SUM(oi.quantity * oi.unit_price) AS category_revenue
FROM ecommerce.categories c
JOIN ecommerce.products p ON c.category_id = p.category_id
JOIN ecommerce.order_items oi ON p.product_id = oi.product_id
JOIN ecommerce.orders o ON oi.order_id = o.order_id
WHERE o.status != 'Cancelled'
GROUP BY c.name
ORDER BY category_revenue DESC;

-- Example 2: Customer lifetime value top list
SELECT 
    u.email, 
    SUM(o.total_amount) AS ltv
FROM ecommerce.users u
JOIN ecommerce.orders o ON u.user_id = o.user_id
WHERE o.status != 'Cancelled'
GROUP BY u.email
ORDER BY ltv DESC
LIMIT 10;

-- Example 3: Shipping performance by carrier
SELECT 
    carrier, 
    AVG(estimated_delivery - CAST(order_date AS DATE)) AS avg_days_to_deliver,
    COUNT(*) as total_shipped
FROM ecommerce.shipping_details sd
JOIN ecommerce.orders o ON sd.order_id = o.order_id
WHERE shipping_status = 'Delivered'
GROUP BY carrier;

-- Example 4: Month-over-Month Revenue Growth
WITH monthly_sales AS (
    SELECT 
        DATE_TRUNC('month', order_date) AS month,
        SUM(total_amount) AS revenue
    FROM ecommerce.orders
    WHERE status != 'Cancelled'
    GROUP BY 1
)
SELECT 
    month,
    revenue,
    LAG(revenue) OVER (ORDER BY month) AS prev_month_revenue,
    ((revenue - LAG(revenue) OVER (ORDER BY month)) / NULLIF(LAG(revenue) OVER (ORDER BY month), 0)) * 100 AS growth_pct
FROM monthly_sales;

-- Example 5: Products with high ratings but low sales (Potential missed opportunity)
SELECT 
    p.name,
    AVG(r.rating) as avg_rating,
    COUNT(DISTINCT oi.order_id) as sales_count,
    p.stock_quantity
FROM ecommerce.products p
LEFT JOIN ecommerce.reviews r ON p.product_id = r.product_id
LEFT JOIN ecommerce.order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_id, p.name, p.stock_quantity
HAVING AVG(r.rating) >= 4 AND COUNT(DISTINCT oi.order_id) < 5
ORDER BY avg_rating DESC;

-- Example 6: Payment method distribution for large orders (>$500)
SELECT 
    payment_method,
    COUNT(*) as transaction_count,
    SUM(amount) as total_collected
FROM ecommerce.payments
WHERE amount > 500 AND status = 'Success'
GROUP BY payment_method
ORDER BY total_collected DESC;

-- Example 7: Daily order volume trends over the last 30 days
SELECT 
    CAST(order_date AS DATE) as day,
    COUNT(*) as order_count,
    SUM(total_amount) as daily_revenue
FROM ecommerce.orders
WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY day
ORDER BY day DESC;

-- Example 8: Identifying "at-risk" customers (No orders in the last 3 months)
SELECT 
    u.first_name, u.last_name, u.email,
    MAX(o.order_date) as last_order_date
FROM ecommerce.users u
JOIN ecommerce.orders o ON u.user_id = o.user_id
GROUP BY u.user_id, u.first_name, u.last_name, u.email
HAVING MAX(o.order_date) < CURRENT_DATE - INTERVAL '90 days'
ORDER BY last_order_date ASC;

-- Example 9: Shipping Status Summary by Order Value
SELECT 
    shipping_status,
    COUNT(*) as order_count,
    AVG(total_amount) as avg_order_value
FROM ecommerce.shipping_details sd
JOIN ecommerce.orders o ON sd.order_id = o.order_id
GROUP BY shipping_status;
