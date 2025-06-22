# src/utils/data_inspector.py
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from configs.config import RAW_DATA_PATH

def inspect_json_structure(json_file):
    """JSON dosyasının yapısını incele"""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📋 Dosya: {os.path.basename(json_file)}")
    print(f"\n🔑 Ana anahtarlar: {list(data.keys())}")
    
    # Competition bilgileri
    if 'competition' in data:
        print(f"\n🏆 Competition anahtarları: {list(data['competition'].keys())}")
        print(f"Competition: {data['competition'].get('name', 'N/A')}")
    
    # Season bilgileri
    if 'season' in data:
        print(f"\n📅 Season anahtarları: {list(data['season'].keys())}")
    
    # Standings yapısı
    if 'standings' in data and data['standings']:
        print(f"\n📊 Standings sayısı: {len(data['standings'])}")
        if data['standings'][0]:
            print(f"Standings[0] anahtarları: {list(data['standings'][0].keys())}")
            if 'table' in data['standings'][0] and data['standings'][0]['table']:
                print(f"\n👥 İlk takım bilgileri:")
                print(f"Takım anahtarları: {list(data['standings'][0]['table'][0].keys())}")
    
    # Matches yapısı
    if 'matches' in data and data['matches']:
        print(f"\n⚽ Maç sayısı: {len(data['matches'])}")
        if data['matches'][0]:
            print(f"İlk maç anahtarları: {list(data['matches'][0].keys())}")
    
    return data

if __name__ == "__main__":
    # En son çekilen standings dosyasını bul
    files = os.listdir(RAW_DATA_PATH)
    standings_files = [f for f in files if 'standings' in f and f.endswith('.json')]
    
    if standings_files:
        latest_file = os.path.join(RAW_DATA_PATH, sorted(standings_files)[-1])
        inspect_json_structure(latest_file)