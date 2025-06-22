# src/transformers/football_data_transformer.py
import pandas as pd
import json
import os
from datetime import datetime
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from configs.config import RAW_DATA_PATH, PROCESSED_DATA_PATH

class FootballDataTransformer:
    def __init__(self):
        self.raw_path = RAW_DATA_PATH
        self.processed_path = PROCESSED_DATA_PATH
        os.makedirs(self.processed_path, exist_ok=True)
    
    
    def transform_standings(self, json_file):
        """Puan durumu verilerini DataFrame'e dönüştür"""
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    
        standings_list = []
    
        # Standings verilerini parse et
        for standing in data['standings']:
            if standing['type'] == 'TOTAL':  # Sadece toplam puanları al
                for team in standing['table']:
                    standings_list.append({
                        'position': team['position'],
                        'team_id': team['team']['id'],
                        'team_name': team['team']['name'],
                        'team_short_name': team['team'].get('shortName', team['team']['name']),
                        'team_tla': team['team'].get('tla', ''),
                        'crest_url': team['team'].get('crest', ''),
                        'played_games': team['playedGames'],
                        'won': team['won'],
                        'draw': team['draw'],
                        'lost': team['lost'],
                        'points': team['points'],
                        'goals_for': team['goalsFor'],
                        'goals_against': team['goalsAgainst'],
                        'goal_difference': team['goalDifference'],
                        'form': team.get('form', ''),
                        'competition_name': data['competition']['name'],
                        'competition_code': data['competition']['code'],
                        'season_start': data['season']['startDate'],
                        'season_end': data['season']['endDate'],
                        'last_updated': data.get('lastUpdated', datetime.now().isoformat())  # Güvenli erişim
                    })
    
        df_standings = pd.DataFrame(standings_list)
    
        # Boş DataFrame kontrolü
        if df_standings.empty:
            print("⚠️ Uyarı: Standings verisi boş!")
            return df_standings
        
            # Hesaplanan metrikleri ekle
        df_standings['win_percentage'] = (df_standings['won'] / df_standings['played_games'] * 100).round(2)
        df_standings['points_per_game'] = (df_standings['points'] / df_standings['played_games']).round(2)
        df_standings['goals_per_game'] = (df_standings['goals_for'] / df_standings['played_games']).round(2)
        df_standings['goals_conceded_per_game'] = (df_standings['goals_against'] / df_standings['played_games']).round(2)
    
        # Form analizini ekle (son 5 maç)
        if 'form' in df_standings.columns and df_standings['form'].notna().any():
            df_standings['form_points'] = df_standings['form'].apply(
                lambda x: sum([3 if c == 'W' else 1 if c == 'D' else 0 for c in str(x)]) if x else 0
            )
    
        print(f"✅ {len(df_standings)} takımın puan durumu işlendi")
    
        return df_standings
    
    
    
    def transform_matches(self, json_file):
        """Maç verilerini DataFrame'e dönüştür"""
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        matches_list = []
        
        for match in data['matches']:
            matches_list.append({
                'match_id': match['id'],
                'competition_name': data['competition']['name'],
                'competition_code': data['competition']['code'],
                'season': match['season']['startDate'][:4],
                'utc_date': match['utcDate'],
                'status': match['status'],
                'matchday': match.get('matchday'),
                'stage': match.get('stage'),
                'home_team_id': match['homeTeam']['id'],
                'home_team_name': match['homeTeam']['name'],
                'home_team_short': match['homeTeam']['shortName'],
                'away_team_id': match['awayTeam']['id'],
                'away_team_name': match['awayTeam']['name'],
                'away_team_short': match['awayTeam']['shortName'],
                'home_score': match['score']['fullTime']['home'],
                'away_score': match['score']['fullTime']['away'],
                'home_score_ht': match['score']['halfTime']['home'],
                'away_score_ht': match['score']['halfTime']['away'],
                'duration': match['score'].get('duration', 'REGULAR'),
                'winner': match['score'].get('winner'),
                'referees': ', '.join([ref.get('name', '') for ref in match.get('referees', [])])
            })
        
        df_matches = pd.DataFrame(matches_list)
        
        # Tarih sütununu datetime'a çevir
        df_matches['utc_date'] = pd.to_datetime(df_matches['utc_date'])
        df_matches['match_date'] = df_matches['utc_date'].dt.date
        df_matches['match_time'] = df_matches['utc_date'].dt.time
        df_matches['match_month'] = df_matches['utc_date'].dt.month
        df_matches['match_day_of_week'] = df_matches['utc_date'].dt.day_name()
        
        # Sadece oynanan maçları filtrele
        df_matches_played = df_matches[df_matches['status'] == 'FINISHED'].copy()
        
        # Hesaplanan metrikleri ekle
        df_matches_played['total_goals'] = df_matches_played['home_score'] + df_matches_played['away_score']
        df_matches_played['is_draw'] = (df_matches_played['home_score'] == df_matches_played['away_score']).astype(int)
        df_matches_played['is_home_win'] = (df_matches_played['home_score'] > df_matches_played['away_score']).astype(int)
        df_matches_played['is_away_win'] = (df_matches_played['home_score'] < df_matches_played['away_score']).astype(int)
        df_matches_played['goal_difference'] = abs(df_matches_played['home_score'] - df_matches_played['away_score'])
        
        print(f"✅ {len(df_matches)} maçtan {len(df_matches_played)} tanesi işlendi (FINISHED)")
        
        return df_matches_played
    
    def save_to_csv(self, df, filename):
        """DataFrame'i CSV olarak kaydet"""
        filepath = os.path.join(self.processed_path, f"{filename}.csv")
        df.to_csv(filepath, index=False, encoding='utf-8')
        print(f"📁 CSV kaydedildi: {filepath}")
        return filepath
    
    def save_to_parquet(self, df, filename):
        """DataFrame'i Parquet olarak kaydet (daha verimli)"""
        filepath = os.path.join(self.processed_path, f"{filename}.parquet")
        df.to_parquet(filepath, index=False)
        print(f"📁 Parquet kaydedildi: {filepath}")
        return filepath

