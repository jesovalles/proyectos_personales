-- Definimos los CTEs m�ltiples
WITH ProductCategoryInfo AS (
    -- CTE 1: Informaci�n de productos y categor�as
    SELECT 
        p.ProductID,
        p.Name AS ProductName,
        pc.Name AS CategoryName,
        p.ListPrice AS UnitPrice
    FROM 
        Production.Product AS p
    INNER JOIN 
        Production.ProductSubcategory AS ps
        ON p.ProductSubcategoryID = ps.ProductSubcategoryID
    INNER JOIN 
        Production.ProductCategory AS pc
        ON ps.ProductCategoryID = pc.ProductCategoryID
),
SalesInfo AS (
    -- CTE 2: Informaci�n de ventas por producto
    SELECT 
        sod.ProductID,
        SUM(sod.LineTotal) AS TotalSales
    FROM 
        Sales.SalesOrderDetail AS sod
    INNER JOIN 
        Sales.SalesOrderHeader AS soh
        ON sod.SalesOrderID = soh.SalesOrderID
    WHERE 
        YEAR(soh.OrderDate) = 2013  -- Filtramos las ventas del a�o 2013
    GROUP BY 
        sod.ProductID
)
-- Consulta final utilizando los CTEs
SELECT 
    pci.ProductName,
    pci.CategoryName,
    pci.UnitPrice,
    COALESCE(si.TotalSales, 0) AS TotalSales
FROM 
    ProductCategoryInfo AS pci
LEFT JOIN 
    SalesInfo AS si
    ON pci.ProductID = si.ProductID
ORDER BY 
    pci.CategoryName, TotalSales DESC;
