-- Crear la tabla temporal
CREATE TABLE #TempSalesBySalesPerson (
    SalesPersonID INT,
    SalesPersonName NVARCHAR(100),
    Year INT,
    TotalSales MONEY
);

-- Insertar datos en la tabla temporal
INSERT INTO #TempSalesBySalesPerson (SalesPersonID, SalesPersonName, Year, TotalSales)
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
    YEAR(soh.OrderDate) = '2013' -- Solo ordenes del 2013
GROUP BY 
    sp.BusinessEntityID, 
    p.FirstName, 
    p.LastName, 
    YEAR(soh.OrderDate);

-- Consultar datos de la tabla temporal
SELECT * 
FROM #TempSalesBySalesPerson
WHERE TotalSales > 10000;

-- (Opcional) Eliminar manualmente la tabla temporal
DROP TABLE #TempSalesBySalesPerson;
