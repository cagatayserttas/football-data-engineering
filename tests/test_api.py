# test_api.py
import requests
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from configs.config import FOOTBALL_DATA_API_KEY

# API anahtarını kontrol et
print(f"API Key: {FOOTBALL_DATA_API_KEY[:10]}..." if FOOTBALL_DATA_API_KEY else "API Key bulunamadı!")

# Basit bir test isteği
headers = {'X-Auth-Token': FOOTBALL_DATA_API_KEY}

# Önce mevcut yarışmaları listeleyelim
response = requests.get('https://api.football-data.org/v4/competitions', headers=headers)
print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print("\nKullanılabilir ligler:")
    for comp in data['competitions'][:10]:  # İlk 10 ligi göster
        print(f"- {comp['code']}: {comp['name']}")
else:
    print(f"Hata: {response.text}")