import random
from app.db.session import SessionLocal
from app.models.report import IssueReport

db = SessionLocal()

india_addresses = [
    "Apollo Pharmacy, Andheri West, Mumbai",
    "MedPlus, T Nagar, Chennai",
    "Wellness Forever, Koramangala, Bangalore",
    "Frank Ross Pharmacy, Salt Lake, Kolkata",
    "Sanjivani Pharmacy, Connaught Place, New Delhi",
    "Netmeds Local, Banjara Hills, Hyderabad",
    "Local Chemist, MG Road, Pune",
    "City Hospital Pharmacy, Navrangpura, Ahmedabad",
    "Guardian Pharmacy, Sector 18, Noida",
    "Suburban Medicals, Viman Nagar, Pune"
]

us_addresses = [
    "CVS Pharmacy, 5th Ave, New York, NY",
    "Walgreens, Market St, San Francisco, CA",
    "Rite Aid, Hollywood Blvd, Los Angeles, CA",
    "Walmart Pharmacy, Michigan Ave, Chicago, IL",
    "Kroger Pharmacy, Main St, Houston, TX",
    "Publix Pharmacy, Ocean Dr, Miami, FL",
    "Safeway Pharmacy, Broadway, Seattle, WA",
    "Target CVS, Boylston St, Boston, MA",
    "Meijer Pharmacy, Woodward Ave, Detroit, MI",
    "HEB Pharmacy, Congress Ave, Austin, TX"
]

eu_addresses = [
    "Boots Pharmacy, Oxford St, London, UK",
    "Pharmacie de la Gare, Paris, France",
    "Apotheke am Bahnhof, Berlin, Germany",
    "Farmacia Centrale, Rome, Italy",
    "Farmacia Internacional, Madrid, Spain",
    "Apotek Hjartat, Stockholm, Sweden",
    "LloydsPharmacy, Dublin, Ireland",
    "Pharmacie Principale, Geneva, Switzerland",
    "Benu Apotheek, Amsterdam, Netherlands",
    "City Farmacia, Lisbon, Portugal"
]

latam_addresses = [
    "Farmacias del Ahorro, Mexico City, Mexico",
    "Droga Raia, Sao Paulo, Brazil",
    "Farmacity, Buenos Aires, Argentina",
    "Cruz Verde, Santiago, Chile",
    "Inkafarma, Lima, Peru",
    "Farmatodo, Bogota, Colombia"
]

asia_addresses = [
    "Watsons, Orchard Road, Singapore",
    "Guardian, Bukit Bintang, Kuala Lumpur",
    "Matsumoto Kiyoshi, Shibuya, Tokyo, Japan",
    "Olive Young, Gangnam, Seoul, South Korea",
    "BKK Pharmacy, Sukhumvit, Bangkok, Thailand",
    "City Chain Pharmacy, Central, Hong Kong"
]

reports = db.query(IssueReport).all()

for r in reports:
    try:
        lat = float(r.lat)
        lng = float(r.lng)
        
        # Simple bounding boxes to assign localized addresses
        if 24.0 <= lat <= 49.0 and -125.0 <= lng <= -66.0:
            addr = random.choice(us_addresses)
        elif 8.0 <= lat <= 35.0 and 68.0 <= lng <= 97.0:
            addr = random.choice(india_addresses)
        elif 35.0 <= lat <= 70.0 and -10.0 <= lng <= 40.0:
            addr = random.choice(eu_addresses)
        elif -55.0 <= lat <= 30.0 and -100.0 <= lng <= -35.0:
            addr = random.choice(latam_addresses)
        elif -10.0 <= lat <= 45.0 and 95.0 <= lng <= 150.0:
            addr = random.choice(asia_addresses)
        else:
            # Fallback random mixing
            addr = random.choice(india_addresses + us_addresses + eu_addresses)
            
    except:
        addr = random.choice(india_addresses + us_addresses)
        
    r.location_details = addr

db.commit()
print("Updated all location details to realistic pharmacy addresses based on coordinates!")
db.close()
