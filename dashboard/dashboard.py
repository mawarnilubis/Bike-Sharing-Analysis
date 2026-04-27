import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import os

# ─────────────────────────────────────────
# KONFIGURASI HALAMAN
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Bike Sharing Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────
# CUSTOM CSS 
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@400;500&display=swap');

/* ── Root & Body ── */
html, body, [class*="css"] {
    font-family: 'Syne', sans-serif !important;
}

/* ── Sembunyikan elemen bawaan Streamlit ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Background utama ── */
.stApp {
    background-color: #0D0F14;
    color: #E8E6E1;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #13161E !important;
    border-right: 1px solid rgba(0,198,184,0.15) !important;
}
[data-testid="stSidebar"] * {
    color: #C8C6C1 !important;
}
[data-testid="stSidebar"] h1 {
    color: #00C6B8 !important;
    font-size: 1.1rem !important;
    font-weight: 800 !important;
    letter-spacing: 0.05em !important;
}

/* ── Sidebar date input label ── */
[data-testid="stSidebar"] label {
    color: #888 !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
}

/* ── Judul utama ── */
h1 {
    font-size: 2rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em !important;
    color: #E8E6E1 !important;
}
h1 span.accent { color: #00C6B8; }

/* ── Subheader ── */
h2, h3, .stSubheader {
    font-size: 0.85rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: #888 !important;
    margin-top: 2rem !important;
}

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: #13161E;
    border: 1px solid rgba(0,198,184,0.15);
    border-left: 3px solid #00C6B8;
    border-radius: 12px;
    padding: 1.25rem 1.5rem !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: #666 !important;
}
[data-testid="stMetricValue"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 1.9rem !important;
    font-weight: 500 !important;
    color: #E8E6E1 !important;
    letter-spacing: -0.04em !important;
}

/* ── Divider ── */
hr {
    border: none !important;
    border-top: 1px solid rgba(0,198,184,0.12) !important;
    margin: 1.5rem 0 !important;
}

/* ── Plot containers ── */
.stPlotlyChart {
    background: #13161E;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 0.5rem;
}

/* ── Caption / Footer ── */
.stCaption {
    color: #444 !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.06em !important;
    text-align: center !important;
    font-family: 'DM Mono', monospace !important;
    margin-top: 2rem !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0D0F14; }
