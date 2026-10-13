import json
import datetime
import requests

def collect_leads():
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = """
    [out:json][timeout:60];
    area["ISO3166-1"="AL"][admin_level=2]->.searchArea;
    (
      node["shop"](area.searchArea);
      way["shop"](area.searchArea);
      node["amenity"~"restaurant|cafe|bar|fast_food|pub|hotel|dentist|pharmacy"](area.searchArea);
      way["amenity"~"restaurant|cafe|bar|fast_food|pub|hotel|dentist|pharmacy"](area.searchArea);
    );
    out body;
    >;
    out skel qt;
    """
    response = requests.post(overpass_url, data={'data': query})
    if response.status_code != 200:
        return None
    
    data = response.json()
    businesses = []
    seen_names = set()
    
    for el in data.get('elements', []):
        tags = el.get('tags', {})
        name = tags.get('name')
        if not name or name in seen_names:
            continue
        if 'website' in tags or 'contact:website' in tags or 'url' in tags:
            continue
        seen_names.add(name)
        
        category = (tags.get('shop') or tags.get('amenity') or 'Business').replace('_', ' ').title()
        city = tags.get('addr:city') or tags.get('addr:town') or 'Tirana'
        address = f"{tags.get('addr:street', '')} {tags.get('addr:housenumber', '')}".strip() or f"{city}, Albania"
        
        businesses.append({
            "id": f"osm_{el.get('id')}",
            "name": name,
            "category": category,
            "city": city,
            "address": address,
            "phone": tags.get('phone') or tags.get('contact:phone'),
            "rating": None,
            "reviews": None,
            "website": None
        })
        
    return {
        "source": "live",
        "generated": datetime.datetime.now().strftime("%Y-%m-%d"),
        "count": len(businesses),
        "businesses": businesses
    }

if __name__ == "__main__":
    result = collect_leads()
    if result and result['businesses']:
        with open("leads.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
