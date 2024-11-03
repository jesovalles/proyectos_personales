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

def create_data_model(df, depot_lat, depot_lon, num_vehicles, vehicle_capacities=None):
    data = {}
    data['distance_matrix'] = calculate_distance_matrix(df, depot_lat, depot_lon)
    data['num_vehicles'] = num_vehicles
    data['depot'] = 0
    if vehicle_capacities:
        data['vehicle_capacities'] = vehicle_capacities
        data['demands'] = [0] + [1] * len(df)  # Assuming uniform demand of 1 for each location
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

def save_results(df, routes, depot_lat, depot_lon, output_file1, output_file2):
    results1 = []
    results2 = []
    for i, route in enumerate(routes):
        if len(route) > 2:  # Only consider routes with at least one stop
            vehicle = f"Vehicle_{i+1}"
            total_distance = sum(geodesic((depot_lat, depot_lon) if j == 0 else (df.iloc[j-1]['LATITUD'], df.iloc[j-1]['LONGITUD']),
                                          (depot_lat, depot_lon) if j == len(route)-1 else (df.iloc[route[j+1]-1]['LATITUD'], df.iloc[route[j+1]-1]['LONGITUD'])).meters
                                 for j in range(len(route)-1))
            points_visited = len(route) - 2  # Exclude depot at start and end
            results1.append({'VEHICULO': vehicle, 'METROS_RECORRIDOS': total_distance, 'PUNTOS_VISITADOS': points_visited})
            
            for order, node in enumerate(route[1:-1], start=1):  # Exclude depot at start and end
                lat, lon = df.iloc[node-1]['LATITUD'], df.iloc[node-1]['LONGITUD']
                results2.append({'VEHICULO': vehicle, 'METROS_RECORRIDOS': total_distance, 'ORDEN_VISITA': order, 'COORDENADAS': f"{lat}, {lon}"})

    pd.DataFrame(results1).to_excel(output_file1, index=False)
    pd.DataFrame(results2).to_excel(output_file2, index=False)

def create_map(df, routes, depot_lat, depot_lon, output_file):
    m = folium.Map(location=[depot_lat, depot_lon], zoom_start=12)
    folium.Marker([depot_lat, depot_lon], icon=folium.Icon(color='red', icon='home')).add_to(m)

    colors = ['blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue']
    for i, route in enumerate(routes):
        color = colors[i % len(colors)]
        for j, node in enumerate(route[1:-1]):  # Exclude depot
            lat, lon = df.iloc[node-1]['LATITUD'], df.iloc[node-1]['LONGITUD']
            folium.Marker([lat, lon], icon=folium.Icon(color=color, icon='car')).add_to(m)
            if j > 0:
                prev_lat, prev_lon = df.iloc[route[j]-1]['LATITUD'], df.iloc[route[j]-1]['LONGITUD']
                folium.PolyLine(locations=[[prev_lat, prev_lon], [lat, lon]], color=color, weight=2, opacity=0.8).add_to(m)

    m.save(output_file)

def run_optimization():
    file_path = file_path_entry.get()
    depot_lat = float(depot_lat_entry.get())
    depot_lon = float(depot_lon_entry.get())
    problem_type = problem_var.get()
    use_all_vehicles = use_all_vehicles_var.get()
    
    try:
        df = pd.read_excel(file_path)
        
        if use_all_vehicles:
            num_vehicles = df['VEHICULO'].nunique()
        else:
            num_vehicles = int(num_vehicles_entry.get())
        
        if problem_type == 'CVRP':
            vehicle_capacity = int(vehicle_capacity_entry.get())
            vehicle_capacities = [vehicle_capacity] * num_vehicles
        else:
            vehicle_capacities = None
        
        data = create_data_model(df, depot_lat, depot_lon, num_vehicles, vehicle_capacities)
        manager, routing, solution = solve_vrp(data)
        
        if solution:
            routes = get_routes(manager, routing, solution)
            save_results(df, routes, depot_lat, depot_lon, 'output1.xlsx', 'output2.xlsx')
            create_map(df, routes, depot_lat, depot_lon, 'route_map.html')
            messagebox.showinfo("Success", "Optimization completed. Results saved to output1.xlsx, output2.xlsx, and route_map.html")
        else:
            messagebox.showerror("Error", "No solution found")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# GUI setup
root = tk.Tk()
root.title("VRP/CVRP Optimizer")

tk.Label(root, text="File Path:").grid(row=0, column=0)
file_path_entry = tk.Entry(root, width=50)
file_path_entry.grid(row=0, column=1)
tk.Button(root, text="Browse", command=lambda: file_path_entry.insert(0, filedialog.askopenfilename())).grid(row=0, column=2)

tk.Label(root, text="Depot Latitude:").grid(row=1, column=0)
depot_lat_entry = tk.Entry(root)
depot_lat_entry.grid(row=1, column=1)

tk.Label(root, text="Depot Longitude:").grid(row=2, column=0)
depot_lon_entry = tk.Entry(root)
depot_lon_entry.grid(row=2, column=1)

problem_var = tk.StringVar(value="VRP")
tk.Radiobutton(root, text="VRP", variable=problem_var, value="VRP").grid(row=3, column=0)
tk.Radiobutton(root, text="CVRP", variable=problem_var, value="CVRP").grid(row=3, column=1)

use_all_vehicles_var = tk.BooleanVar(value=True)
tk.Checkbutton(root, text="Use all available vehicles", variable=use_all_vehicles_var).grid(row=4, column=0, columnspan=2)

tk.Label(root, text="Number of Vehicles:").grid(row=5, column=0)
num_vehicles_entry = tk.Entry(root)
num_vehicles_entry.grid(row=5, column=1)

tk.Label(root, text="Vehicle Capacity (CVRP only):").grid(row=6, column=0)
vehicle_capacity_entry = tk.Entry(root)
vehicle_capacity_entry.grid(row=6, column=1)

tk.Button(root, text="Run Optimization", command=run_optimization).grid(row=7, column=0, columnspan=3)

root.mainloop()