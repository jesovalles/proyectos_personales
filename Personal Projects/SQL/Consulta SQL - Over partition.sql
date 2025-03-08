SELECT 
    e.BusinessEntityID,
    p.FirstName,
    p.LastName,
    d.Name AS Department,
    s.Rate AS Salary,
    AVG(s.Rate) OVER (PARTITION BY d.Name) AS AvgSalaryByDept -- Calcula el salario promedio por departamento discretizando por empleado
FROM HumanResources.Employee e
INNER JOIN Person.Person p ON e.BusinessEntityID = p.BusinessEntityID
INNER JOIN HumanResources.EmployeeDepartmentHistory edh ON e.BusinessEntityID = edh.BusinessEntityID
INNER JOIN HumanResources.Department d ON edh.DepartmentID = d.DepartmentID
INNER JOIN HumanResources.EmployeePayHistory s ON e.BusinessEntityID = s.BusinessEntityID;
