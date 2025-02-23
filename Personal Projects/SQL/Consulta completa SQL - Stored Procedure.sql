CREATE PROCEDURE GetSalesReport
    @StartDate DATE,               -- Fecha de inicio del rango
    @EndDate DATE,                 -- Fecha de fin del rango
    @CustomerID INT = NULL,        -- ID del cliente (opcional)
    @OrderBy NVARCHAR(50) = 'TotalSales DESC' -- Columna para ordenar (opcional)
AS
BEGIN
    SET NOCOUNT ON;

    -- Validación de parámetros
    IF @StartDate IS NULL OR @EndDate IS NULL
    BEGIN
        RAISERROR ('Debe proporcionar un rango de fechas válido.', 16, 1);
        RETURN;
    END

    -- Consulta principal con filtros dinámicos
    DECLARE @SQL NVARCHAR(MAX);

    SET @SQL = '
        SELECT 
            P.ProductID,
            P.Name AS ProductName,
            SUM(SOD.OrderQty) AS TotalQuantity,
            SUM(SOD.LineTotal) AS TotalSales,
            COUNT(DISTINCT SOH.SalesOrderID) AS TotalOrders
        FROM 
            Sales.SalesOrderHeader AS SOH
        INNER JOIN 
            Sales.SalesOrderDetail AS SOD ON SOH.SalesOrderID = SOD.SalesOrderID
        INNER JOIN 
            Production.Product AS P ON SOD.ProductID = P.ProductID
        WHERE 
            SOH.OrderDate BETWEEN @StartDate AND @EndDate ' +
            CASE WHEN @CustomerID IS NOT NULL THEN 'AND SOH.CustomerID = @CustomerID ' ELSE '' END + '
        GROUP BY 
            P.ProductID, P.Name
        ORDER BY ' + @OrderBy + ';
    ';

    -- Ejecutar la consulta dinámica
    EXEC sp_executesql 
        @SQL, 
        N'@StartDate DATE, @EndDate DATE, @CustomerID INT', 
        @StartDate, @EndDate, @CustomerID;
END;

-- Obtener ventas para todos los clientes entre enero y marzo de 2013
EXEC GetSalesReport '2013-01-01', '2013-03-31';

-- Obtener ventas ordenadas por cantidad total (TotalQuantity) en orden ascendente:
EXEC GetSalesReport '2013-01-01', '2013-03-31', NULL, 'TotalQuantity ASC';

-- Eliminar SP
DROP PROCEDURE GetSalesReport;



