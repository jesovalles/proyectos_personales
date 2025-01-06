-- Subconsulta en la cláusula FROM
SELECT 
    ProductID,
    ProductName,
    TotalSales
FROM 
    (
        -- Subconsulta: Obtiene ventas totales por producto
        SELECT 
            p.ProductID,
            p.Name AS ProductName,
            SUM(sod.LineTotal) AS TotalSales
        FROM 
            Production.Product AS p
        JOIN 
            Sales.SalesOrderDetail AS sod
            ON p.ProductID = sod.ProductID
        GROUP BY 
            p.ProductID, p.Name
    ) AS ProductSales
WHERE 
    TotalSales > 1000 -- Filtramos los productos con ventas mayores a 1000
ORDER BY 
    TotalSales DESC;
