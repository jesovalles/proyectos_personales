-- Definir el CTE recursivo
WITH EmployeeHierarchy AS (
    -- Ancla: Empezamos con el gerente principal (por ejemplo, con BusinessEntityID = 1)
    SELECT 
        e.BusinessEntityID AS EmployeeID,
        e.ManagerID,
        p.FirstName + ' ' + p.LastName AS EmployeeName,
        0 AS HierarchyLevel -- Nivel jerárquico inicial
    FROM 
        HumanResources.Employee AS e
    INNER JOIN 
        Person.Person AS p
        ON e.BusinessEntityID = p.BusinessEntityID
    WHERE 
        e.ManagerID IS NULL -- Encontrar el gerente principal

    UNION ALL

    -- Parte recursiva: Encontrar los empleados reportando a cada empleado en el CTE
    SELECT 
        e.BusinessEntityID AS EmployeeID,
        e.ManagerID,
        p.FirstName + ' ' + p.LastName AS EmployeeName,
        eh.HierarchyLevel + 1 AS HierarchyLevel
    FROM 
        HumanResources.Employee AS e
    INNER JOIN 
        Person.Person AS p
        ON e.BusinessEntityID = p.BusinessEntityID
    INNER JOIN 
        EmployeeHierarchy AS eh
        ON e.ManagerID = eh.EmployeeID
)
-- Consultar la jerarquía completa
SELECT 
    EmployeeID,
    ManagerID,
    EmployeeName,
    HierarchyLevel
FROM 
    EmployeeHierarchy
ORDER BY 
    HierarchyLevel, 
	EmployeeName;
