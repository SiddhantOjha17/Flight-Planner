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
        graph[src][dest] = {'distance': distance, 'airline': airline, 'flight_number': flight_number, 'departure_time': dep_time, 'arrival_time': arr_time}
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
                edges = []
                total_duration = 0
                for i in range(len(path)-1):
                    src, dest = path[i], path[i+1]
                    edge_data = graph[src][dest]
                    departure_time = datetime.datetime.combine(flight_date, datetime.datetime.strptime(str(edge_data['departure_time']), '%H%M').time())
                    arrival_time = datetime.datetime.combine(flight_date, datetime.datetime.strptime(str(edge_data['arrival_time']), '%H%M').time())
                    duration = arrival_time - departure_time
                    total_duration += duration.seconds // 60
                    edges.append((src, dest, {'airline': edge_data['airline'], 'flight_number': edge_data['flight_number'], 'duration': duration}))
                if total_duration < shortest_duration:
                    shortest_duration = total_duration
                    shortest_path = {'path': path, 'duration': total_duration, 'edges': edges}
            for neighbor, edge_data in graph[node].items():
                heappush(heap, (cost + edge_data['distance'], neighbor, path))
    return shortest_path


# Load flight data
df = load_data()

# Create flight graph
graph = create_flight_graph(df)

# Define Streamlit app
st.title('Flight Planner')

start_airport = st.selectbox("Select the starting airport", df['Origin_Airport'].unique())
end_airport = st.selectbox("Select the destination airport", df['Destination_Airport'].unique())
flight_date = st.date_input('Select flight date:')
if st.button('Find Shortest Path'):
    result = calculate_shortest_path(graph, start_airport, end_airport, flight_date)
    if result['duration'] == 0:
        st.write('No flight path found')
    else:
        st.write('Total duration:', result['duration'], 'minutes')
        st.write('Path:')
        for i, edge in enumerate(result['edges']):
            st.write(f"{i+1}. Fly {edge[2]['airline']} flight {edge[2]['flight_number']} from {edge[0]}")