::-webkit-scrollbar-thumb { background: #00C6B8; border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# HELPER FUNCTIONS 
# ─────────────────────────────────────────
def create_daily_rentals_df(df):
    daily_rentals_df = df.resample(rule='D', on='dteday').agg({
        "cnt": "sum"
    }).reset_index()
    return daily_rentals_df

def create_byweather_df(df):
    byweather_df = df.groupby(by="weathersit").cnt.mean().reset_index()
    return byweather_df

def create_rfm_df(df):
    rfm_df = df.groupby(by="dteday", as_index=False).agg({
        "cnt": "sum"
    })
    rfm_df.columns = ["date", "total_rental"]
    recent_date = df["dteday"].max()
    rfm_df["recency"] = rfm_df["date"].apply(lambda x: (recent_date - x).days)
    return rfm_df

# ─────────────────────────────────────────
# LOAD DATA 
# ─────────────────────────────────────────
file_path = "main_data.csv"
if not os.path.exists(file_path):
    file_path = "dashboard/main_data.csv"

try:
    main_df = pd.read_csv(file_path)
    main_df["dteday"] = pd.to_datetime(main_df["dteday"])
except FileNotFoundError:
    st.error(f"File '{file_path}' tidak ditemukan. Pastikan file main_data.csv ada di folder yang sama dengan dashboard.py")
    st.stop()

# ─────────────────────────────────────────
# SIDEBAR 
# ─────────────────────────────────────────
with st.sidebar:
    st.title("Bike Sharing Analysis 🚲")
    # Logo SVG inline – sepeda + data, tidak butuh file/URL eksternal
    st.markdown("""
        <div style="margin:0.25rem 0 1.25rem;">
            <svg viewBox="0 0 220 80" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;">
              <circle cx="30" cy="55" r="18" fill="none" stroke="#00C6B8" stroke-width="3"/>
              <circle cx="30" cy="55" r="3" fill="#00C6B8"/>
              <circle cx="110" cy="55" r="18" fill="none" stroke="#00C6B8" stroke-width="3"/>
              <circle cx="110" cy="55" r="3" fill="#00C6B8"/>
              <line x1="30" y1="55" x2="65" y2="30" stroke="#00C6B8" stroke-width="2.5" stroke-linecap="round"/>
              <line x1="65" y1="30" x2="110" y2="55" stroke="#00C6B8" stroke-width="2.5" stroke-linecap="round"/>
              <line x1="65" y1="30" x2="70" y2="55" stroke="#00C6B8" stroke-width="2.5" stroke-linecap="round"/>
              <line x1="70" y1="55" x2="30" y2="55" stroke="#888" stroke-width="1.5" stroke-linecap="round"/>
              <line x1="65" y1="30" x2="63" y2="20" stroke="#00C6B8" stroke-width="2.5" stroke-linecap="round"/>
              <line x1="58" y1="20" x2="68" y2="20" stroke="#00C6B8" stroke-width="2.5" stroke-linecap="round"/>
              <line x1="70" y1="55" x2="72" y2="43" stroke="#00C6B8" stroke-width="2.5" stroke-linecap="round"/>
              <line x1="67" y1="42" x2="78" y2="42" stroke="#00C6B8" stroke-width="3" stroke-linecap="round"/>
              <rect x="138" y="50" width="8" height="18" rx="2" fill="#00C6B8" opacity="0.9"/>
              <rect x="150" y="38" width="8" height="30" rx="2" fill="#00C6B8" opacity="0.7"/>
              <rect x="162" y="28" width="8" height="40" rx="2" fill="#00C6B8" opacity="0.5"/>
              <rect x="174" y="43" width="8" height="25" rx="2" fill="#00C6B8" opacity="0.7"/>
              <rect x="186" y="33" width="8" height="35" rx="2" fill="#00C6B8" opacity="0.6"/>
              <line x1="134" y1="68" x2="198" y2="68" stroke="#00C6B8" stroke-width="1.5" stroke-linecap="round" opacity="0.4"/>
              <text x="130" y="16" font-family="monospace" font-size="11" font-weight="bold" fill="#00C6B8" letter-spacing="1">BIKE</text>
              <text x="155" y="16" font-family="monospace" font-size="11" fill="#888" letter-spacing="1">DATA</text>
            </svg>
        </div>
    """, unsafe_allow_html=True)

    min_date = main_df["dteday"].min()
    max_date = main_df["dteday"].max()

    try:
        start_date, end_date = st.date_input(
            label='Rentang Waktu',
            min_value=min_date,
            max_value=max_date,
            value=[min_date, max_date]
        )
    except ValueError:
        start_date = end_date = st.date_input(label='Rentang Waktu', value=min_date)

    st.markdown("---")
    st.markdown(
        "<p style='font-size:0.72rem;color:#444;letter-spacing:0.06em;text-transform:uppercase;'>Filter aktif</p>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"<p style='font-family:DM Mono,monospace;font-size:0.85rem;color:#00C6B8;'>"
        f"{start_date} → {end_date}</p>",
        unsafe_allow_html=True
    )

    st.markdown("---")

    # Biodata – menggunakan komponen native Streamlit agar tidak render sebagai teks
    st.caption("DIBUAT OLEH")
    col_av, col_bio = st.columns([1, 3])
    with col_av:
        st.markdown(
            "<div style=\"width:38px;height:38px;border-radius:50%;background:#00C6B8;"
            "display:flex;align-items:center;justify-content:center;"
            "font-weight:700;font-size:0.85rem;color:#0D0F14;margin-top:4px;\">"
            "ML</div>",
            unsafe_allow_html=True
        )
    with col_bio:
        st.markdown("**Mawarni Lubis**")
        st.caption("Data Science")
    st.markdown("🎓 &nbsp;**Informatika**", unsafe_allow_html=True)
    st.markdown("🏛️ &nbsp;Universitas Negeri Padang", unsafe_allow_html=True)

# ─────────────────────────────────────────
# FILTER DATA 
# ─────────────────────────────────────────
main_df = main_df[
    (main_df["dteday"] >= str(start_date)) &
    (main_df["dteday"] <= str(end_date))
]

# ─────────────────────────────────────────
# SIAPKAN DATA –
# ─────────────────────────────────────────
daily_rentals_df = create_daily_rentals_df(main_df)
byweather_df     = create_byweather_df(main_df)
rfm_df           = create_rfm_df(main_df)

# ─────────────────────────────────────────
# PLOTLY THEME 
# ─────────────────────────────────────────
PLOT_BG    = "#13161E"
PAPER_BG   = "#13161E"
FONT_COLOR = "#C8C6C1"
GRID_COLOR = "rgba(255,255,255,0.05)"
CYAN       = "#00C6B8"
GRAY       = "#888780"
GREEN      = "#639922"

BASE_LAYOUT = dict(
    paper_bgcolor=PAPER_BG,
    plot_bgcolor=PLOT_BG,
    font=dict(family="DM Mono, monospace", color=FONT_COLOR, size=12),
    margin=dict(l=16, r=16, t=16, b=16),
    xaxis=dict(gridcolor=GRID_COLOR, zeroline=False, linecolor="rgba(255,255,255,0.06)"),
    yaxis=dict(gridcolor=GRID_COLOR, zeroline=False, linecolor="rgba(255,255,255,0.06)"),
    hoverlabel=dict(
        bgcolor="#1E2230",
        bordercolor=CYAN,
        font=dict(family="DM Mono, monospace", color="#E8E6E1", size=12)
    )
)

# ─────────────────────────────────────────
# MAIN PAGE
# ─────────────────────────────────────────
st.markdown(
    "<h1>Bike<span style='color:#00C6B8;'>Share</span> Dashboard 🚲</h1>",
    unsafe_allow_html=True
)

# ── Metrics Utama ─────────────────────────
total_rentals = main_df.cnt.sum()     # sama persis dengan kode asli
avg_rentals   = main_df.cnt.mean()    # sama persis dengan kode asli

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Penyewaan", value=f"{total_rentals:,}")
with col2:
    st.metric("Rata-rata Harian", value=f"{round(avg_rentals, 2)}")
with col3:
    st.metric("Hari Terpilih", value=f"{len(daily_rentals_df):,}")
with col4:
    peak = int(daily_rentals_df["cnt"].max()) if not daily_rentals_df.empty else 0
    st.metric("Puncak Harian", value=f"{peak:,}")

st.markdown("---")

# ── Visualisasi 1: Tren Harian ────────────
st.subheader("Daily Rentals Trend")

fig_trend = go.Figure()
fig_trend.add_trace(go.Scatter(
    x=daily_rentals_df["dteday"],
    y=daily_rentals_df["cnt"],
    mode="lines+markers",
    line=dict(color=CYAN, width=2),
    marker=dict(size=4, color=CYAN, line=dict(width=0)),
    fill="tozeroy",
    fillcolor="rgba(0,198,184,0.08)",
    hovertemplate="<b>%{x|%d %b %Y}</b><br>Penyewaan: %{y:,}<extra></extra>"
))
fig_trend.update_layout(
    **BASE_LAYOUT,
    height=320,
    xaxis_title=None,
    yaxis_title="Jumlah Penyewaan",
)
st.plotly_chart(fig_trend, use_container_width=True)

# ── Visualisasi 2: Berdasarkan Cuaca ──────
st.subheader("Penyewaan Berdasarkan Kondisi Cuaca")

weather_labels = {1: "Cerah / Berawan Sebagian", 2: "Berkabut / Mendung", 3: "Hujan / Salju Ringan", 4: "Badai / Cuaca Buruk"}
byweather_plot = byweather_df.copy().sort_values(by="cnt", ascending=False)
byweather_plot["weathersit"] = byweather_plot["weathersit"].map(weather_labels).fillna(byweather_plot["weathersit"].astype(str))
colors_weather = [CYAN if i == 0 else GRAY for i in range(len(byweather_plot))]

fig_weather = go.Figure(go.Bar(
    x=byweather_plot["cnt"],
    y=byweather_plot["weathersit"],
    orientation="h",
    marker=dict(color=colors_weather, line=dict(width=0)),
    text=byweather_plot["cnt"].round(1),
    textposition="outside",
    textfont=dict(color=FONT_COLOR, size=11),
    hovertemplate="<b>%{y}</b><br>Rata-rata: %{x:,.1f} unit<extra></extra>"
))
fig_weather.update_layout(
    **BASE_LAYOUT,
    height=280,
    xaxis_title="Rata-rata Unit",
    yaxis_title=None,
    bargap=0.35,
)
st.plotly_chart(fig_weather, use_container_width=True)

# ── Visualisasi 3: RFM Analysis ───────────
st.subheader("Advanced Analysis: RFM (Harian)")

col_rfm1, col_rfm2 = st.columns(2)

# Recency histogram – sama persis dengan sns.histplot(rfm_df["recency"], bins=20, kde=True)
with col_rfm1:
    fig_recency = go.Figure()
    fig_recency.add_trace(go.Histogram(
        x=rfm_df["recency"],
        nbinsx=20,
        marker=dict(color=CYAN, line=dict(color="rgba(0,0,0,0)", width=0)),
        opacity=0.85,
        name="Recency",
        hovertemplate="Recency: %{x} hari<br>Frekuensi: %{y}<extra></extra>"
    ))
    # KDE overlay (approximasi smooth)
    import numpy as np
    from scipy.stats import gaussian_kde   # tersedia di scipy bawaan Streamlit
    r_vals = rfm_df["recency"].dropna().values
    if len(r_vals) > 1:
        kde_x = np.linspace(r_vals.min(), r_vals.max(), 300)
        kde_y = gaussian_kde(r_vals)(kde_x) * len(r_vals) * (r_vals.max() - r_vals.min()) / 20
        fig_recency.add_trace(go.Scatter(
            x=kde_x, y=kde_y,
            mode="lines",
            line=dict(color="#00E5D8", width=2),
            name="KDE",
            hoverinfo="skip"
        ))
    fig_recency.update_layout(
        **BASE_LAYOUT,
        height=300,
        title=dict(text="Recency (Hari dari Data Terakhir)", font=dict(size=13, color=FONT_COLOR), x=0),
        showlegend=False,
        bargap=0.05
    )
    st.plotly_chart(fig_recency, use_container_width=True)

# Monetary histogram – sama persis dengan sns.histplot(rfm_df["total_rental"], bins=20, kde=True)
with col_rfm2:
    fig_monetary = go.Figure()
    fig_monetary.add_trace(go.Histogram(
        x=rfm_df["total_rental"],
        nbinsx=20,
        marker=dict(color=GREEN, line=dict(color="rgba(0,0,0,0)", width=0)),
        opacity=0.85,
        name="Monetary",
        hovertemplate="Total: %{x:,}<br>Frekuensi: %{y}<extra></extra>"
    ))
    m_vals = rfm_df["total_rental"].dropna().values
    if len(m_vals) > 1:
        kde_x2 = np.linspace(m_vals.min(), m_vals.max(), 300)
        kde_y2 = gaussian_kde(m_vals)(kde_x2) * len(m_vals) * (m_vals.max() - m_vals.min()) / 20
        fig_monetary.add_trace(go.Scatter(
            x=kde_x2, y=kde_y2,
            mode="lines",
            line=dict(color="#8BD43A", width=2),
            name="KDE",
            hoverinfo="skip"
        ))
    fig_monetary.update_layout(
        **BASE_LAYOUT,
        height=300,
        title=dict(text="Monetary (Total Unit Tersewa)", font=dict(size=13, color=FONT_COLOR), x=0),
        showlegend=False,
        bargap=0.05
    )
    st.plotly_chart(fig_monetary, use_container_width=True)

# ─────────────────────────────────────────
# CONCLUSION & RECOMMENDATION
# ─────────────────────────────────────────
st.markdown("---")
st.subheader("Conclusion & Recommendation")

with st.container():
    tabs = st.tabs(["📊 Analisis Lingkungan", "👥 Analisis Pengguna", "💡 Rekomendasi"])

    with tabs[0]:
        st.markdown("""
        **Kesimpulan 1: Pengaruh Kondisi Cuaca & Suhu**
        * **Dominasi Cuaca:** Cuaca cerah adalah faktor penentu utama dengan rata-rata tertinggi (~4.876 unit). Sebaliknya, cuaca hujan/salju menurunkan minat hingga ~1.803 unit.
        * **Suhu:** Memiliki korelasi positif yang kuat ($0.63$). Semakin hangat suhu, semakin tinggi volume penyewaan.
        * **Hambatan:** Kelembaban dan angin berpengaruh negatif kecil, namun pengguna jauh lebih sensitif terhadap presipitasi (hujan/salju).
        """)
    with tabs[1]:
        st.markdown("""
        **Kesimpulan 2: Pola Pengguna Casual vs Registered**
        * **Registered (Komuter):** Menunjukkan pola *double peak* tajam pada pukul 08:00 dan 17:00-18:00 WIB, mengindikasikan penggunaan untuk transportasi kerja rutin.
        * **Casual (Rekreasi):** Pola meningkat stabil pada siang hingga sore hari (11:00-16:00 WIB), mengindikasikan motivasi rekreasi.
        * **Volume:** Pengguna *Registered* mendominasi total transaksi secara signifikan pada hari kerja.
        """)
    with tabs[2]:
        st.markdown("""
        **Strategi Bisnis:**
        1.  **Maintenance & Stok:** Fokuskan pemeliharaan sepeda pada jam non-sibuk (10:00-14:00 WIB) untuk memastikan ketersediaan saat jam pulang kerja.
        2.  **Promo Cuaca:** Memberikan insentif atau diskon khusus pada hari dengan cuaca kurang mendukung untuk menjaga volume penyewaan.
        3.  **Target Marketing:** Meningkatkan konversi pengguna *Casual* menjadi *Registered* melalui program loyalitas yang menargetkan jam rekreasi sore hari.
        """)

# ── Kesimpulan Hasil Analisis ────────────
st.markdown("---")
st.subheader("Kesimpulan Hasil Analisis")

col_k1, col_k2, col_k3 = st.columns(3)

with col_k1:
    st.markdown("""
    <div style="background:#13161E;border:1px solid rgba(0,198,184,0.15);border-top:3px solid #00C6B8;border-radius:12px;padding:1.25rem 1.5rem;">
        <div style="font-size:1.5rem;margin-bottom:0.5rem;">🌤️</div>
        <div style="font-size:0.7rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#555;margin-bottom:0.5rem;">Kondisi Cuaca</div>
        <div style="font-size:0.88rem;color:#C8C6C1;line-height:1.7;">
            Penyewaan sepeda mencapai puncaknya pada cuaca cerah
            (rata-rata <span style="color:#00C6B8;font-weight:700;">~4.876 unit</span>)
            dan menurun drastis saat hujan/salju.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_k2:
    st.markdown("""
    <div style="background:#13161E;border:1px solid rgba(0,198,184,0.15);border-top:3px solid #00C6B8;border-radius:12px;padding:1.25rem 1.5rem;">
        <div style="font-size:1.5rem;margin-bottom:0.5rem;">🌡️</div>
        <div style="font-size:0.7rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#555;margin-bottom:0.5rem;">Suhu</div>
        <div style="font-size:0.88rem;color:#C8C6C1;line-height:1.7;">
            Terdapat korelasi positif yang kuat
            (<span style="color:#00C6B8;font-weight:700;">0.63</span>),
            menunjukkan bahwa minat bersepeda meningkat seiring bertambahnya suhu udara.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_k3:
    st.markdown("""
    <div style="background:#13161E;border:1px solid rgba(0,198,184,0.15);border-top:3px solid #00C6B8;border-radius:12px;padding:1.25rem 1.5rem;">
        <div style="font-size:1.5rem;margin-bottom:0.5rem;">👥</div>
        <div style="font-size:0.7rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#555;margin-bottom:0.5rem;">Pola Pengguna</div>
        <div style="font-size:0.88rem;color:#C8C6C1;line-height:1.7;">
            Pengguna <span style="color:#00C6B8;font-weight:700;">Registered</span> memiliki pola komuter
            (puncak jam 08:00 &amp; 17:00), sementara pengguna
            <span style="color:#00C6B8;font-weight:700;">Casual</span> lebih dominan siang hari untuk rekreasi.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)

# ── Footer / Caption ──────────────────────
st.caption("Copyright (c) Mawarni Lubis 2026")