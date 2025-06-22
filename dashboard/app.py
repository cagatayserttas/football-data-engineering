# dashboard/app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
from datetime import datetime
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Sayfa ayarları
st.set_page_config(
    page_title="Premier League Analiz Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS stil eklemeleri
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1e3d59;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_connection():
    """Veritabanı bağlantısı"""
    # Dashboard klasöründen çalıştığımız için bir üst klasöre çıkmalıyız
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'football_data.db')
    
    if not os.path.exists(db_path):
        st.error(f"Veritabanı dosyası bulunamadı: {db_path}")
        st.info("Lütfen önce veri yükleme scriptlerini çalıştırın.")
        st.stop()
    
    return sqlite3.connect(db_path, check_same_thread=False)

@st.cache_data
def load_standings():
    """Puan durumunu yükle"""
    query = """
        SELECT 
            t.team_name,
            s.position,
            s.played_games,
            s.won,
            s.draw,
            s.lost,
            s.points,
            s.goals_for,
            s.goals_against,
            s.goal_difference,
            s.form,
            s.points_per_game,
            s.goals_per_game
        FROM standings s
        JOIN teams t ON s.team_id = t.team_id
        ORDER BY s.position
    """
    return pd.read_sql_query(query, get_connection())

@st.cache_data
def load_matches():
    """Maç verilerini yükle"""
    query = """
        SELECT 
            m.*,
            h.team_name as home_team_name,
            a.team_name as away_team_name
        FROM matches m
        JOIN teams h ON m.home_team_id = h.team_id
        JOIN teams a ON m.away_team_id = a.team_id
        WHERE m.status = 'FINISHED'
    """
    return pd.read_sql_query(query, get_connection())

@st.cache_data
def get_team_stats():
    """Takım istatistikleri"""
    query = """
        SELECT 
            t.team_name,
            COUNT(CASE WHEN m.home_team_id = t.team_id THEN 1 END) as home_games,
            COUNT(CASE WHEN m.away_team_id = t.team_id THEN 1 END) as away_games,
            SUM(CASE WHEN m.home_team_id = t.team_id AND m.is_home_win = 1 THEN 1
                     WHEN m.away_team_id = t.team_id AND m.is_away_win = 1 THEN 1 ELSE 0 END) as total_wins,
            SUM(CASE WHEN m.home_team_id = t.team_id AND m.is_home_win = 1 THEN 1 ELSE 0 END) as home_wins,
            SUM(CASE WHEN m.away_team_id = t.team_id AND m.is_away_win = 1 THEN 1 ELSE 0 END) as away_wins,
            AVG(CASE WHEN m.home_team_id = t.team_id THEN m.home_score
                     WHEN m.away_team_id = t.team_id THEN m.away_score END) as avg_goals_scored,
            AVG(CASE WHEN m.home_team_id = t.team_id THEN m.away_score
                     WHEN m.away_team_id = t.team_id THEN m.home_score END) as avg_goals_conceded
        FROM teams t
        LEFT JOIN matches m ON m.home_team_id = t.team_id OR m.away_team_id = t.team_id
        WHERE m.status = 'FINISHED'
        GROUP BY t.team_id, t.team_name
    """
    return pd.read_sql_query(query, get_connection())

def main():
    # Başlık
    st.markdown('<h1 class="main-header">⚽ Premier League 2023/24 Analiz Dashboard</h1>', unsafe_allow_html=True)
    
    # Yan menü
    st.sidebar.title("📊 Menü")
    page = st.sidebar.radio("Sayfa Seçin:", 
                            ["🏠 Ana Sayfa", "📊 Puan Durumu", "⚽ Maç Analizi", "📈 Takım Performansı", "🎯 Detaylı İstatistikler"])
    
    if page == "🏠 Ana Sayfa":
        show_homepage()
    elif page == "📊 Puan Durumu":
        show_standings()
    elif page == "⚽ Maç Analizi":
        show_match_analysis()
    elif page == "📈 Takım Performansı":
        show_team_performance()
    elif page == "🎯 Detaylı İstatistikler":
        show_detailed_stats()

