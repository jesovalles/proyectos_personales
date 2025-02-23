DECLARE @FechaInicio DATE = '2012-01-01';
DECLARE @FechaFin DATE = '2013-12-31';
DECLARE @Condicion NVARCHAR(MAX);
DECLARE @Consulta NVARCHAR(MAX);

-- Construir la condición dinámica
SET @Condicion = CONCAT('OrderDate BETWEEN ''', @FechaInicio, ''' AND ''', @FechaFin, '''');

-- Construir la consulta dinámica
SET @Consulta = CONCAT(
    'SELECT 
		SalesOrderID, 
		OrderDate, 
		CustomerID, 
		TotalDue ',
    'FROM Sales.SalesOrderHeader ',
    'WHERE ', @Condicion, ' ',
    'ORDER BY OrderDate DESC'
);

-- Imprimir la consulta para verificar su contenido
PRINT @Consulta;

-- Ejecutar la consulta dinámica
EXEC sp_executesql @Consulta;
