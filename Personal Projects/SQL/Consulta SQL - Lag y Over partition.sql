WITH SalaryHistory AS (
    SELECT 
        e.BusinessEntityID,
        p.FirstName,
        p.LastName,
        s.Rate AS CurrentSalary,
        s.ModifiedDate,
        LAG(s.Rate) OVER (
            PARTITION BY e.BusinessEntityID 
            ORDER BY s.ModifiedDate
        ) AS PreviousSalary
    FROM HumanResources.Employee e
    INNER JOIN Person.Person p ON e.BusinessEntityID = p.BusinessEntityID
    INNER JOIN HumanResources.EmployeePayHistory s ON e.BusinessEntityID = s.BusinessEntityID
)
SELECT *, 
       CurrentSalary - ISNULL(PreviousSalary, 0) AS SalaryChange
FROM SalaryHistory;
