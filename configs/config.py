# configs/config.py
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# API Ayarları
FOOTBALL_DATA_API_KEY = os.getenv('FOOTBALL_DATA_API_KEY')
API_BASE_URL = 'https://api.football-data.org/v4'

# Desteklenen ligler
LEAGUES = {
    'PL': 'Premier League',
    'PD': 'La Liga', 
    'SA': 'Serie A',
    'BL1': 'Bundesliga',
    'FL1': 'Ligue 1'
}

# Veri klasörleri
RAW_DATA_PATH = 'data/raw'
PROCESSED_DATA_PATH = 'data/processed'

# Rate limiting
REQUEST_DELAY = 6  # saniye (dakikada 10 istek için)