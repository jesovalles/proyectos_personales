-- Crear una tabla temporal para almacenar mensajes
CREATE TABLE #MensajesClientes (
    CustomerID INT,
    Mensaje NVARCHAR(100)
);

-- Declarar variables para el cursor
DECLARE @CustomerID INT;
DECLARE @NombreCliente NVARCHAR(50);

-- Declarar el cursor
DECLARE CursorClientes CURSOR FOR
SELECT 
    CustomerID,
    PersonID -- Suponiendo que esta columna representa el nombre o ID de una persona
FROM 
    Sales.Customer;

-- Abrir el cursor
OPEN CursorClientes;

-- Obtener la primera fila
FETCH NEXT FROM CursorClientes INTO @CustomerID, @NombreCliente;

-- Recorrer cada fila
WHILE @@FETCH_STATUS = 0
BEGIN
    -- Insertar un mensaje personalizado en la tabla temporal
    INSERT INTO #MensajesClientes (CustomerID, Mensaje)
    VALUES (@CustomerID, CONCAT('Hola, cliente con ID: ', @CustomerID, '. Gracias por ser parte de nuestra empresa.'));

    -- Obtener la siguiente fila
    FETCH NEXT FROM CursorClientes INTO @CustomerID, @NombreCliente;
END;

-- Cerrar y liberar el cursor
CLOSE CursorClientes;
DEALLOCATE CursorClientes;

-- Ver el contenido de la tabla temporal
SELECT * FROM #MensajesClientes;

-- Limpiar la tabla temporal
DROP TABLE #MensajesClientes;
