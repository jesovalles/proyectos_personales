-- Funcion de ventana OVER PARTITION
SELECT 
    soh.CustomerID,                          -- Selecciona el CustomerID de la tabla SalesOrderHeader
    sod.SalesOrderID,                        -- Selecciona el SalesOrderID de la tabla SalesOrderDetail
    sod.OrderQty,                            -- Selecciona la cantidad de productos en la orden de venta
    sod.LineTotal,                           -- Selecciona el total de la línea (valor de la venta)
    SUM(sod.LineTotal) OVER (PARTITION BY soh.CustomerID ORDER BY sod.SalesOrderID) AS TotalVentasPorCliente -- Calcula la suma total de las ventas por cliente
FROM 
    Sales.SalesOrderDetail sod               -- Fuente de datos de detalles de las órdenes de venta
JOIN 
    Sales.SalesOrderHeader soh              -- Hacemos un JOIN con la tabla SalesOrderHeader
    ON sod.SalesOrderID = soh.SalesOrderID  -- Relacionamos las órdenes de venta entre ambas tablas (por SalesOrderID)
ORDER BY 
    soh.CustomerID, sod.SalesOrderID;       -- Ordenamos el resultado por CustomerID y SalesOrderID

-- Funcion de ventana ROW NUMBER
SELECT 
    soh.CustomerID,
    sod.SalesOrderID,
    sod.OrderQty,
    sod.LineTotal,
    ROW_NUMBER() OVER (PARTITION BY soh.CustomerID ORDER BY sod.SalesOrderID) AS RowNum -- Asigna un número único y secuencial a cada fila por CustomerID
FROM 
    Sales.SalesOrderDetail sod
JOIN 
    Sales.SalesOrderHeader soh ON sod.SalesOrderID = soh.SalesOrderID
ORDER BY 
    soh.CustomerID, sod.SalesOrderID;

-- Funcion de ventana LAG
SELECT 
    soh.CustomerID,
    YEAR(soh.OrderDate) AS Año,
    MONTH(soh.OrderDate) AS Mes,
    SUM(sod.LineTotal) AS TotalVentas,
    LAG(SUM(sod.LineTotal)) OVER (PARTITION BY soh.CustomerID ORDER BY YEAR(soh.OrderDate), MONTH(soh.OrderDate)) AS TotalVentasAnterior,
    SUM(sod.LineTotal) - LAG(SUM(sod.LineTotal)) OVER (PARTITION BY soh.CustomerID ORDER BY YEAR(soh.OrderDate), MONTH(soh.OrderDate)) AS DiferenciaVentas
FROM 
    Sales.SalesOrderDetail sod
JOIN 
    Sales.SalesOrderHeader soh ON sod.SalesOrderID = soh.SalesOrderID
GROUP BY 
    soh.CustomerID, YEAR(soh.OrderDate), MONTH(soh.OrderDate)
ORDER BY 
    soh.CustomerID, Año, Mes;