import pandas as pd
import numpy as np
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import folium
from datetime import datetime
import math

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371 # Radius of earth in kilometers
    return int(c * r * 1000) # Convert to meters and round to integer

def create_distance_matrix(df, depot_lat, depot_lon):
    """
    Create a distance matrix from the dataframe and depot location
    """
    num_locations = len(df) + 1  # Include depot
    matrix = np.zeros((num_locations, num_locations), dtype=int)
    
    # Calculate distances from depot to all points
    for i in range(1, num_locations):
        matrix[0][i] = matrix[i][0] = haversine_distance(
            depot_lat, depot_lon, 
            df.iloc[i-1]['Latitud'], df.iloc[i-1]['Longitud']
        )
    
    # Calculate distances between all points
    for i in range(1, num_locations):
        for j in range(i+1, num_locations):
            dist = haversine_distance(
                df.iloc[i-1]['Latitud'], df.iloc[i-1]['Longitud'],
                df.iloc[j-1]['Latitud'], df.iloc[j-1]['Longitud']
            )
            matrix[i][j] = matrix[j][i] = dist
    
    return matrix.tolist()

def solve_routing_problem(data, manager, routing, is_cvrp):
    """
    Solve the routing problem and return the solution
    """
    # Create and register a transit callback
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    if is_cvrp:
        # Add capacity constraint
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

    # Add Distance constraint
    dimension_name = 'Distance'
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        3000000,  # vehicle maximum travel distance
        True,  # start cumul to zero
        dimension_name)
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(100)

    # Setting first solution heuristic
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem
    solution = routing.SolveWithParameters(search_parameters)
    
    return solution

def get_routes(solution, routing, manager, data):
    """
    Get the routes for each vehicle from the solution
    """
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
        routes.append((route, route_distance))
    return routes

def create_map(df, routes, depot_lat, depot_lon):
    """
    Create a Folium map with routes and delivery points
    """
    m = folium.Map(location=[depot_lat, depot_lon], zoom_start=10)

    # Add depot marker
    folium.Marker(
        [depot_lat, depot_lon],
        popup='Depot',
        icon=folium.Icon(color='red', icon='home')
    ).add_to(m)

    colors = ['blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray']

    for i, (route, _) in enumerate(routes):
        color = colors[i % len(colors)]
        route_points = [(depot_lat, depot_lon)]
        
        for point in route[1:-1]:  # Exclude depot at start and end
            lat = df.iloc[point-1]['Latitud']
            lon = df.iloc[point-1]['Longitud']
            route_points.append((lat, lon))
            
            # Add delivery point marker
            folium.Marker(
                [lat, lon],
                popup=f'Delivery Point {point}',
                icon=folium.Icon(color=color, icon='car', prefix='fa')
            ).add_to(m)
        
        route_points.append((depot_lat, depot_lon))
        
        # Add route line
        folium.PolyLine(
            route_points,
            weight=2,
            color=color,
            opacity=0.8
        ).add_to(m)

    return m

def optimize_routes(file_path, depot_lat, depot_lon, is_cvrp=False, consider_depot_distance=True):
    """
    Main function to optimize routes
    """
    try:
        # Read Excel file
        df = pd.read_excel(file_path)

        # Create distance matrix
        distance_matrix = create_distance_matrix(df, depot_lat, depot_lon)

        # Get number of vehicles
        num_vehicles = len(df['NombreVahiculo'].unique())

        # Prepare data for the solver
        data = {
            'distance_matrix': distance_matrix,
            'num_vehicles': num_vehicles,
            'depot': 0,
        }

        if is_cvrp:
            # For CVRP, we set demands and vehicle capacities
            num_orders = len(df)
            capacity = math.ceil(num_orders / num_vehicles)  # 6 in this case
            data['demands'] = [0] + [1] * num_orders  # 0 for depot, 1 for each delivery
            data['vehicle_capacities'] = [capacity] * num_vehicles

        # Create the routing index manager
        manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                               data['num_vehicles'], data['depot'])

        # Create Routing Model
        routing = pywrapcp.RoutingModel(manager)

        # Solve the problem
        solution = solve_routing_problem(data, manager, routing, is_cvrp)

        if solution:
            routes = get_routes(solution, routing, manager, data)
            
            # Create Folium map
            m = create_map(df, routes, depot_lat, depot_lon)
            m.save('route_map_VRP_CON_BODEGA.html')

            # Prepare data for Excel output
            output_data = []
            for i, (route, distance) in enumerate(routes):
                vehicle_name = df.iloc[route[1]-1]['NombreVahiculo']  # Get vehicle name from first delivery point
                num_deliveries = len(route) - 2  # Exclude depot at start and end
                
                if not consider_depot_distance:
                    # Subtract distance from depot to first point and last point to depot
                    distance -= (data['distance_matrix'][0][route[1]] + data['distance_matrix'][route[-2]][0])

                output_data.append({
                    'Vehicle Number': vehicle_name,
                    'Distance Traveled (m)': distance,
                    'Number of Deliveries': num_deliveries,
                    'Date': datetime.now().strftime('%Y-%m-%d'),
                    'Route': ' -> '.join(map(str, route[1:-1]))  # Detailed route
                })

            # Create Excel output
            output_df = pd.DataFrame(output_data)
            output_df.to_excel(f'route_summary_VRP_CON_BODEGA.xlsx', index=False)

            print("Optimization completed. Check 'route_map.html' for the map and 'route_summary.xlsx' for the summary.")
        else:
            print("No solution found!")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Example usage
file_path = 'data.xlsx'
depot_lat =  5.067183834026405 
depot_lon = -75.49638298612197 

optimize_routes(file_path, depot_lat, depot_lon, is_cvrp=False, consider_depot_distance=True)