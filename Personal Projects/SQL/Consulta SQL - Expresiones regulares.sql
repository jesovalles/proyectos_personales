SELECT EmailAddress 
FROM Person.EmailAddress
WHERE EmailAddress LIKE '%[a-zA-Z0-9._%+-]@[a-zA-Z0-9.-]%.[a-zA-Z]%';

--'%[a-zA-Z0-9._%+-]@[a-zA-Z0-9.-]%.[a-zA-Z]%'
--→ Este es el patrón que se usa para validar los correos. Vamos a dividirlo en partes:

--%
--→ Representa cualquier número de caracteres antes o después del patrón.

--[a-zA-Z0-9._%+-]
--→ Busca cualquier carácter dentro del conjunto (a-z, A-Z, 0-9, ., _, %, +, -).
--→ Es la parte del usuario del correo (antes del @).

--@
--→ Verifica que haya un símbolo @.

--[a-zA-Z0-9.-]
--→ Representa el dominio del correo (por ejemplo, gmail, outlook, empresa).

--%.[a-zA-Z]%
--→ Busca un punto (.) seguido de letras (a-zA-Z), asegurando que haya un dominio válido (.com, .net, .org).