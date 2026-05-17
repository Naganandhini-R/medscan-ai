import requests
import json

base_url = "http://127.0.0.1:8000/api/v1"
def test():
    try:
        # Get all MFGs
        mfgs = requests.get(f"{base_url}/manufacturer/list").json()
        print(f"Total Manufacturers: {len(mfgs)}")
        
        for m in mfgs:
            m_name = m['name']
            res = requests.get(f"{base_url}/report/stats?manufacturer={m_name}").json()
            print(f"- {m_name}: Total Scans = {res.get('total_scans')}, Fake = {res.get('scans_by_status', {}).get('fake')}")
            
        print("\nGlobal stats (no filter):")
        res_global = requests.get(f"{base_url}/report/stats").json()
        print(json.dumps(res_global, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test()
