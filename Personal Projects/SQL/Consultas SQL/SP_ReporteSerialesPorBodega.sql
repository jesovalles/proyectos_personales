USE [AUTOMATIC_BI_PRO]
GO
/****** Object:  StoredProcedure [dbo].[SP_AUTOMATIC_BI_SerialesPorBodega]    Script Date: 21/10/2024 10:44:43 a. m. ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

--Procedimiento para traer el detallado de los atributos de los preoperacionales con no conformidades.
ALTER PROCEDURE [dbo].[SP_AUTOMATIC_BI_SerialesPorBodega]
        @BDNAME VARCHAR(MAX)
	   ,@FILTROS VARCHAR(MAX) = ''
	   ,@PERIODO VARCHAR (30) = ''
	   ,@CENTROCOSTO VARCHAR(MAX) = '*'
    
As BEGIN

 SET NOCOUNT ON

	-- CREACIÓN TABLA TEMPORAL PARA GUARDAR LAS BD A RECORRER
	IF OBJECT_ID(N'tempdb..#BIReporteMapeo') IS NOT NULL DROP TABLE #BIReporteMapeo;
	SELECT * INTO #BIReporteMapeo FROM (
		SELECT BaseDatos
			,CASE
				WHEN (CASE WHEN LEN((CASE WHEN CentroCostos LIKE '%_%' THEN LEFT(CentroCostos,4) ELSE CentroCostos END))< 4 THEN CONCAT('0',(CASE WHEN CentroCostos LIKE '%_%' THEN LEFT(CentroCostos,4) ELSE CentroCostos END)) ELSE (CASE WHEN CentroCostos LIKE '%_%' THEN LEFT(CentroCostos,4) ELSE CentroCostos END) END) = '0009' THEN 'P009'
				ELSE (CASE WHEN LEN((CASE WHEN CentroCostos LIKE '%_%' THEN LEFT(CentroCostos,4) ELSE CentroCostos END))< 4 THEN CONCAT('0',(CASE WHEN CentroCostos LIKE '%_%' THEN LEFT(CentroCostos,4) ELSE CentroCostos END)) ELSE (CASE WHEN CentroCostos LIKE '%_%' THEN LEFT(CentroCostos,4) ELSE CentroCostos END) END)
				END AS [CentroCostos]
		FROM [R2021Businmel].[dbo].[Ambiente]
		WHERE IdAmbienteTipo = 1
			AND Activo = 1
			AND BaseDatos NOT LIKE 'TEMIS_MOODLE_PRO'
			AND BaseDatos NOT LIKE '%IMP%'
			AND BaseDatos NOT LIKE '%OLD%'
			AND BaseDatos NOT LIKE '%004%'
			AND BaseDatos LIKE '%11d_PRO%'
	) BD

	--SELECT * FROM #BIReporteMapeo;

	--------=======================================================--------
	-- Tabla temporal donde se acumularán los resultados
	CREATE TABLE #TempReporte (
		Estado VARCHAR(500)
		,[Estado serial] VARCHAR(500)
		,[Tipo Documento] VARCHAR(500)
		,Serial VARCHAR(500)
		,[Mac Address] VARCHAR(500)
		,[Codigo Referencia] VARCHAR(500)
		,[Nombre Referencia] VARCHAR(500)
		,Documento VARCHAR(500)
		,Bodega VARCHAR(500) 
		,Tecnico VARCHAR(500)
		,FechaDocumento DATETIME
		,[Nombre del Cliente] VARCHAR(500)
		,Cuenta VARCHAR(500)
		,[Tercnico Retiro] VARCHAR(500)
		,[Fecha último movimiento] DATETIME
		,[BD_Name] VARCHAR(6)
	);

	-- Declaramos la variable de campos que se utilizará en el procedimiento
	DECLARE @campos VARCHAR(MAX) = '
		ES.Estado Estado
		,ES.Descripcion [Estado serial]
		,TD.NombreTipoDocumento [Tipo Documento]
		,S.Serial Serial
		,S.MacAddress [Mac Address]
		,R.CodigoReferencia [Codigo Referencia]
		,R.NombreReferencia [Nombre Referencia]
		,D.NroDocumento Documento
		,SBO.CodigoSubBodega Bodega
		,SBO.NombreSubBodega Tecnico
		,D.FechaDocumento FechaDocumento
		,T.RazonSocial [Nombre del Cliente]
		,T.CodigoTercero Cuenta
		,CASE WHEN ES.IdEstadoSerial = 4 THEN SBO.NombreSubBodega ELSE '''''''' END [Tercnico Retiro]
		,S.FechaModificacion [Fecha último movimiento]
		,''{{CENTROCOSTOS}}'' [BD_Name]
		';

	-- Declara las variables que se usarán en el cursor
	DECLARE @NombreBaseDatos VARCHAR(300),
			@centrocostos VARCHAR(6),
			@SQL NVARCHAR(MAX);

	-- Declara el cursor para recorrer la lista de bases de datos
	DECLARE cursor_balance CURSOR FOR
	SELECT BaseDatos,CentroCostos
	FROM #BIReporteMapeo; -- Aquí está la tabla que contiene el nombre de las bases de datos

	-- Abre el cursor
	OPEN cursor_balance;
	FETCH NEXT FROM cursor_balance INTO @NombreBaseDatos,@centrocostos;

	-- Inicia el ciclo de recorrido
	WHILE @@FETCH_STATUS = 0
	BEGIN
        -- Reemplaza el marcador de posición con el valor real de @centrocostos
        DECLARE @camposActuales VARCHAR(MAX) = REPLACE(@campos, '{{CENTROCOSTOS}}', ''''+@centrocostos+'''');
		-- Construye el SQL dinámico para ejecutar el procedimiento en la base de datos actual
		SET @SQL = '
		INSERT INTO #TempReporte
		EXEC [' + @NombreBaseDatos + '].dbo.SP_ReporteSerialesPorBodega
		@campos = ''' + @camposActuales + ''',
		@filtros = '' WHERE MONTH(CAST(S.FechaModificacion As DATE)) = 10 AND YEAR(CAST(S.FechaModificacion As DATE)) = 2024 ''
		';

		-- Ejecuta el SQL dinámico
		EXEC sp_executesql @SQL;

		-- Pasa a la siguiente base de datos
		FETCH NEXT FROM cursor_balance INTO @NombreBaseDatos,@centrocostos;
	END;

	-- Cierra y libera el cursor
	CLOSE cursor_balance;
	DEALLOCATE cursor_balance;

	-- Consulta los resultados acumulados
	SELECT * FROM #TempReporte;

	DROP TABLE #TempReporte
	DROP TABLE #BIReporteMapeo;

END;

--EXEC [dbo].[SP_AUTOMATIC_BI_SerialesPorBodega] '004'