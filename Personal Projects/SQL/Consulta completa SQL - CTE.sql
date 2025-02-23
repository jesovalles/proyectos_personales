-- Definición del CTE
WITH SalesBySalesPersonCTE AS (
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
        cat.Name = 'Bikes' -- Filtrar solo productos de la categoría Bicicletas
    GROUP BY 
        sp.BusinessEntityID, 
        p.FirstName, 
        p.LastName, 
        YEAR(soh.OrderDate)
)
-- Consulta final usando el CTE
SELECT 
    SalesPersonID,
    SalesPersonName,
    Year,
    TotalSales
FROM 
    SalesBySalesPersonCTE
WHERE 
    TotalSales > 50000 -- Filtrar vendedores con ventas mayores a $50,000
ORDER BY 
    TotalSales DESC;
