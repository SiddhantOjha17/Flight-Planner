import pandas as pd
import datetime
from collections import defaultdict
import streamlit as st
from heapq import heappush, heappop

@st.cache_data()
def load_data():
    # Load flight data
    df = pd.read_csv('Flight_on_time_HIX.csv')
    return df

def create_flight_graph(df):
    graph = defaultdict(dict)
    for _, row in df.iterrows():
        src = row['Origin_Airport']
        dest = row['Destination_Airport']
        dep_time = row['Scheduled_Departure_Time']
        arr_time = row['Scheduled_Arrival_Time']
        distance = row['Flight_Distance']
        airline = row['Airline']
        flight_number = row['Flight_Number']
        # Check if flights have already been added between these airports
        if dest in graph[src]:
            graph[src][dest].append({'distance': distance, 'airline': airline, 'flight_number': flight_number, 'departure_time': dep_time, 'arrival_time': arr_time})
        else:
            graph[src][dest] = [{'distance': distance, 'airline': airline, 'flight_number': flight_number, 'departure_time': dep_time, 'arrival_time': arr_time}]
    return graph

def calculate_shortest_path(graph, start, end, flight_date):
    heap = []
    heappush(heap, (0, start, []))
    visited = set()
    shortest_duration = float('inf')
    shortest_path = []
    while heap:
        (cost, node, path) = heappop(heap)
        if node not in visited:
            visited.add(node)
            path = path + [node]
            if node == end:
                total_duration = 0
                for i in range(len(path)-1):
                    src, dest = path[i], path[i+1]
                    flight = graph[src][dest][0]
                    dep_time_str = f"{str(flight['departure_time']):0>4}"
                    arr_time_str = f"{str(flight['arrival_time']):0>4}"
                    departure_time = datetime.datetime.combine(flight_date, datetime.datetime.strptime(dep_time_str, '%H%M').time())
                    arrival_time = datetime.datetime.combine(flight_date, datetime.datetime.strptime(arr_time_str, '%H%M').time())
                    total_duration += (arrival_time - departure_time).seconds // 60
                if total_duration < shortest_duration:
                    shortest_duration = total_duration
                    shortest_path = [(path[i], path[i+1], graph[path[i]][path[i+1]][0]) for i in range(len(path)-1)]
            for neighbor, flights in graph[node].items():
                for flight in flights:
                    if flight['arrival_time'] and cost + flight['distance'] < shortest_duration:
                        heappush(heap, (cost + flight['distance'], neighbor, path))
    return shortest_path, shortest_duration

# Load flight data
df = load_data()
# Create flight graph
graph = create_flight_graph(df)
st.title('Flight Planner :airplane:')
# Create dropdown for selecting start and end airports
start_airport = st.selectbox('Select the starting airport', df['Origin_Airport'].unique())
end_airport = st.selectbox('Select the destination airport', df['Destination_Airport'].unique())

# Create date picker for selecting flight date
# flight_date = st.date_input('Select the flight date')
flight_date ='2023-03-15'
flight_date = datetime.datetime.strptime(flight_date, '%Y-%m-%d')


# Calculate shortest path and display results
if st.button('Find Shortest Path'):
    shortest_path, shortest_duration = calculate_shortest_path(graph, start_airport, end_airport, flight_date)
    if shortest_duration == float('inf'):
        st.write(f'There is no path from {start_airport} to {end_airport}')
    else:
        st.write(f'The shortest path from ',start_airport, ' to ', end_airport ,' :')
        path_str = " --> ".join([f" Flight {edge[0]} ({edge[2]['airline']} {edge[2]['flight_number']}) to {edge[1]}" for edge in shortest_path])
        st.write(f'Path: ', path_str)
        st.write(f'Duration: ', shortest_duration , ' minutes')

