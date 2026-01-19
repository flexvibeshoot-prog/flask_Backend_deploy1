import requests

def geocode_address(address):
    from config import Config
    url = Config.GEOLOCATION_URL
    params = {
        "q": address,
        "api_key": Config.GEOLOCATION_API_KEY
    }

    res = requests.get(url, params=params)
    res.raise_for_status()

    data = res.json()
    if not data:
        return None, None

    return float(data[0]["lat"]), float(data[0]["lon"])