def show_homepage():
    """Ana sayfa"""
    st.subheader("🏆 Sezon Özeti")
    
    # Temel metrikler
    standings_df = load_standings()
    matches_df = load_matches()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🏆 Şampiyon", standings_df.iloc[0]['team_name'])
        
    with col2:
        total_goals = matches_df['total_goals'].sum()
        st.metric("⚽ Toplam Gol", f"{total_goals:,}")
        
    with col3:
        avg_goals = matches_df['total_goals'].mean()
        st.metric("📊 Ortalama Gol/Maç", f"{avg_goals:.2f}")
        
    with col4:
        home_win_pct = (matches_df['is_home_win'].sum() / len(matches_df) * 100)
        st.metric("🏠 Ev Sahibi Galibiyet %", f"{home_win_pct:.1f}%")
    
    # Top 5 takım grafiği
    st.subheader("📊 İlk 5 Takım")
    top5 = standings_df.head()
    
    fig = px.bar(top5, x='team_name', y='points', 
                 color='points',
                 color_continuous_scale='Blues',
                 title='Puan Durumu - İlk 5')
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Gol istatistikleri
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚽ En Çok Gol Atan Takımlar")
        top_scorers = standings_df.nlargest(5, 'goals_for')[['team_name', 'goals_for']]
        fig_goals = px.bar(top_scorers, x='goals_for', y='team_name', 
                          orientation='h',
                          color='goals_for',
                          color_continuous_scale='Reds')
        fig_goals.update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_goals, use_container_width=True)
    
    with col2:
        st.subheader("🛡️ En Az Gol Yiyen Takımlar")
        best_defense = standings_df.nsmallest(5, 'goals_against')[['team_name', 'goals_against']]
        fig_defense = px.bar(best_defense, x='goals_against', y='team_name', 
                            orientation='h',
                            color='goals_against',
                            color_continuous_scale='Greens_r')
        fig_defense.update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_defense, use_container_width=True)

def show_standings():
    """Puan durumu sayfası"""
    st.subheader("📊 Puan Durumu Tablosu")
    
    standings_df = load_standings()
    
    # Renklendirme için stil
    def highlight_positions(row):
        if row['position'] <= 4:
            return ['background-color: #90EE90'] * len(row)  # Champions League
        elif row['position'] == 5:
            return ['background-color: #FFE4B5'] * len(row)  # Europa League
        elif row['position'] >= 18:
            return ['background-color: #FFB6C1'] * len(row)  # Küme düşme
        else:
            return [''] * len(row)
    
    # Tabloyu göster
    styled_df = standings_df.style.apply(highlight_positions, axis=1)
    st.dataframe(styled_df, height=750, use_container_width=True)
    
    # Açıklama
    st.markdown("""
    **Renk Kodları:**
    - 🟢 Yeşil: Champions League (1-4)
    - 🟡 Sarı: Europa League (5)
    - 🔴 Kırmızı: Küme Düşme (18-20)
    """)

