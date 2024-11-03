# ESTE ES EL MODELO DE CAPACIDAD
from datetime import datetime
inicio = datetime.now()

import math
import folium
import itertools
import numpy as np
import pandas as pd
from colorama import init, Fore
import matplotlib.pyplot as plt
from geopy.distance import geodesic
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2

def CVRP(fuente,ruta_base,len_cuadr,capacity,nombre_adjunto,latitud_bodega,longitud_bodega):
    # Se filtra la fuente según la capacidad para evitar errores en el modelo
    fuente = fuente
    n = (len_cuadr*capacity)-1
    fuente = fuente.loc[:n]
    # Asegúrate de que la columna de fecha esté en formato datetime
    fuente['FECHA_ORDEN'] = pd.to_datetime(fuente['FECHA_ORDEN'])
    fuente = fuente.sort_values(by='FECHA_ORDEN', ascending=True)
    print(f'Fuente filtrada...{len(fuente)}')
    
    def custom_round(number):
        # Comprueba si el número está exactamente a la mitad entre dos enteros
        if number - math.floor(number) == 0.5:
            return math.ceil(number)
        else:
            return round(number)

    def haversine(lat1, lon1, lat2, lon2):
        """Calcula la distancia entre dos puntos en la tierra dados por latitud y longitud."""
        # R = 6371  # Radio de la Tierra en kilómetros
        R = 6371000 # Radio de la Tierra en metros
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c # en kilómetros

        return distance
    
    def create_distance_matrix(df, depot_lat, depot_lon):
        locations = [(depot_lat, depot_lon)] + list(zip(df['LATITUD'], df['LONGITUD']))
        return [[int(geodesic(loc1, loc2).meters) for loc2 in locations] for loc1 in locations]
        
    def create_data_model(df, depot_lat, depot_lon, longitud_cuadrilla, capacidad):
        """Almacena los datos de entrada del problema"""
        data = {}
        data['matriz_distancias'] = create_distance_matrix(df, depot_lat, depot_lon)
        data['num_vehiculos'] = longitud_cuadrilla
        data['deposito'] = 0
        data['demanda'] = [0]
        data['demanda'].extend([1] * (len(data['matriz_distancias'])-1))
        data['capacidad_vehiculos'] = []
        data['capacidad_vehiculos'].extend([capacidad] * longitud_cuadrilla)

        # Adjust the distance matrix to include only the points we'll visit
        data['matriz_distancias'] = [row[:1 + capacidad * data['num_vehiculos']] for row in data['matriz_distancias'][:1 + capacidad * data['num_vehiculos']]]
        print(len(data['matriz_distancias']))
        return data


    def print_solution(data, manager, routing, solution,mapeo_cuadrilla):
        """Imprimir la solución en la consola."""
        total_distance = 0
        total_load = 0
        for vehicle_id in range(data['num_vehiculos']):
            index = routing.Start(vehicle_id)
            codigo_cuadrilla = mapeo_cuadrilla[vehicle_id]
            plan_output = 'Ruta para el vehículo {}:\n'.format(vehicle_id)
            route_distance = 0
            route_load = 0
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                route_load += data['demanda'][node_index]
                plan_output += ' {0} metros ({1}) -> '.format(node_index, route_distance)
                # print(plan_output)
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                # ------------------------------------------------------------------------------------------------------------------
                if manager.IndexToNode(previous_index) != data['deposito'] and manager.IndexToNode(index) != data['deposito']:
                    route_distance += routing.GetArcCostForVehicle(
                        previous_index, index, vehicle_id)
                # -----------------------------------------------------------------------------------------------------------------    
            plan_output = route_load #la carga por vehículo para el dataframe
            # print(plan_output)
            total_distance += route_distance
            total_load += route_load
            return plan_output

    def main(fuente):
        # Crear DataFrame para almacenar los resultados finales de cada dia
        final_result_df = pd.DataFrame(columns=["CODIGO_SUB_BODEGA", "METROS_RECORRIDOS","FECHA_EJECUCION","CANTIDAD_ORDENES"])
        
        # Quitar el primer registro que no tiene fecha
        fuente = fuente.dropna(subset=['FECHA_ORDEN'])
        
        # Convertir la columna de fecha y hora a solo fecha
        fuente['FECHA_ORDEN'] = pd.to_datetime(fuente['FECHA_ORDEN']).dt.date

        fecha = str(datetime.now().date())

        # for fecha, fuente in fuente.groupby('FECHA_ORDEN'):
        print(Fore.YELLOW + f"Procesando datos para el día {fecha}...")

        latitudes = fuente['LATITUD'].tolist()
        longitudes = fuente['LONGITUD'].tolist()
        longitud_cuadrilla = len_cuadr
        ordenes = len(fuente)
        capacidad = int(capacity)
        # capacidad = math.ceil(ordenes / longitud_cuadrilla)

        # Generar una lista que contenga al menos una vez todos los números del 1 al num_maximo
        numeros = list(range(1, longitud_cuadrilla + 1))
        faltantes = ordenes - len(numeros)

        # Completar la lista con números aleatorios en el rango 1 a num_maximo
        numeros.extend(np.random.randint(1, longitud_cuadrilla + 1, size=faltantes))

        # Mezclar la lista de números aleatoriamente
        np.random.shuffle(numeros)

        # Asignar la lista mezclada como una nueva columna al DataFrame
        fuente['CodigoSubBodega'] = numeros
        cuadrilla = fuente['CodigoSubBodega'].unique()

        print('Cuadrilla: ',longitud_cuadrilla)
        print('Capacidad: ',capacidad)
        print('Ordenes: ',ordenes)

        # Mapeo de vehículos a códigos de cuadrilla
        mapeo_cuadrilla = {i: codigo for i, codigo in enumerate(cuadrilla)}

        # Combinar latitudes y longitudes en una lista de coordenadas
        coordenadas = list(zip(latitudes, longitudes))

        # Agrega el depósito al principio (o final) de tu lista de coordenadas
        coordenadas.insert(0,(latitud_bodega,longitud_bodega))

        long_cuadr_int = int(longitud_cuadrilla)
        
        """Punto de entrada del programa"""
        data = create_data_model(df=fuente, depot_lat=latitud_bodega, depot_lon=longitud_bodega, longitud_cuadrilla=long_cuadr_int, capacidad=capacidad)

        # Validación de datos antes de crear RoutingIndexManager
        if not isinstance(data['matriz_distancias'], list) or not all(isinstance(i, list) for i in data['matriz_distancias']):
            raise ValueError("La matriz de distancias debe ser una lista de listas (matriz 2D).")

        if not all(len(row) == len(data['matriz_distancias']) for row in data['matriz_distancias']):
            raise ValueError("La matriz de distancias debe ser cuadrada (todas las filas deben tener la misma longitud).")

        if not isinstance(data['num_vehiculos'], int) or data['num_vehiculos'] <= 0:
            raise ValueError("El número de vehículos debe ser un entero positivo.")

        if not isinstance(data['deposito'], int) or not (0 <= data['deposito'] < len(data['matriz_distancias'])):
            raise ValueError("El depósito debe ser un índice válido dentro de la matriz de distancias.")

        # Crea el administrador del índice de rutas.
        manager = pywrapcp.RoutingIndexManager(len(data['matriz_distancias']),
                                            data['num_vehiculos'],data['deposito'])

        # Crea el modelo de enrutamiento.
        routing = pywrapcp.RoutingModel(manager)

        # Crea y registra una devolución de llamada de distancia.
        def distance_callback(from_index, to_index):
            """Retorna la distancia entre dos nodos."""
            # Convierte desde la variable de ruta Index hasta la matriz de distancia NodeIndex.
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            # ---------------------------------------------------------------------------------------------------
            if from_node == data['deposito'] or to_node == data['deposito']:
                return 0
            return data['matriz_distancias'][from_node][to_node]
            # ---------------------------------------------------------------------------------------------------

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)

        # Define el costo de cada arco.
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Adhiere la restricción de capacidad.
        def demand_callback(from_index):
            """Retorna la demanda asociada a cada nodo"""
            # Convierte desde la variable de ruta Index hacia la matriz de distancia NodeIndex.
            from_node = manager.IndexToNode(from_index)
            return data['demanda'][from_node]

        demand_callback_index = routing.RegisterUnaryTransitCallback(
            demand_callback)
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # Sin holgura en la capacidad de los vehículos
            data['capacidad_vehiculos'],  # Capacidad máxima de los vehículos
            True,  # Iniciar el acumulador en cero
            'Capacity')

        # Configurar los parámetros de búsqueda.
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            # routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
            routing_enums_pb2.FirstSolutionStrategy.CHRISTOFIDES)
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
        search_parameters.time_limit.FromSeconds(30)

        # Solucionador del problema.
        solution = routing.SolveWithParameters(search_parameters)

        # Imprimir la solución en la consola.
        if solution:
            print_solution(data, manager, routing, solution,mapeo_cuadrilla)
            # Extraer rutas y graficarlas
            routes = extract_routes(data, manager, routing, solution)
            # Graficar en MAPA
            mapa = plot_routes_maps(routes, coordenadas)
            nombre_adj_fxd = nombre_adjunto.split('.')[0]
            ruta_informe_html = f"{ruta_base}Resultado_{nombre_adj_fxd}.html"
            mapa.save(ruta_informe_html)  # Guardar el mapa como archivo HTML
            #SET UP de los parametros para subir el archivo html a SharePoint
            nombre_archivo_html = ruta_informe_html.split('/')[-1]
            # upload_analytics_vrp(nombre_archivo_html)
            print('HTML Mapa guardado correctamente.')

            # Generar el informe
            results_df = informe(routes,fecha,mapeo_cuadrilla,fuente)
        else:
            print('No se encuentra solución !')
        
        # Concatenamos los resultados al DataFrame consolidado
        final_result_df = pd.concat([final_result_df, results_df], ignore_index=True)
        print(Fore.YELLOW + f"Fin del procesamiento de datos para el día {fecha}...")
        # Después de salir del bucle for, guarda el DataFrame consolidado en un solo archivo Excel
       
        nombre_adj_resumen = nombre_adjunto.split('.')[0]
        ruta_informe_resumen = f"{ruta_base}Resultado_{nombre_adj_resumen}_Resumen.xlsx"
        final_result_df.to_excel(ruta_informe_resumen, index=False)
        #SET UP de los parametros para subir el archivo html a SharePoint
        nombre_archivo_resumen = ruta_informe_resumen.split('/')[-1]
        # upload_analytics_vrp(nombre_archivo_resumen)
        print('HTML Mapa guardado correctamente.')
        

    def extract_routes(data, manager, routing, solution):
        """Extrae las rutas de la solución."""
        routes = []
        for vehicle_id in range(data['num_vehiculos']):
            index = routing.Start(vehicle_id)
            route = []
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                route.append(node_index)
                index = solution.Value(routing.NextVar(index))
            routes.append(route)
        return routes

    def informe(routes, fecha, mapeo_cuadrilla, fuente):
        # Crear DataFrame para almacenar los resultados
        results_df = pd.DataFrame(columns=["LATITUD", "LONGITUD", "COORDENADAS", "CODIGO_SUB_BODEGA", "METROS_RECORRIDOS","FECHA_EJECUCION","ID_ORDEN","DESC_MUNICIPIO","NODO","DIRECCION","PDA NUMERO"])

        for route in routes:
            vehiculo = routes.index(route)
            vehiculo = mapeo_cuadrilla[vehiculo]
            metros_anterior = 0
            orden_visita = 1  # Inicializar el orden de visita

            # for i in range(1, len(route)):
            for i in range(0, len(route)):
                # -------------------------- ORIGINAL ------------------------
                # lat1, lon1 = coordenadas[route[i - 1]]
                # lat2, lon2 = coordenadas[route[i]]
                start_pc = route[i]
                end_pc = route[i - 1]   
                lat1, lon1 = (fuente.iloc[end_pc-1]['LATITUD'], fuente.iloc[end_pc-1]['LONGITUD'])
                lat2, lon2 = (fuente.iloc[start_pc-1]['LATITUD'], fuente.iloc[start_pc-1]['LONGITUD'])

                # print('lat1, lon1: ',lat1, lon1)
                # print('lat2, lon2: ',lat2, lon2)

                # PARA EL PRIMER PUNTO PONEMOS LOS METROS EN 0
                if i == 1:
                    metros = 0
                    # print(i)
                else:
                    # SUMA LOS METROS DE COORDENADA ACTUAL CON LA ANTERIOR
                    metros = custom_round(haversine(lat1, lon1, lat2, lon2))
                # print(i,'metros = ',metros,'lat1 =',lat1,'lon1 = ',lon1,'lat2 =',lat2, 'lon2 =', lon2)

                    # Agregar los datos al DataFrame results_df
                    results_df = results_df._append({
                        "LATITUD": lat2,
                        "LONGITUD": lon2,
                        "COORDENADAS": f'({lat1},{lon1}),({lat2},{lon2})',
                        "CODIGO_SUB_BODEGA": vehiculo,
                        "METROS_RECORRIDOS": metros,
                        "FECHA_EJECUCION": fecha,
                        "ID_ORDEN": fuente.iloc[start_pc-1]['ID_ORDEN'],
                        "DESC_MUNICIPIO": fuente.iloc[start_pc-1]['DESC_MUNICIPIO'],
                        "NODO": fuente.iloc[start_pc-1]['NODO'],
                        "DIRECCION": fuente.iloc[start_pc-1]['DIRECCION'],
                        "PDA NUMERO": fuente.iloc[start_pc-1]['PDA NUMERO'],
                        "ORDEN_VISITA": orden_visita
                    }, ignore_index=True)

                    orden_visita += 1

                    # print('metros = ', metros, 'vehiculo = ', vehiculo)

            # Sumar la distancia de los metros recorridos
            metros_anterior += metros

        #SET UP de los parametros para subir el archivo a SharePoint
        nombre_adj_fxd = nombre_adjunto.split('.')[0]
        ruta_informe = f"{ruta_base}Resultado_{nombre_adj_fxd}.xlsx"
        # Cambiar orden a columnas
        orden_final = ['LATITUD','LONGITUD','COORDENADAS','METROS_RECORRIDOS','FECHA_EJECUCION','ID_ORDEN','DESC_MUNICIPIO','NODO','DIRECCION','PDA NUMERO','ORDEN_VISITA','CODIGO_SUB_BODEGA']
        results_df = results_df[orden_final]
        results_df = results_df.rename(columns={'CODIGO_SUB_BODEGA': 'GRUPO'})
        results_df.to_excel(ruta_informe, index=False)
        print("Excel guardado satisfactoriamente")
        nombre_archivo = ruta_informe.split('/')[-1]
        # upload_analytics_vrp(nombre_archivo)

        results_df = results_df.groupby(['GRUPO', 'FECHA_EJECUCION']).agg({
            'METROS_RECORRIDOS': 'sum', 
            'ID_ORDEN': 'count'
        }).reset_index()
        
        results_df.rename(columns={'ID_ORDEN': 'CANTIDAD_ORDENES'}, inplace=True)

        return results_df


    ########################################################################## FUNCION PARA DIBUJAR RUTAS EN MAPA
    def plot_routes_maps(routes, coordenadas):
        # Ruta al archivo del icono personalizado en tu computadora
        # ruta_icono = f'C:/Automatic/VRP/inmel_pin.png'
        # Convertir la ruta local a una URL de archivo
        # url_icono_personalizado = f'file://{os.path.abspath(ruta_icono)}'
    
        # Ciclo de colores
        # color_cycle = itertools.cycle(['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black', 'lightblue'])
        color_cycle = itertools.cycle({'beige', 'lightblue', 'orange', 'darkred', 'lightgray', 'red', 'purple',
                                    'darkblue', 'lightgreen', 'white', 'blue', 'black', 'cadetblue', 'pink',
                                    'darkgreen', 'green', 'darkpurple', 'lightred', 'gray'})
        
        
        bodega = (latitud_bodega,longitud_bodega)
        # Iniciar el mapa en la primera coordenada
        m = folium.Map(location=bodega, zoom_start=9)
    
        # Graficar las rutas
        for i, route in enumerate(routes):
            route_color = next(color_cycle)  # Color para esta ruta
            route_points = [coordenadas[node] for node in route]
            numero_cuadrilla = f"Cuadrilla_{i+1}"
    
            # Añadir línea para la ruta
            folium.PolyLine(route_points, color=route_color, weight=2.5, opacity=1).add_to(m)
    
            # Añadir marcadores y pop-ups a los puntos
            for idx, point in enumerate(route_points):
                if idx == 0:  # Punto de inicio (Bodega)
                    folium.Marker(
                        location=[point[0] + 0.0001, point[1]],
                        popup='BODEGA INMEL',
                        icon=folium.Icon(color='red', icon='home')
                        # icon=folium.CustomIcon(icon_image=url_icono_personalizado, icon_size=(40, 60))
                    ).add_to(m)
                else:
                    folium.Marker(
                        location=point,
                        popup=f'Punto {idx}: ({point[0]}, {point[1]}, {numero_cuadrilla})',
                        icon=folium.Icon(color=route_color, icon='car', prefix='fa')
                    ).add_to(m)        

            # Conectar el último punto con el inicio con línea punteada
            folium.PolyLine([route_points[-1], route_points[0]], color=route_color, weight=2.5, opacity=1, dash_array='5, 5').add_to(m)

        return m
    
    main(fuente)

    fin = datetime.now()
    print(Fore.CYAN + f'Duración {fin-inicio}')