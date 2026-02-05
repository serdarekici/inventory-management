-- SQL TEMPLATE (placeholders only)
-- Replace <...> with your own schema/table names.
-- Never hardcode credentials in SQL files.

SELECT PartNum, Description, TransactionDate, Quantity, OpenOrderQty, UnitPrice, UnitCost
FROM <SCHEMA>.<SALES_TABLE>
WHERE TransactionDate >= DATEADD(month, -36, GETDATE());

SELECT PartNum, Description, OnHandQty, UnitCost, LeadTime, MinOrderQty, TotalPOQty
FROM <SCHEMA>.<INVENTORY_TABLE>;
