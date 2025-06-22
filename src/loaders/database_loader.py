# src/loaders/database_loader.py
import sqlite3
import pandas as pd
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from configs.config import PROCESSED_DATA_PATH

class DatabaseLoader:
    def __init__(self, db_path='data/football_data.db'):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Veritabanına bağlan"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        print(f"✅ Veritabanına bağlanıldı: {self.db_path}")
        
    def disconnect(self):
        """Bağlantıyı kapat"""
        if self.conn:
            self.conn.close()
            print("🔌 Veritabanı bağlantısı kapatıldı")
    
    def create_tables(self):
        """Tabloları oluştur"""
        schema_path = 'src/database/schema.sql'
        
        with open(schema_path, 'r') as f:
            schema = f.read()
        
        self.cursor.executescript(schema)
        self.conn.commit()
        print("✅ Tablolar oluşturuldu")
    
    def load_teams(self, standings_df):
        """Takımları veritabanına yükle"""
        # Unique takımları al
        teams_df = standings_df[['team_id', 'team_name', 'team_short_name', 'team_tla', 'crest_url']].drop_duplicates()
        
        # Veritabanına yükle
        for _, team in teams_df.iterrows():
            self.cursor.execute("""
                INSERT OR REPLACE INTO teams (team_id, team_name, team_short_name, team_tla, crest_url)
                VALUES (?, ?, ?, ?, ?)
            """, (team['team_id'], team['team_name'], team['team_short_name'], team['team_tla'], team['crest_url']))
        
        self.conn.commit()
        print(f"✅ {len(teams_df)} takım yüklendi")
        
    def load_season(self, standings_df):
        """Sezon bilgisini yükle"""
        season_info = standings_df[['competition_code', 'competition_name', 'season_start', 'season_end']].iloc[0]
        
        self.cursor.execute("""
            INSERT INTO seasons (competition_code, competition_name, season_start, season_end)
            VALUES (?, ?, ?, ?)
        """, (season_info['competition_code'], season_info['competition_name'], 
              season_info['season_start'], season_info['season_end']))
        
        season_id = self.cursor.lastrowid
        self.conn.commit()
        print(f"✅ Sezon yüklendi (ID: {season_id})")
        
        return season_id
    
    def load_standings(self, standings_df, season_id):
        """Puan durumunu yükle"""
        standings_df['season_id'] = season_id
        standings_df['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # String formatına çevir
        
        columns = ['season_id', 'team_id', 'position', 'played_games', 'won', 'draw', 'lost', 
                'points', 'goals_for', 'goals_against', 'goal_difference', 'form', 
                'win_percentage', 'points_per_game', 'goals_per_game', 'goals_conceded_per_game', 
                'last_updated']
        
        # form_points varsa ekle
        if 'form_points' in standings_df.columns:
            columns.insert(columns.index('form') + 1, 'form_points')
        
        for _, row in standings_df.iterrows():
            values = []
            for col in columns:
                value = row[col]
                # NaN değerleri None'a çevir
                if pd.isna(value):
                    values.append(None)
                # Timestamp objelerini string'e çevir
                elif hasattr(value, 'strftime'):
                    values.append(value.strftime('%Y-%m-%d %H:%M:%S'))
                else:
                    values.append(value)
            
            placeholders = ','.join(['?' for _ in columns])
            query = f"INSERT INTO standings ({','.join(columns)}) VALUES ({placeholders})"
            self.cursor.execute(query, values)
        
        self.conn.commit()
        print(f"✅ {len(standings_df)} takımın puan durumu yüklendi")
    
    def load_matches(self, matches_df, season_id):
        """Maçları yükle"""
        matches_df['season_id'] = season_id
        
        # match_date ve match_time sütunlarını string'e çevir
        if 'match_date' in matches_df.columns:
            matches_df['match_date'] = pd.to_datetime(matches_df['match_date']).dt.strftime('%Y-%m-%d')
        
        if 'match_time' in matches_df.columns:
            matches_df['match_time'] = matches_df['match_time'].astype(str)
        
        columns = ['match_id', 'season_id', 'match_date', 'match_time', 'matchday',
                'home_team_id', 'away_team_id', 'home_score', 'away_score',
                'home_score_ht', 'away_score_ht', 'status', 'total_goals',
                'goal_difference', 'is_draw', 'is_home_win', 'is_away_win', 'referees']
        
        for _, row in matches_df.iterrows():
            values = []
            for col in columns:
                value = row[col] if col in row else None
                # NaN değerleri None'a çevir
                if pd.isna(value):
                    values.append(None)
                # Timestamp objelerini string'e çevir
                elif hasattr(value, 'strftime'):
                    values.append(value.strftime('%Y-%m-%d %H:%M:%S'))
                else:
                    values.append(value)
            
            placeholders = ','.join(['?' for _ in columns])
            query = f"INSERT OR REPLACE INTO matches ({','.join(columns)}) VALUES ({placeholders})"
            self.cursor.execute(query, values)
        
        self.conn.commit()
        print(f"✅ {len(matches_df)} maç yüklendi")
    
    def get_statistics(self):
        """Veritabanı istatistiklerini göster"""
        stats = {}
        
        # Tablo istatistikleri
        tables = ['teams', 'seasons', 'standings', 'matches']
        for table in tables:
            self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
            stats[table] = self.cursor.fetchone()[0]
        
        print("\n📊 Veritabanı İstatistikleri:")
        for table, count in stats.items():
            print(f"  - {table}: {count} kayıt")
        
        return stats

# Test
if __name__ == "__main__":
    # CSV dosyalarını yükle
    standings_df = pd.read_csv(os.path.join(PROCESSED_DATA_PATH, 'premier_league_standings.csv'))
    matches_df = pd.read_csv(os.path.join(PROCESSED_DATA_PATH, 'premier_league_matches.csv'))
    
    # Veritabanı işlemleri
    loader = DatabaseLoader()
    
    try:
        loader.connect()
        loader.create_tables()
        
        # Verileri yükle
        loader.load_teams(standings_df)
        season_id = loader.load_season(standings_df)
        loader.load_standings(standings_df, season_id)
        loader.load_matches(matches_df, season_id)
        
        # İstatistikleri göster
        loader.get_statistics()
        
    finally:
        loader.disconnect()