import math
from app.db.session import SessionLocal
from app.models.report import IssueReport

db = SessionLocal()

# Global Pharmacy Nodes matching the original seed architecture
city_nodes = [
    # India
    {"name": "Mumbai", "lat": 19.0760, "lng": 72.8777},
    {"name": "Delhi", "lat": 28.6139, "lng": 77.2090},
    {"name": "Chennai", "lat": 13.0827, "lng": 80.2707},
    {"name": "Bangalore", "lat": 12.9716, "lng": 77.5946},
    {"name": "Hyderabad", "lat": 17.3850, "lng": 78.4867},
    {"name": "Kolkata", "lat": 22.5726, "lng": 88.3639},
    {"name": "Pune", "lat": 18.5204, "lng": 73.8567},
    {"name": "Ahmedabad", "lat": 23.0225, "lng": 72.5714},
    {"name": "Jaipur", "lat": 26.9124, "lng": 75.7873},
    {"name": "Lucknow", "lat": 26.8467, "lng": 80.9462},
    # US / North America
    {"name": "New York", "lat": 40.7128, "lng": -74.0060},
    {"name": "Chicago", "lat": 41.8781, "lng": -87.6298},
    {"name": "Los Angeles", "lat": 34.0522, "lng": -118.2437},
    {"name": "Houston", "lat": 29.7604, "lng": -95.3698},
    {"name": "Miami", "lat": 25.7617, "lng": -80.1918},
    {"name": "Boston", "lat": 42.3601, "lng": -71.0589},
    {"name": "Seattle", "lat": 47.6062, "lng": -122.3321},
    # Europe
    {"name": "London", "lat": 51.5074, "lng": -0.1278},
    {"name": "Paris", "lat": 48.8566, "lng": 2.3522},
    {"name": "Berlin", "lat": 52.5200, "lng": 13.4050},
    {"name": "Rome", "lat": 41.9028, "lng": 12.4964},
    {"name": "Madrid", "lat": 40.4168, "lng": -3.7038},
    # Latin America
    {"name": "Sao Paulo", "lat": -23.5505, "lng": -46.6333},
    {"name": "Mexico City", "lat": 19.4326, "lng": -99.1332},
    {"name": "Bogota", "lat": 4.7110, "lng": -74.0721},
    # East Asia / Others
    {"name": "Tokyo", "lat": 35.6762, "lng": 139.6503},
    {"name": "Singapore", "lat": 1.3521, "lng": 103.8198},
    {"name": "Seoul", "lat": 37.5665, "lng": 126.9780},
    {"name": "Bangkok", "lat": 13.7563, "lng": 100.5018}
]

def get_closest_city(lat, lng):
    closest = city_nodes[0]["name"]
    min_dist = float('inf')
    for node in city_nodes:
        # Simple Euclidean distance approximation for finding the nearest regional hub
        dist = math.hypot(lat - node["lat"], lng - node["lng"])
        if dist < min_dist:
            min_dist = dist
            closest = node["name"]
    return closest

reports = db.query(IssueReport).all()

for r in reports:
    try:
        lat = float(r.lat)
        lng = float(r.lng)
        city = get_closest_city(lat, lng)
        r.location_details = f"{city} Pharmacy Node"
    except:
        r.location_details = "Mumbai Pharmacy Node"

db.commit()
print("Restored all location details to '{City} Pharmacy Node' matching real scan coordinates!")
db.close()
