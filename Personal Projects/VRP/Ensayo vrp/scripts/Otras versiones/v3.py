import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from geopy.distance import geodesic
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import folium

def calculate_distance_matrix(df, depot_lat, depot_lon):
    locations = [(depot_lat, depot_lon)] + list(zip(df['LATITUD'], df['LONGITUD']))
    return [[int(geodesic(loc1, loc2).meters) for loc2 in locations] for loc1 in locations]

def create_data_model(df, depot_lat, depot_lon, num_vehicles, vehicle_capacity=None):
    data = {}
    data['distance_matrix'] = calculate_distance_matrix(df, depot_lat, depot_lon)
    data['num_vehicles'] = num_vehicles
    data['depot'] = 0
    
    if vehicle_capacity:
        data['vehicle_capacities'] = [vehicle_capacity] * num_vehicles
        points_per_vehicle = min(vehicle_capacity, len(df) // num_vehicles)
        data['demands'] = [0] + [1] * (points_per_vehicle * num_vehicles)
        
        # Adjust the distance matrix to include only the points we'll visit
        data['distance_matrix'] = [row[:1 + points_per_vehicle * num_vehicles] for row in data['distance_matrix'][:1 + points_per_vehicle * num_vehicles]]
    
    return data

def solve_vrp(data, time_limit=30):
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']), data['num_vehicles'], data['depot'])
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    if 'vehicle_capacities' in data:
        def demand_callback(from_index):
            from_node = manager.IndexToNode(from_index)
            return data['demands'][from_node]

        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            data['vehicle_capacities'],  # vehicle maximum capacities
            True,  # start cumul to zero
            'Capacity')

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.seconds = time_limit

    solution = routing.SolveWithParameters(search_parameters)
    return manager, routing, solution

def get_routes(manager, routing, solution):
    routes = []
    for vehicle_id in range(routing.vehicles()):
        index = routing.Start(vehicle_id)
        route = []
        while not routing.IsEnd(index):
            route.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        route.append(manager.IndexToNode(index))
        routes.append(route)
    return routes

def save_results(df, routes, depot_lat, depot_lon, output_file1, output_file2, include_start_distance, include_end_distance):
    results1 = []
    results2 = []
    for i, route in enumerate(routes):
        if len(route) > 2:  # Only consider routes with at least one stop
            vehicle = f"Cuadrilla_{i+1}"
            total_distance = 0
            for j in range(len(route) - 1):
                start = route[j]
                end = route[j + 1]
                start_coords = (depot_lat, depot_lon) if start == 0 else (df.iloc[start-1]['LATITUD'], df.iloc[start-1]['LONGITUD'])
                end_coords = (depot_lat, depot_lon) if end == 0 else (df.iloc[end-1]['LATITUD'], df.iloc[end-1]['LONGITUD'])
                segment_distance = geodesic(start_coords, end_coords).meters
                
                if (j == 0 and not include_start_distance) or (j == len(route) - 2 and not include_end_distance):
                    continue
                
                total_distance += segment_distance
                
                if j > 0 or (j == 0 and include_start_distance):  # Skip first segment if start distance is not included
                    results2.append({
                        'VEHICULO': vehicle,
                        'METROS_RECORRIDOS': segment_distance,
                        'ORDEN_VISITA': j if include_start_distance else j - 1,
                        'COORDENADAS': f"{end_coords[0]}, {end_coords[1]}"
                    })
            
            points_visited = len(route) - 2  # Exclude depot at start and end
            results1.append({'VEHICULO': vehicle, 'METROS_RECORRIDOS': total_distance, 'PUNTOS_VISITADOS': points_visited})

    pd.DataFrame(results1).to_excel(output_file1, index=False)
    pd.DataFrame(results2).to_excel(output_file2, index=False)

