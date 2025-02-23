DECLARE @FechaInicio DATE = '2012-01-01';
DECLARE @FechaFin DATE = '2013-12-31';
DECLARE @Condicion NVARCHAR(MAX);
DECLARE @Consulta NVARCHAR(MAX);

-- Construir la condici�n din�mica
SET @Condicion = CONCAT('OrderDate BETWEEN ''', @FechaInicio, ''' AND ''', @FechaFin, '''');

-- Construir la consulta din�mica
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

-- Ejecutar la consulta din�mica
EXEC sp_executesql @Consulta;
