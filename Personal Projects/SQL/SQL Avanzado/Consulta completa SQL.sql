-- Obtener un informe que muestre la cantidad total de ventas por cada vendedor, desglosado por año desde el 2013
-- y que las ventas hayan sido mayores a 500k

SELECT 
    sp.BusinessEntityID AS SalesPersonID,
    p.FirstName + ' ' + p.LastName AS SalesPersonName,
    YEAR(soh.OrderDate) AS Year,
    SUM(sod.LineTotal) AS TotalSales
FROM 
    Sales.SalesOrderHeader AS soh
INNER JOIN 
    Sales.SalesOrderDetail AS sod
    ON soh.SalesOrderID = sod.SalesOrderID
INNER JOIN 
    Production.Product AS prod
    ON sod.ProductID = prod.ProductID
INNER JOIN 
    Production.ProductSubcategory AS subcat
    ON prod.ProductSubcategoryID = subcat.ProductSubcategoryID
INNER JOIN 
    Production.ProductCategory AS cat
    ON subcat.ProductCategoryID = cat.ProductCategoryID
INNER JOIN 
    Sales.SalesPerson AS sp
    ON soh.SalesPersonID = sp.BusinessEntityID
INNER JOIN 
    Person.Person AS p
    ON sp.BusinessEntityID = p.BusinessEntityID
WHERE 
    YEAR(soh.OrderDate) >= '2013' -- Filtrar por órdenes desde 2013
GROUP BY 
    sp.BusinessEntityID, 
    p.FirstName, 
    p.LastName, 
    YEAR(soh.OrderDate)
HAVING 
    SUM(sod.LineTotal) > 500000 -- Mostrar solo vendedores con más de $500.000 en ventas
ORDER BY 
    YEAR(soh.OrderDate) ASC, 
    TotalSales DESC;