def create_map(df, routes, depot_lat, depot_lon):
    m = folium.Map(location=[depot_lat, depot_lon], zoom_start=10)

    folium.Marker(
        [depot_lat, depot_lon],
        popup='Depot',
        icon=folium.Icon(color='red', icon='home')
    ).add_to(m)

    colors = ['blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray']

    for i, route in enumerate(routes):
        color = colors[i % len(colors)]
        vehicle = f"Vehicle_{i+1}"
        route_points = [(depot_lat, depot_lon)]
        
        for point in route[1:-1]:  # Exclude depot at start and end
            lat = df.iloc[point-1]['LATITUD']
            lon = df.iloc[point-1]['LONGITUD']
            route_points.append((lat, lon))
            
            folium.Marker(
                [lat, lon],
                popup=f'Delivery Point {point}, {vehicle}',
                icon=folium.Icon(color=color, icon='car', prefix='fa')
            ).add_to(m)
        
        route_points.append((depot_lat, depot_lon))
        
        folium.PolyLine(
            [route_points[0], route_points[1]],
            weight=2,
            color=color,
            opacity=0.8,
            dash_array='20, 20'
        ).add_to(m)

        if len(route_points) > 3:
            folium.PolyLine(
                route_points[1:-1],
                weight=2,
                color=color,
                opacity=0.8
            ).add_to(m)

        folium.PolyLine(
            [route_points[-2], route_points[-1]],
            weight=2,
            color=color,
            opacity=0.8,
            dash_array='10, 10'
        ).add_to(m)

    return m

def run_optimization():
    file_path = file_path_entry.get()
    depot_coords = depot_coords_entry.get().strip('()').split(',')
    depot_lat = float(depot_coords[0])
    depot_lon = float(depot_coords[1])
    problem_type = problem_var.get()
    use_all_vehicles = use_all_vehicles_var.get()
    include_start_distance = include_start_distance_var.get()
    include_end_distance = include_end_distance_var.get()
    
    try:
        df = pd.read_excel(file_path)
        
        if use_all_vehicles:
            num_vehicles = df['VEHICULO'].nunique()
        else:
            num_vehicles = int(num_vehicles_entry.get())
        
        if problem_type == 'CVRP':
            vehicle_capacity = int(vehicle_capacity_entry.get())
        else:
            vehicle_capacity = None
        
        data = create_data_model(df, depot_lat, depot_lon, num_vehicles, vehicle_capacity)
        manager, routing, solution = solve_vrp(data)
        
        if solution:
            routes = get_routes(manager, routing, solution)
            save_results(df, routes, depot_lat, depot_lon, 'Solucion_detallada.xlsx', 'Solucion_resumida.xlsx', include_start_distance, include_end_distance)
            m = create_map(df, routes, depot_lat, depot_lon)
            m.save('Solucion_mapa.html')
            messagebox.showinfo("Exitoso", "Optimizacion completada. Resultados guardados como: Solucion_detallada.xlsx, Solucion_resumida.xlsx, y Solucion_mapa.html")
        else:
            messagebox.showerror("Error", "Solución no encontrada")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# GUI setup
root = tk.Tk()
root.title("Optimizador VRP/CVR")

tk.Label(root, text="Ruta Archivo:").grid(row=0, column=0)
file_path_entry = tk.Entry(root, width=50)
file_path_entry.grid(row=0, column=1)
tk.Button(root, text="Navegar", command=lambda: file_path_entry.insert(0, filedialog.askopenfilename())).grid(row=0, column=2)

tk.Label(root, text="Coordenadas Deposito (lat,lon):").grid(row=1, column=0)
depot_coords_entry = tk.Entry(root)
depot_coords_entry.grid(row=1, column=1)

problem_var = tk.StringVar(value="VRP")
tk.Radiobutton(root, text="VRP", variable=problem_var, value="VRP").grid(row=2, column=0)
tk.Radiobutton(root, text="CVRP", variable=problem_var, value="CVRP").grid(row=2, column=1)

use_all_vehicles_var = tk.BooleanVar(value=True)
tk.Checkbutton(root, text="Usar todos los vehiculos", variable=use_all_vehicles_var).grid(row=3, column=0, columnspan=2)

tk.Label(root, text="Numero de vehiculos:").grid(row=4, column=0)
num_vehicles_entry = tk.Entry(root)
num_vehicles_entry.grid(row=4, column=1)

tk.Label(root, text="Capacidad vehiculo (Solo para CVRP):").grid(row=5, column=0)
vehicle_capacity_entry = tk.Entry(root)
vehicle_capacity_entry.grid(row=5, column=1)

include_start_distance_var = tk.BooleanVar(value=True)
tk.Checkbutton(root, text="Incluir distancia del deposito al primer punto", variable=include_start_distance_var).grid(row=6, column=0, columnspan=2)

include_end_distance_var = tk.BooleanVar(value=True)
tk.Checkbutton(root, text="Incluir distancia del ultimo punto al deposito", variable=include_end_distance_var).grid(row=7, column=0, columnspan=2)

tk.Button(root, text="Optimizar", command=run_optimization).grid(row=8, column=0, columnspan=3)

root.mainloop()