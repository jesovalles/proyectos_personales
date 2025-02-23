-- Consultas con donde un campo es un JSON
SELECT * FROM dbo.Productos;

-- Consulta donde se extrae el valor de claves especificas
SELECT 
    ProductoID,
    Nombre,
    JSON_VALUE(Detalles, '$.Precio') AS Precio,
    JSON_VALUE(Detalles, '$.Stock') AS Stock
FROM Productos;

-- Consulta donde se extrae el valor de claves especificas de un JSON anidado
SELECT 
    ProductoID,
    Nombre,
    JSON_VALUE(Detalles, '$.Especificaciones.RAM') AS RAM,
    JSON_VALUE(Detalles, '$.Especificaciones.Procesador') AS Procesador
FROM Productos;

-- Consulta de despliegue de varios json
SELECT 
    ProductoID,
    Nombre,
    JSON_VALUE(Detalles, '$.Precio') AS Precio,
    JSON_VALUE(Detalles, '$.Stock') AS Stock,
    JSON_VALUE(Detalles, '$.Especificaciones.RAM') AS RAM,
    JSON_VALUE(Detalles, '$.Especificaciones.Procesador') AS Procesador
FROM Productos;



