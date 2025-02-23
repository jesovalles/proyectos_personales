SELECT 
    COUNT(*) AS TotalOrders,             -- Cuenta el número total de órdenes
    SUM(sod.LineTotal) AS TotalSales,    -- Suma las ventas totales
    AVG(sod.LineTotal) AS AvgSales,      -- Calcula el promedio de ventas
    MAX(sod.LineTotal) AS MaxSale,       -- Encuentra la venta más alta
    MIN(sod.LineTotal) AS MinSale        -- Encuentra la venta más baja
FROM 
    Sales.SalesOrderDetail AS sod;

SELECT 
    LEN(p.Name) AS NameLength,                  -- Longitud del nombre del producto
    SUBSTRING(p.Name, 1, 5) AS NamePrefix,      -- Extrae los primeros 5 caracteres del nombre del producto
    CONCAT(p.Name, ' - ', p.Color) AS FullName, -- Concatenación de nombre y color
    UPPER(p.Name) AS UpperName,                 -- Convierte el nombre a mayúsculas
    LOWER(p.Name) AS LowerName,                 -- Convierte el nombre a minúsculas
    TRIM(p.Name) AS TrimmedName                 -- Elimina los espacios en blanco de ambos extremos
FROM 
    Production.Product AS p;

SELECT 
    GETDATE() AS CurrentDate,                -- Obtiene la fecha y hora actuales
    DATEADD(DAY, 7, GETDATE()) AS NextWeek,  -- Suma 7 días a la fecha actual
    DATEDIFF(DAY, sod.OrderDate, GETDATE()) AS DaysSinceOrder, -- Calcula los días desde la fecha de la orden
    YEAR(sod.OrderDate) AS OrderYear,        -- Extrae el año de la fecha de la orden
    MONTH(sod.OrderDate) AS OrderMonth,      -- Extrae el mes de la fecha de la orden
    DAY(sod.OrderDate) AS OrderDay           -- Extrae el día de la fecha de la orden
FROM 
    Sales.SalesOrderDetail AS sod;

SELECT 
    ABS(sod.LineTotal) AS AbsoluteValue,          -- Valor absoluto de las ventas
    ROUND(sod.LineTotal, 2) AS RoundedSales,      -- Redondea las ventas a 2 decimales
    CEILING(sod.LineTotal) AS CeilingSales,       -- Redondea hacia arriba
    FLOOR(sod.LineTotal) AS FloorSales,           -- Redondea hacia abajo
    PI() AS PiValue                               -- Valor de pi
FROM 
    Sales.SalesOrderDetail AS sod;

SELECT 
    p.ProductID,
    p.Name AS ProductName,
    SUM(sod.LineTotal) AS TotalSales,
    CASE 
        WHEN SUM(sod.LineTotal) > 10000 THEN 'High Sales'
        WHEN SUM(sod.LineTotal) BETWEEN 5000 AND 10000 THEN 'Medium Sales'
        ELSE 'Low Sales'
    END AS SalesCategory
FROM 
    Production.Product AS p
JOIN 
    Sales.SalesOrderDetail AS sod
    ON p.ProductID = sod.ProductID
GROUP BY 
    p.ProductID, p.Name
ORDER BY 
    TotalSales DESC;

SELECT 
    CAST(sod.LineTotal AS INT) AS LineTotalInt,        -- Convierte LineTotal a entero
    CONVERT(VARCHAR, sod.OrderDate, 103) AS OrderDateStr  -- Convierte la fecha a formato de cadena
FROM 
    Sales.SalesOrderDetail AS sod;
