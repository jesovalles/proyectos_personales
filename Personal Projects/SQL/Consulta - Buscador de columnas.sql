SELECT 
    t.name AS TableName,
    c.name AS ColumnName
FROM 
    sys.columns c
INNER JOIN 
    sys.tables t ON c.object_id = t.object_id
WHERE 
    c.name LIKE '%Name%'
		and t.name like '%Sales%' ;