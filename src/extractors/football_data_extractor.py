# src/extractors/football_data_extractor.py
import requests
import json
import time
from datetime import datetime
import os
import sys

# Parent directory'yi path'e ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from configs.config import FOOTBALL_DATA_API_KEY, API_BASE_URL, LEAGUES, RAW_DATA_PATH, REQUEST_DELAY

class FootballDataExtractor:
    def __init__(self):
        self.headers = {
            'X-Auth-Token': FOOTBALL_DATA_API_KEY
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def extract_league_standings(self, league_code, season=2023):
        """Lig puan durumunu çeker"""
        url = f"{API_BASE_URL}/competitions/{league_code}/standings"
        params = {'season': season}
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Veriyi kaydet
            self._save_data(data, f"{league_code}_standings_{season}")
            
            print(f"✅ {LEAGUES[league_code]} puan durumu başarıyla çekildi")
            time.sleep(REQUEST_DELAY)
            
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Hata: {e}")
            return None
    
    def extract_league_matches(self, league_code, season=2023):
        """Lig maçlarını çeker"""
        url = f"{API_BASE_URL}/competitions/{league_code}/matches"
        params = {'season': season}
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Veriyi kaydet
            self._save_data(data, f"{league_code}_matches_{season}")
            
            print(f"✅ {LEAGUES[league_code]} maçları başarıyla çekildi")
            time.sleep(REQUEST_DELAY)
            
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Hata: {e}")
            return None
    
    def _save_data(self, data, filename):
        """Veriyi JSON olarak kaydet"""
        os.makedirs(RAW_DATA_PATH, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = os.path.join(RAW_DATA_PATH, f"{filename}_{timestamp}.json")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"📁 Veri kaydedildi: {filepath}")

# Test için
if __name__ == "__main__":
    extractor = FootballDataExtractor()
    
    # Premier League verilerini çek
    extractor.extract_league_standings('PL')
    extractor.extract_league_matches('PL')