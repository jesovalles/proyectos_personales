-- Crear la función escalar para calcular el impuesto
CREATE FUNCTION dbo.CalcularImpuesto (@monto DECIMAL)
RETURNS DECIMAL
AS
BEGIN
    DECLARE @impuesto DECIMAL;
    SET @impuesto = @monto * 0.15;  -- 15% de impuesto
    RETURN @impuesto;
END;
GO

-- Llamar a la función escalar
SELECT 
    p.ProductID,
    p.Name AS ProductName,
    sod.LineTotal,
    dbo.CalcularImpuesto(sod.LineTotal) AS ImpuestoCalculado
FROM 
    Sales.SalesOrderDetail AS sod
JOIN 
    Production.Product AS p
    ON sod.ProductID = p.ProductID;

-- Eliminar funcion
DROP FUNCTION IF EXISTS dbo.CalcularImpuesto;
