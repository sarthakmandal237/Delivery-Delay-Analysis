/* ============================================================
   DELIVERY DELAY ANALYSIS — SQL QUERIES
   Table used: orders
   Columns: order_id, order_date, hub, courier_partner, distance_km,
            order_value_inr, promised_delivery_date, actual_delivery_date,
            delay_days, is_late, order_weekday, order_month
   ============================================================ */


/* ------------------------------------------------------------
   SECTION A — SIMPLE QUERIES
   (basic aggregation, no window functions — the "quick answers")
   ------------------------------------------------------------ */

-- A1. What % of all orders are late overall?
SELECT 
    COUNT(*) AS total_orders,
    SUM(is_late) AS late_orders,
    ROUND(100.0 * SUM(is_late) / COUNT(*), 1) AS late_pct
FROM orders;


-- A2. Which hub has the worst late-delivery rate?
SELECT 
    hub,
    COUNT(*) AS total_orders,
    SUM(is_late) AS late_orders,
    ROUND(100.0 * SUM(is_late) / COUNT(*), 1) AS late_pct
FROM orders
GROUP BY hub
ORDER BY late_pct DESC;


-- A3. Which courier partner has the worst late-delivery rate?
SELECT 
    courier_partner,
    COUNT(*) AS total_orders,
    SUM(is_late) AS late_orders,
    ROUND(100.0 * SUM(is_late) / COUNT(*), 1) AS late_pct
FROM orders
GROUP BY courier_partner
ORDER BY late_pct DESC;


-- A4. Are weekend orders more likely to be late than weekday orders?
SELECT 
    CASE WHEN order_weekday IN ('Saturday','Sunday') THEN 'Weekend' ELSE 'Weekday' END AS day_type,
    COUNT(*) AS total_orders,
    ROUND(100.0 * SUM(is_late) / COUNT(*), 1) AS late_pct
FROM orders
GROUP BY day_type;


/* ------------------------------------------------------------
   SECTION B — COMPLEX QUERIES
   (CTEs + window functions — the "deeper analysis" queries
   that show you can go beyond basic GROUP BY)
   ------------------------------------------------------------ */

-- B1. Rank the WORST hub + courier COMBINATIONS 
--     (not just hub alone, or courier alone — the actual pairing that fails most)
--     Uses: CTE, HAVING (to ignore tiny/noisy combos), RANK() window function
WITH hub_courier_stats AS (
    SELECT 
        hub,
        courier_partner,
        COUNT(*) AS total_orders,
        SUM(is_late) AS late_orders,
        ROUND(100.0 * SUM(is_late) / COUNT(*), 1) AS late_pct,
        ROUND(AVG(CASE WHEN is_late = 1 THEN delay_days END), 1) AS avg_delay_when_late
    FROM orders
    GROUP BY hub, courier_partner
    HAVING COUNT(*) >= 50          -- ignore combinations with too few orders to trust
)
SELECT 
    *,
    RANK() OVER (ORDER BY late_pct DESC) AS worst_combo_rank
FROM hub_courier_stats
ORDER BY late_pct DESC
LIMIT 10;


-- B2. Month-over-month delay trend WITH a rolling 3-month average
--     (shows if the problem is getting better/worse, smoothed to remove monthly noise)
--     Uses: window function with ROWS BETWEEN frame
SELECT 
    order_month,
    COUNT(*) AS total_orders,
    SUM(is_late) AS late_orders,
    ROUND(100.0 * SUM(is_late) / COUNT(*), 1) AS late_pct,
    ROUND(AVG(100.0 * SUM(is_late) / COUNT(*)) OVER (
        ORDER BY MIN(order_date) 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 1) AS rolling_3month_avg_late_pct
FROM orders
GROUP BY order_month
ORDER BY MIN(order_date);


-- B3. Distance-band analysis: does distance actually drive delay, or is it a hub/courier issue?
--     Uses: CASE for binning + CTE, isolates distance as a variable
WITH distance_bands AS (
    SELECT *,
        CASE 
            WHEN distance_km < 100 THEN '1. Under 100km'
            WHEN distance_km < 250 THEN '2. 100-250km'
            WHEN distance_km < 400 THEN '3. 250-400km'
            ELSE '4. Over 400km'
        END AS distance_band
    FROM orders
)
SELECT 
    distance_band,
    COUNT(*) AS total_orders,
    ROUND(100.0 * SUM(is_late) / COUNT(*), 1) AS late_pct,
    ROUND(AVG(order_value_inr), 0) AS avg_order_value
FROM distance_bands
GROUP BY distance_band
ORDER BY distance_band;