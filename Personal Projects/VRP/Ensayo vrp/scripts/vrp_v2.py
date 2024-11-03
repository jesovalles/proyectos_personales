import pandas as pd
import numpy as np
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import folium
from datetime import datetime
import math
import tkinter as tk
from tkinter import filedialog, messagebox
import webbrowser
import random

class RoutingOptimizer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Route Optimizer")
        self.create_widgets()

    def create_widgets(self):
        # File selection
        tk.Label(self.root, text="Excel File:").grid(row=0, column=0, sticky="e")
        self.file_path = tk.StringVar()
        tk.Entry(self.root, textvariable=self.file_path, width=50).grid(row=0, column=1)
        tk.Button(self.root, text="Browse", command=self.browse_file).grid(row=0, column=2)

        # Optimization type
        tk.Label(self.root, text="Optimization Type:").grid(row=1, column=0, sticky="e")
        self.opt_type = tk.StringVar(value="VRP")
        tk.Radiobutton(self.root, text="VRP", variable=self.opt_type, value="VRP").grid(row=1, column=1, sticky="w")
        tk.Radiobutton(self.root, text="CVRP", variable=self.opt_type, value="CVRP").grid(row=1, column=1)

        # Use all vehicles
        self.use_all_vehicles = tk.BooleanVar(value=True)
        tk.Checkbutton(self.root, text="Use All Vehicles", variable=self.use_all_vehicles).grid(row=2, column=1, sticky="w")

        # Consider depot distance
        self.consider_depot = tk.BooleanVar(value=True)
        tk.Checkbutton(self.root, text="Consider Depot Distance", variable=self.consider_depot).grid(row=3, column=1, sticky="w")

        # Multi-depot support
        self.multi_depot = tk.BooleanVar(value=False)
        tk.Checkbutton(self.root, text="Multi-Depot", variable=self.multi_depot, command=self.toggle_multi_depot).grid(row=4, column=1, sticky="w")

        # Number of depots (initially hidden)
        self.depot_frame = tk.Frame(self.root)
        self.depot_frame.grid(row=5, column=0, columnspan=3, sticky="w")
        self.depot_frame.grid_remove()

        tk.Label(self.depot_frame, text="Number of Depots:").pack(side="left")
        self.num_depots = tk.IntVar(value=1)
        tk.Entry(self.depot_frame, textvariable=self.num_depots, width=5).pack(side="left")

        # Optimize button
        tk.Button(self.root, text="Optimize Routes", command=self.optimize).grid(row=6, column=1)

    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        self.file_path.set(filename)

    def toggle_multi_depot(self):
        if self.multi_depot.get():
            self.depot_frame.grid()
        else:
            self.depot_frame.grid_remove()

    def optimize(self):
        try:
            file_path = self.file_path.get()
            is_cvrp = self.opt_type.get() == "CVRP"
            use_all_vehicles = self.use_all_vehicles.get()
            consider_depot_distance = self.consider_depot.get()
            multi_depot = self.multi_depot.get()
            num_depots = self.num_depots.get() if multi_depot else 1

            if not file_path:
                messagebox.showerror("Error", "Please select an Excel file.")
                return

            df = pd.read_excel(file_path)
            
            if multi_depot:
                depot_coords = self.get_depot_coordinates(num_depots)
            else:
                # Use the first row as the depot in single depot case
                depot_coords = [(df.iloc[0]['Latitud'], df.iloc[0]['Longitud'])]

            results = []
            for i in range(3):  # Run 3 times with different random seeds
                result = self.optimize_routes(df, depot_coords, is_cvrp, use_all_vehicles, consider_depot_distance, random_seed=i)
                results.append(result)

            best_result = min(results, key=lambda x: x['total_distance'])
            self.create_output(best_result, df, depot_coords)
            
            messagebox.showinfo("Success", "Optimization completed. Check the output files.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def get_depot_coordinates(self, num_depots):
        depot_coords = []
        for i in range(num_depots):
            depot_window = tk.Toplevel(self.root)
            depot_window.title(f"Depot {i+1} Coordinates")
            
            tk.Label(depot_window, text="Latitude:").grid(row=0, column=0)
            lat_var = tk.DoubleVar()
            tk.Entry(depot_window, textvariable=lat_var).grid(row=0, column=1)
            
            tk.Label(depot_window, text="Longitude:").grid(row=1, column=0)
            lon_var = tk.DoubleVar()
            tk.Entry(depot_window, textvariable=lon_var).grid(row=1, column=1)
            
            tk.Button(depot_window, text="OK", command=depot_window.quit).grid(row=2, column=0, columnspan=2)
            
            depot_window.mainloop()
            depot_window.destroy()
            
            depot_coords.append((lat_var.get(), lon_var.get()))
        
        return depot_coords

    def optimize_routes(self, df, depot_coords, is_cvrp, use_all_vehicles, consider_depot_distance, random_seed):
        np.random.seed(random_seed)
        random.seed(random_seed)

        num_depots = len(depot_coords)
        distance_matrix = self.create_distance_matrix(df, depot_coords)

        num_vehicles = len(df['NombreVahiculo'].unique()) if use_all_vehicles else min(len(df['NombreVahiculo'].unique()), len(df) // 6)

        data = {
            'distance_matrix': distance_matrix,
            'num_vehicles': num_vehicles,
            'num_depots': num_depots,
            'depot': 0,
        }

        if is_cvrp:
            capacity = math.ceil(len(df) / num_vehicles)
            data['demands'] = [0] * num_depots + [1] * (len(df) - num_depots)
            data['vehicle_capacities'] = [capacity] * num_vehicles

        # Update the RoutingIndexManager initialization
        if num_depots == 1:
            manager = pywrapcp.RoutingIndexManager(len(distance_matrix), num_vehicles, data['depot'])
        else:
            manager = pywrapcp.RoutingIndexManager(len(distance_matrix), num_vehicles, list(range(num_depots)), list(range(num_depots)))

        routing = pywrapcp.RoutingModel(manager)

        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data['distance_matrix'][from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        if is_cvrp:
            def demand_callback(from_index):
                from_node = manager.IndexToNode(from_index)
                return data['demands'][from_node]

            demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
            routing.AddDimensionWithVehicleCapacity(
                demand_callback_index,
                0,
                data['vehicle_capacities'],
                True,
                'Capacity')

        dimension_name = 'Distance'
        routing.AddDimension(
            transit_callback_index,
            0,
            3000000,
            True,
            dimension_name)
        distance_dimension = routing.GetDimensionOrDie(dimension_name)
        distance_dimension.SetGlobalSpanCostCoefficient(100)

        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
        search_parameters.time_limit.FromSeconds(30)

        solution = routing.SolveWithParameters(search_parameters)

        if solution:
            return self.get_solution_details(data, manager, routing, solution, consider_depot_distance)
        else:
            raise Exception("No solution found!")

    def create_distance_matrix(self, df, depot_coords):
        matrix = []
        all_coords = depot_coords + list(zip(df['Latitud'], df['Longitud']))
        
        for from_lat, from_lon in all_coords:
            row = []
            for to_lat, to_lon in all_coords:
                distance = self.haversine_distance(from_lat, from_lon, to_lat, to_lon)
                row.append(distance)
            matrix.append(row)
        
        return matrix

    def haversine_distance(self, lat1, lon1, lat2, lon2):
        R = 6371  # Earth radius in kilometers

        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return int(R * c * 1000)  # Distance in meters

    def get_solution_details(self, data, manager, routing, solution, consider_depot_distance):
        total_distance = 0
        routes = []
        for vehicle_id in range(data['num_vehicles']):
            index = routing.Start(vehicle_id)
            route = [manager.IndexToNode(index)]
            route_distance = 0
            while not routing.IsEnd(index):
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route.append(manager.IndexToNode(index))
                route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
            
            if not consider_depot_distance:
                route_distance -= (data['distance_matrix'][route[0]][route[1]] + data['distance_matrix'][route[-2]][route[-1]])
            
            routes.append((route, route_distance))
            total_distance += route_distance

        return {
            'routes': routes,
            'total_distance': total_distance
        }

    def create_output(self, result, df, depot_coords):
        routes, total_distance = result['routes'], result['total_distance']

        # Create Excel output
        output_data = []
        for i, (route, distance) in enumerate(routes):
            vehicle_name = df.iloc[route[1] - len(depot_coords)]['NombreVahiculo']
            num_deliveries = len(route) - 2
            start_depot = route[0]
            end_depot = route[-1]
            output_data.append({
                'Vehicle Number': vehicle_name,
                'Distance Traveled (m)': distance,
                'Number of Deliveries': num_deliveries,
                'Date': datetime.now().strftime('%Y-%m-%d'),
                'Start Depot': start_depot,
                'End Depot': end_depot,
                'Route': ' -> '.join(map(str, route))
            })

        output_df = pd.DataFrame(output_data)
        output_df.to_excel('route_summary_222.xlsx', index=False)

        # Create Folium map
        m = folium.Map(location=depot_coords[0], zoom_start=10)

        colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray']

        # Add depot markers
        for i, (lat, lon) in enumerate(depot_coords):
            folium.Marker(
                [lat, lon],
                popup=f'Depot {i+1}',
                icon=folium.Icon(color='red', icon='home')
            ).add_to(m)

        # Add routes
        for i, (route, _) in enumerate(routes):
            color = colors[i % len(colors)]
            route_points = [depot_coords[route[0]]] + [(df.iloc[point - len(depot_coords)]['Latitud'], df.iloc[point - len(depot_coords)]['Longitud']) for point in route[1:-1] if point >= len(depot_coords)] + [depot_coords[route[-1]]]
            
            folium.PolyLine(
                route_points,
                weight=2,
                color=color,
                opacity=0.8
            ).add_to(m)

            # Add markers for delivery points
            for j, point in enumerate(route[1:-1]):
                if point >= len(depot_coords):
                    folium.Marker(
                        [df.iloc[point - len(depot_coords)]['Latitud'], df.iloc[point - len(depot_coords)]['Longitud']],
                        popup=f'Delivery Point {j+1}',
                        icon=folium.Icon(color=color, icon='car', prefix='fa')
                    ).add_to(m)

        # Add total distance info
        # folium.LayerControl().add_to(m)
        # m.get_root().html.add_child(folium.Element(f'<h3>Total Distance: {total_distance} meters</h3>'))

        m.save('route_map_222.html')
        # webbrowser.open('route_map_222.html', new=2)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = RoutingOptimizer()
    app.run()