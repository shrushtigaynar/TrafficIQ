import requests
import json

resp = requests.post('http://127.0.0.1:8000/analyse-city', json={'city_name': 'Pune'}, timeout=60)
print(f"Status: {resp.status_code}")
data = resp.json()
print("Top-level keys:", list(data.keys()))
if 'blueprint' in data:
    print("✓ 'blueprint' key found")
    bp = data['blueprint']
    print("Blueprint keys:", list(bp.keys()))
    print("\nSample blueprint data:")
    print(f"  city_name: {bp.get('city_name')}")
    print(f"  overall_score: {bp.get('overall_score')}")
    print(f"  total_areas: {bp.get('total_areas')}")
else:
    print("✗ 'blueprint' key NOT found")
    print("Response:", json.dumps(data, indent=2)[:500])

