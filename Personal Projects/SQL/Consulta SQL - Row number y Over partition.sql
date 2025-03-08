WITH EmployeeSalaryHistory AS (
    SELECT 
        e.BusinessEntityID,
        p.FirstName,
        p.LastName,
        s.Rate AS Salary,
        s.PayFrequency,
        s.ModifiedDate,
        ROW_NUMBER() OVER (
            PARTITION BY e.BusinessEntityID 
            ORDER BY s.ModifiedDate DESC
        ) AS SalaryChangeRank -- se enumeran los ID empleados desde la fecha mas reciente a la mas antigua
    FROM HumanResources.Employee e
    INNER JOIN HumanResources.EmployeePayHistory s 
        ON e.BusinessEntityID = s.BusinessEntityID
    INNER JOIN Person.Person p 
        ON e.BusinessEntityID = p.BusinessEntityID
)
SELECT * 
FROM EmployeeSalaryHistory
WHERE SalaryChangeRank = 1  --se obtiene el salario más reciente por empleado
ORDER BY LastName, FirstName;