def show_match_analysis():
    """Maç analizi sayfası"""
    st.subheader("⚽ Maç Analizleri")
    
    matches_df = load_matches()
    
    # Filtreleme seçenekleri
    col1, col2 = st.columns(2)
    
    with col1:
        selected_team = st.selectbox("Takım Seçin:", ["Tüm Takımlar"] + sorted(matches_df['home_team_name'].unique().tolist()))
    
    with col2:
        matchday = st.slider("Hafta Aralığı:", 1, 38, (1, 38))
    
    # Filtreleme
    filtered_df = matches_df.copy()
    
    if selected_team != "Tüm Takımlar":
        filtered_df = filtered_df[(filtered_df['home_team_name'] == selected_team) | 
                                  (filtered_df['away_team_name'] == selected_team)]
    
    filtered_df = filtered_df[(filtered_df['matchday'] >= matchday[0]) & 
                              (filtered_df['matchday'] <= matchday[1])]
    
    # İstatistikler
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_home_goals = filtered_df['home_score'].mean()
        st.metric("🏠 Ort. Ev Sahibi Golü", f"{avg_home_goals:.2f}")
    
    with col2:
        avg_away_goals = filtered_df['away_score'].mean()
        st.metric("✈️ Ort. Deplasman Golü", f"{avg_away_goals:.2f}")
    
    with col3:
        high_scoring_games = len(filtered_df[filtered_df['total_goals'] > 3])
        st.metric("🎯 3+ Gollü Maçlar", high_scoring_games)
    
    # Gol dağılımı
    st.subheader("📊 Maçlardaki Gol Dağılımı")
    goal_dist = filtered_df['total_goals'].value_counts().sort_index()
    
    fig = px.bar(x=goal_dist.index, y=goal_dist.values,
                 labels={'x': 'Toplam Gol', 'y': 'Maç Sayısı'},
                 title='Maçlardaki Toplam Gol Dağılımı')
    st.plotly_chart(fig, use_container_width=True)
    
    # En yüksek skorlu maçlar
    st.subheader("🔥 En Çok Gollü Maçlar")
    top_matches = filtered_df.nlargest(10, 'total_goals')[
        ['match_date', 'home_team_name', 'home_score', 'away_score', 'away_team_name', 'total_goals']
    ]
    st.dataframe(top_matches, use_container_width=True)

def show_team_performance():
    """Takım performans analizi"""
    st.subheader("📈 Takım Performans Analizi")
    
    standings_df = load_standings()
    team_stats_df = get_team_stats()
    
    # Takım seçimi
    selected_team = st.selectbox("Takım Seçin:", sorted(standings_df['team_name'].tolist()))
    
    # Takım bilgileri
    team_data = standings_df[standings_df['team_name'] == selected_team].iloc[0]
    team_stats = team_stats_df[team_stats_df['team_name'] == selected_team].iloc[0]
    
    # Metrikler
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📍 Lig Sıralaması", f"{int(team_data['position'])}")
        st.metric("🎯 Puan", f"{int(team_data['points'])}")
    
    with col2:
        st.metric("✅ Galibiyet", f"{int(team_data['won'])}")
        st.metric("🤝 Beraberlik", f"{int(team_data['draw'])}")
    
    with col3:
        st.metric("❌ Mağlubiyet", f"{int(team_data['lost'])}")
        st.metric("⚽ Atılan Gol", f"{int(team_data['goals_for'])}")
    
    with col4:
        st.metric("🚫 Yenilen Gol", f"{int(team_data['goals_against'])}")
        st.metric("📊 Averaj", f"{int(team_data['goal_difference'])}")
    
    # Ev/Deplasman performansı
    st.subheader("🏠 Ev Sahibi vs ✈️ Deplasman Performansı")
    
    col1, col2 = st.columns(2)
    
    with col1:
        home_away_data = pd.DataFrame({
            'Konum': ['Ev Sahibi', 'Deplasman'],
            'Galibiyet': [int(team_stats['home_wins']), int(team_stats['away_wins'])],
            'Maç': [int(team_stats['home_games']), int(team_stats['away_games'])]
        })
        home_away_data['Galibiyet %'] = (home_away_data['Galibiyet'] / home_away_data['Maç'] * 100).round(1)
        
        fig = px.bar(home_away_data, x='Konum', y='Galibiyet %',
                     color='Konum',
                     color_discrete_map={'Ev Sahibi': '#1f77b4', 'Deplasman': '#ff7f0e'},
                     title='Ev Sahibi vs Deplasman Galibiyet Oranı')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Form grafiği
        if team_data['form']:
            form_data = []
            for i, result in enumerate(team_data['form'][-5:]):
                form_data.append({
                    'Maç': i+1,
                    'Sonuç': result,
                    'Puan': 3 if result == 'W' else (1 if result == 'D' else 0)
                })
            form_df = pd.DataFrame(form_data)
            
            fig = px.line(form_df, x='Maç', y='Puan', 
                         markers=True,
                         title='Son 5 Maç Formu')
            fig.update_yaxis(range=[-0.5, 3.5], tickvals=[0, 1, 3], ticktext=['L', 'D', 'W'])
            st.plotly_chart(fig, use_container_width=True)
    
    # Takımın tüm maçları
    st.subheader("📅 Sezon Maçları")
    matches_df = load_matches()
    team_matches = matches_df[(matches_df['home_team_name'] == selected_team) | 
                              (matches_df['away_team_name'] == selected_team)].copy()
    
    # Sonuç sütunu ekle
    def get_result(row, team):
        if row['home_team_name'] == team:
            if row['is_home_win'] == 1:
                return 'W'
            elif row['is_draw'] == 1:
                return 'D'
            else:
                return 'L'
        else:
            if row['is_away_win'] == 1:
                return 'W'
            elif row['is_draw'] == 1:
                return 'D'
            else:
                return 'L'
    
    team_matches['result'] = team_matches.apply(lambda x: get_result(x, selected_team), axis=1)
    team_matches['match_display'] = team_matches.apply(
        lambda x: f"{x['home_team_name']} {x['home_score']}-{x['away_score']} {x['away_team_name']}", axis=1
    )
    
    # Renklendirme
    def color_result(val):
        if val == 'W':
            return 'background-color: #90EE90'
        elif val == 'D':
            return 'background-color: #FFE4B5'
        elif val == 'L':
            return 'background-color: #FFB6C1'
        return ''
    
    display_cols = ['match_date', 'matchday', 'match_display', 'result']
    styled_matches = team_matches[display_cols].style.applymap(color_result, subset=['result'])
    
    st.dataframe(styled_matches, use_container_width=True, height=500)

