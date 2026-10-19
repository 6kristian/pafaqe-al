"""Collect Albanian businesses with no website from OpenStreetMap -> leads.raw.json (NOT committed).
Next steps in the pipeline: clean_leads.py -> upload_leads.py."""
import datetime, json, sys, time
import requests

ENDPOINTS = ["https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter"]
QUERY = """
[out:json][timeout:180];
area["ISO3166-1"="AL"][admin_level=2]->.a;
(
  nwr["shop"](area.a);
  nwr["craft"](area.a);
  nwr["amenity"~"^(restaurant|cafe|bar|pub|fast_food|ice_cream|nightclub|dentist|clinic|doctors|pharmacy|veterinary|car_wash|car_rental|driving_school)$"](area.a);
  nwr["tourism"~"^(hotel|guest_house|hostel|motel|apartment|chalet)$"](area.a);
  nwr["office"~"^(lawyer|estate_agent|travel_agent|accountant|insurance)$"](area.a);
);
out center tags;
"""
WEBSITE_TAGS = ("website", "contact:website", "url", "contact:url")


def to_lead(el):
    t = el.get("tags") or {}
    name = (t.get("name") or "").strip()
    if not name or any(k in t for k in WEBSITE_TAGS):
        return None
    c = el.get("center") or el  # nodes carry lat/lon, ways/relations carry a center
    lat, lng = c.get("lat"), c.get("lon")
    if lat is None or lng is None:
        return None
    cat = next((t[k] for k in ("shop", "amenity", "tourism", "craft", "office") if t.get(k)), "business")
    city = t.get("addr:city") or t.get("addr:town") or t.get("addr:village") or "Albania"  # cleaner infers unknowns
    street = f"{t.get('addr:street', '')} {t.get('addr:housenumber', '')}".strip()
    return {
        "id": f"osm_{el['type']}_{el['id']}",  # type in the id: node and way ids can collide
        "name": name,
        "category": cat.replace("_", " ").title(),
        "city": city,
        "address": street or city,
        "phone": t.get("phone") or t.get("contact:phone") or t.get("mobile") or t.get("contact:mobile"),
        "rating": None,
        "reviews": 0,
        "website": None,
        "lat": lat,
        "lng": lng,
    }


def fetch():
    for _ in range(3):
        for url in ENDPOINTS:
            try:
                r = requests.post(url, data={"data": QUERY}, timeout=240)
                if r.status_code == 200:
                    return r.json()
                print(url, "->", r.status_code)
            except requests.RequestException as e:
                print(url, "->", e)
        time.sleep(30)
    return None


if __name__ == "__main__":
    data = fetch()
    if not data:
        sys.exit("Overpass request failed")
    leads = [x for x in map(to_lead, data.get("elements", [])) if x]
    if len(leads) < 5000:
        sys.exit(f"Only {len(leads)} leads collected, refusing to continue")
    out = {"source": "live", "generated": datetime.date.today().isoformat(),
           "provider": "OpenStreetMap (Overpass API)", "count": len(leads), "businesses": leads}
    with open("leads.raw.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    print("collected", len(leads))