# Test
if __name__ == "__main__":
    transformer = FootballDataTransformer()
    
    # En son çekilen dosyaları bul
    files = os.listdir(RAW_DATA_PATH)
    
    # Standings dosyasını işle
    standings_files = [f for f in files if 'standings' in f and f.endswith('.json')]
    if standings_files:
        latest_standings = os.path.join(RAW_DATA_PATH, sorted(standings_files)[-1])
        print(f"\n📊 İşleniyor: {latest_standings}")
        
        df_standings = transformer.transform_standings(latest_standings)
        transformer.save_to_csv(df_standings, 'premier_league_standings')
        
        # İlk 5 takımı göster
        print("\n🏆 İlk 5 takım:")
        print(df_standings[['position', 'team_name', 'played_games', 'points', 'goal_difference']].head())
    
    # Matches dosyasını işle
    matches_files = [f for f in files if 'matches' in f and f.endswith('.json')]
    if matches_files:
        latest_matches = os.path.join(RAW_DATA_PATH, sorted(matches_files)[-1])
        print(f"\n📊 İşleniyor: {latest_matches}")
        
        df_matches = transformer.transform_matches(latest_matches)
        transformer.save_to_csv(df_matches, 'premier_league_matches')
        
        # Özet istatistikler
        print("\n📈 Maç İstatistikleri:")
        print(f"Toplam gol: {df_matches['total_goals'].sum()}")
        print(f"Maç başına ortalama gol: {df_matches['total_goals'].mean():.2f}")
        print(f"Ev sahibi galibiyeti: {df_matches['is_home_win'].sum()} ({df_matches['is_home_win'].mean()*100:.1f}%)")
        print(f"Beraberlik: {df_matches['is_draw'].sum()} ({df_matches['is_draw'].mean()*100:.1f}%)")
        print(f"Deplasman galibiyeti: {df_matches['is_away_win'].sum()} ({df_matches['is_away_win'].mean()*100:.1f}%)")