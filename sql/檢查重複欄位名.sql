WITH column_list AS (
    SELECT table_name, column_name
    FROM information_schema.columns
    WHERE table_schema = 'public'
    AND table_name IN ('產品規格', '包裝管標籤', '單位')
)
SELECT column_name, STRING_AGG(table_name, ', ') AS tables_with_column
FROM column_list
GROUP BY column_name
HAVING COUNT(DISTINCT table_name) > 1
ORDER BY column_name;