def show_detailed_stats():
    """Detaylı istatistikler"""
    st.subheader("🎯 Detaylı İstatistikler")
    
    standings_df = load_standings()
    matches_df = load_matches()
    
    # Tab'lar
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Lig İstatistikleri", "👥 Kafa Kafaya", "📈 Trendler", "🏆 Rekorlar"])
    
    with tab1:
        # Lig geneli istatistikler
        col1, col2 = st.columns(2)
        
        with col1:
            # Puan/Maç dağılımı
            fig = px.scatter(standings_df, x='played_games', y='points',
                           size='goals_for', color='position',
                           hover_data=['team_name'],
                           title='Puan vs Oynanan Maç (Gol Sayısına Göre)',
                           color_continuous_scale='RdYlGn_r')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Atak vs Savunma
            fig = px.scatter(standings_df, x='goals_for', y='goals_against',
                           color='points', size='points',
                           hover_data=['team_name', 'position'],
                           title='Atak vs Savunma Performansı',
                           color_continuous_scale='Blues')
            fig.add_hline(y=standings_df['goals_against'].mean(), line_dash="dash", line_color="gray")
            fig.add_vline(x=standings_df['goals_for'].mean(), line_dash="dash", line_color="gray")
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Kafa kafaya karşılaştırma
        st.subheader("👥 Takım Karşılaştırması")
        
        col1, col2 = st.columns(2)
        with col1:
            team1 = st.selectbox("Takım 1:", sorted(standings_df['team_name'].tolist()), key="team1")
        with col2:
            team2 = st.selectbox("Takım 2:", sorted(standings_df['team_name'].tolist()), key="team2", index=1)
        
        if team1 != team2:
            # H2H maçları
            h2h_matches = matches_df[
                ((matches_df['home_team_name'] == team1) & (matches_df['away_team_name'] == team2)) |
                ((matches_df['home_team_name'] == team2) & (matches_df['away_team_name'] == team1))
            ]
            
            if not h2h_matches.empty:
                st.subheader("🤝 Karşılaşmalar")
                for _, match in h2h_matches.iterrows():
                    st.write(f"📅 {match['match_date']}: {match['home_team_name']} {match['home_score']}-{match['away_score']} {match['away_team_name']}")
            
            # Karşılaştırma radar chart
            team1_data = standings_df[standings_df['team_name'] == team1].iloc[0]
            team2_data = standings_df[standings_df['team_name'] == team2].iloc[0]
            
            categories = ['Puan', 'Galibiyet', 'Atılan Gol', 'Az Yenilen Gol', 'Puan/Maç']
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=[team1_data['points'], team1_data['won'], team1_data['goals_for'], 
                   38-team1_data['goals_against'], team1_data['points_per_game']*10],
                theta=categories,
                fill='toself',
                name=team1
            ))
            
            fig.add_trace(go.Scatterpolar(
                r=[team2_data['points'], team2_data['won'], team2_data['goals_for'], 
                   38-team2_data['goals_against'], team2_data['points_per_game']*10],
                theta=categories,
                fill='toself',
                name=team2
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100])
                ),
                title="Takım Performans Karşılaştırması",
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Sezon içi trendler
        st.subheader("📈 Sezon İçi Trendler")
        
        # Haftalık gol ortalaması
        weekly_goals = matches_df.groupby('matchday')['total_goals'].agg(['sum', 'count', 'mean'])
        weekly_goals['avg_goals'] = weekly_goals['mean']
        
        fig = px.line(weekly_goals.reset_index(), x='matchday', y='avg_goals',
                     title='Haftalık Ortalama Gol Sayısı',
                     labels={'matchday': 'Hafta', 'avg_goals': 'Ortalama Gol'})
        fig.add_hline(y=weekly_goals['avg_goals'].mean(), line_dash="dash", 
                     line_color="red", annotation_text="Sezon Ortalaması")
        st.plotly_chart(fig, use_container_width=True)
        
        # Ev sahibi avantajı trendi
        home_advantage = matches_df.groupby('matchday')[['is_home_win', 'is_draw', 'is_away_win']].mean() * 100
        
        fig = px.area(home_advantage.reset_index(), x='matchday', 
                     y=['is_home_win', 'is_draw', 'is_away_win'],
                     title='Maç Sonucu Dağılımı (%)',
                     labels={'value': 'Yüzde (%)', 'matchday': 'Hafta'},
                     color_discrete_map={'is_home_win': '#2E7D32', 'is_draw': '#FFA000', 'is_away_win': '#C62828'})
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        # Rekorlar
        st.subheader("🏆 Sezon Rekorları")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ⚽ Gol Rekorları")
            
            # En çok gol atan takım
            top_scorer = standings_df.nlargest(1, 'goals_for').iloc[0]
            st.metric("En Çok Gol Atan", top_scorer['team_name'], f"{int(top_scorer['goals_for'])} gol")
            
            # En az gol yiyen takım
            best_defense = standings_df.nsmallest(1, 'goals_against').iloc[0]
            st.metric("En Az Gol Yiyen", best_defense['team_name'], f"{int(best_defense['goals_against'])} gol")
            
            # En yüksek skorlu maç
            highest_scoring = matches_df.nlargest(1, 'total_goals').iloc[0]
            st.metric("En Çok Gollü Maç", 
                     f"{highest_scoring['home_team_name']} {int(highest_scoring['home_score'])}-{int(highest_scoring['away_score'])} {highest_scoring['away_team_name']}", 
                     f"{int(highest_scoring['total_goals'])} gol")
        
        with col2:
            st.markdown("### 🏃 Seri Rekorları")
            
            # En uzun galibiyet serisi
            longest_win_streak = 0
            longest_win_team = ""
            
            for team in standings_df['team_name']:
                team_form = standings_df[standings_df['team_name'] == team]['form'].iloc[0]
                if team_form:
                    current_streak = 0
                    max_streak = 0
                    for result in team_form:
                        if result == 'W':
                            current_streak += 1
                            max_streak = max(max_streak, current_streak)
                        else:
                            current_streak = 0
                    if max_streak > longest_win_streak:
                        longest_win_streak = max_streak
                        longest_win_team = team
            
            if longest_win_team:
                st.metric("En Uzun Galibiyet Serisi", longest_win_team, f"{longest_win_streak} maç")
            
            # En yüksek puan/maç oranı
            best_ppg = standings_df.nlargest(1, 'points_per_game').iloc[0]
            st.metric("En Yüksek Puan/Maç", best_ppg['team_name'], f"{best_ppg['points_per_game']:.2f}")

if __name__ == "__main__":
    main()