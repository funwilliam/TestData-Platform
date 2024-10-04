WITH AllModelNumbers AS (
    SELECT "型號" AS "型號" FROM "型號"
    UNION
    SELECT "主型號" AS "型號" FROM "產品規格"
    UNION
    SELECT "型號" AS "型號" FROM "包裝管標籤"
    UNION
    SELECT "型號" AS "型號" FROM "單位"
)
SELECT 
    amn."型號", 
    CASE WHEN mo."型號" IS NOT NULL THEN 'v' ELSE NULL END AS "型號表_存在狀態",
    CASE WHEN ps."主型號" IS NOT NULL THEN 'v' ELSE NULL END AS "產品規格_存在狀態",
    CASE WHEN pt."型號" IS NOT NULL THEN 'v' ELSE NULL END AS "包裝管標籤_存在狀態",
    CASE WHEN u."型號" IS NOT NULL THEN 'v' ELSE NULL END AS "單位_存在狀態"
FROM 
    AllModelNumbers amn
LEFT JOIN 
    "型號" mo ON amn."型號" = mo."型號"
LEFT JOIN 
    "產品規格" ps ON amn."型號" = ps."主型號"
LEFT JOIN 
    "包裝管標籤" pt ON amn."型號" = pt."型號"
LEFT JOIN 
    "單位" u ON amn."型號" = u."型號"
ORDER BY 
    amn."型號";