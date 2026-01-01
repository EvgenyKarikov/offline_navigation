import osmnx as ox
import networkx as nx
from geopy.distance import geodesic

# Замена get_route: Получи маршрут через OSM (без API ключа)
def get_route_osm(start_lat, start_lon, end_lat, end_lon, mode='walk'):
    # Загрузи граф дорог вокруг точек (bbox на основе расстояния + запас)
    dist = geodesic((start_lat, start_lon), (end_lat, end_lon)).km * 1.5  # Запас 50%
    graph = ox.graph_from_point((start_lat, start_lon), dist=dist*1000, network_type=mode)
    
    # Найди ближайшие ноды
    start_node = ox.distance.nearest_nodes(graph, start_lon, start_lat)
    end_node = ox.distance.nearest_nodes(graph, end_lon, end_lat)
    
    # Построй маршрут (shortest_path по длине)
    route = nx.shortest_path(graph, start_node, end_node, weight='length')
    
    # Извлеки координаты (lat, lon)
    polyline_points = [(graph.nodes[node]['y'], graph.nodes[node]['x']) for node in route]
    return polyline_points

# 1. Генерация URL для Google Maps (waypoints лимит ~10, так что subsample если много точек)
def generate_google_maps_url(start_lat, start_lon, end_lat, end_lon, waypoints, travel_mode='driving'):
    base_url = "https://www.google.com/maps/dir/?api=1"
    origin = f"origin={start_lat},{start_lon}"
    destination = f"destination={end_lat},{end_lon}"
    
    # Subsample waypoints до 8-10 (Google лимит), исключая start/end
    if len(waypoints) > 10:
        step = len(waypoints) // 8
        waypoints = waypoints[1:-1:step]  # Пропусти start/end
    
    waypoints_str = "|".join(f"{lat},{lon}" for lat, lon in waypoints)
    waypoints_param = f"waypoints={waypoints_str}" if waypoints_str else ""
    
    url = f"{base_url}&{origin}&{destination}&{waypoints_param}&travelmode={travel_mode}"
    return url

# Альтернатива: URL для OSM (используй утилиту типа routing.openstreetmap.de)
def generate_osm_url(start_lat, start_lon, end_lat, end_lon):
    # Простой URL для просмотра, но без полного маршрута (OSM не имеет встроенного dir как Google)
    base_url = "https://www.openstreetmap.org/directions"
    params = f"?engine=fossgis_osrm_car&route={start_lat}%2C{start_lon}%3B{end_lat}%2C{end_lon}"
    return base_url + params

# 2. Экспорт в KML файл (простой XML, открывается в Google Earth или Maps)
def export_to_kml(polyline_points, output_file='route.kml'):
    kml_header = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
<name>Route</name>
<Placemark>
<name>Path</name>
<LineString>
<coordinates>'''
    kml_footer = '''</coordinates>
</LineString>
</Placemark>
</Document>
</kml>'''
    
    coordinates = " ".join(f"{lon},{lat},0" for lat, lon in polyline_points)  # KML: lon,lat,alt
    with open(output_file, 'w') as f:
        f.write(kml_header + coordinates + kml_footer)
    print(f"KML exported to {output_file}. Open in Google Earth or import to Maps.")

# Пример использования (остальное как раньше)
start_lat, start_lon = 55.7558, 37.6173  # Москва, Кремль
end_lat, end_lon = 55.7415, 37.6209      # Москва, Арбат
step_meters = 50

polyline = get_route_osm(start_lat, start_lon, end_lat, end_lon, mode='drive')  # 'drive', 'walk', 'bike'
# sampled = sample_route_points(polyline, step_meters)
# download_panoramas(sampled, zoom=0)

# URL для проверки
google_url = generate_google_maps_url(start_lat, start_lon, end_lat, end_lon, polyline)
print(f"Google Maps URL: {google_url}")
osm_url = generate_osm_url(start_lat, start_lon, end_lat, end_lon)
print(f"OSM URL: {osm_url}")

# Экспорт KML
export_to_kml(polyline)

pass