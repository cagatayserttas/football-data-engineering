# src/database/test_queries.py
import sqlite3
import pandas as pd

def test_database():
    conn = sqlite3.connect('data/football_data.db')
    
    # Test sorguları
    queries = {
        "Top 5 Takım": """
            SELECT t.team_name, s.position, s.points, s.goal_difference
            FROM standings s
            JOIN teams t ON s.team_id = t.team_id
            ORDER BY s.position
            LIMIT 5
        """,
        
        "En Çok Gol Atan Takımlar": """
            SELECT t.team_name, s.goals_for, s.goals_per_game
            FROM standings s
            JOIN teams t ON s.team_id = t.team_id
            ORDER BY s.goals_for DESC
            LIMIT 5
        """,
        
        "En Çok Gol Yenen Maçlar": """
            SELECT 
                h.team_name as home_team,
                a.team_name as away_team,
                m.home_score,
                m.away_score,
                m.total_goals,
                m.match_date
            FROM matches m
            JOIN teams h ON m.home_team_id = h.team_id
            JOIN teams a ON m.away_team_id = a.team_id
            ORDER BY m.total_goals DESC
            LIMIT 10
        """
    }
    
    for title, query in queries.items():
        print(f"\n📊 {title}:")
        df = pd.read_sql_query(query, conn)
        print(df)
    
    conn.close()

if __name__ == "__main__":
    test_database()