from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

# ----------------------------------------------------------------------
# Konfigurasi halaman & gaya visual
# ----------------------------------------------------------------------
st.set_page_config(page_title="Bike Sharing Dashboard", page_icon="🚲", layout="wide")
sns.set_theme(style="whitegrid", font_scale=0.95)

C_PRIMARY = "#2A6F97"   # warna utama
C_ACCENT = "#E07A5F"    # warna penekanan / sorotan
C_MUTED = "#B8C0C8"     # warna pendukung

BASE_DIR = Path(__file__).parent
SEASONS = ["Dingin", "Semi", "Panas", "Gugur"]
WEATHERS = ["Cerah", "Berkabut/Berawan", "Hujan/Salju Ringan", "Hujan/Salju Lebat"]
DAY_TYPES = ["Hari Kerja", "Akhir Pekan/Libur"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
WEEKDAYS = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
TEMP_LABELS = ["Dingin (<10°C)", "Sejuk (10–20°C)", "Hangat (20–30°C)", "Panas (≥30°C)"]


def fmt(n):
    """Format angka ribuan dengan pemisah titik (gaya Indonesia)."""
    return f"{n:,.0f}".replace(",", ".")


# ----------------------------------------------------------------------
# Load data
# ----------------------------------------------------------------------
@st.cache_data
def load_data():
    hour = pd.read_csv(BASE_DIR / "main_data.csv", parse_dates=["dteday"])
    day = pd.read_csv(BASE_DIR / "day_data.csv", parse_dates=["dteday"])
    for df in (hour, day):
        df["season_label"] = pd.Categorical(df["season_label"], SEASONS, ordered=True)
        df["weather_label"] = pd.Categorical(df["weather_label"], WEATHERS, ordered=True)
        df["day_type"] = pd.Categorical(df["day_type"], DAY_TYPES, ordered=True)
        df["weekday_name"] = pd.Categorical(df["weekday_name"], WEEKDAYS, ordered=True)
    return hour, day


hour_df, day_df = load_data()

# ----------------------------------------------------------------------
# Sidebar: filter
# ----------------------------------------------------------------------
st.sidebar.title("🚲 Filter Data")
min_date, max_date = day_df["dteday"].min().date(), day_df["dteday"].max().date()
date_range = st.sidebar.date_input(
    "Rentang tanggal", value=(min_date, max_date), min_value=min_date, max_value=max_date
)
if isinstance(date_range, (tuple, list)):
    if len(date_range) > 0:
        start_date, end_date = date_range[0], date_range[-1]
    else:
        start_date, end_date = min_date, max_date
else:
    start_date = end_date = date_range

selected_types = st.sidebar.multiselect("Tipe hari", DAY_TYPES, default=DAY_TYPES)

mask_h = (
    (hour_df["dteday"].dt.date >= start_date)
    & (hour_df["dteday"].dt.date <= end_date)
    & (hour_df["day_type"].isin(selected_types))
)
mask_d = (
    (day_df["dteday"].dt.date >= start_date)
    & (day_df["dteday"].dt.date <= end_date)
    & (day_df["day_type"].isin(selected_types))
)
hour_f, day_f = hour_df[mask_h], day_df[mask_d]

st.sidebar.caption(
    "Dataset: Capital Bikeshare, Washington D.C. (2011–2012). "
    "Filter berlaku untuk seluruh visualisasi."
)

# ----------------------------------------------------------------------
# Header & KPI
# ----------------------------------------------------------------------
st.title("🚲 Dashboard Analisis Bike Sharing")
st.markdown(
    "Dashboard ini merangkum pola penyewaan sepeda Capital Bikeshare (2011–2012) "
    "untuk membantu operator mengatur distribusi armada, jadwal perawatan, dan promosi."
)

if day_f.empty or hour_f.empty:
    st.warning("Tidak ada data pada filter yang dipilih. Ubah rentang tanggal atau tipe hari.")
    st.stop()

total_rent = int(day_f["cnt"].sum())
avg_daily = day_f["cnt"].mean()
casual_share = day_f["casual"].sum() / total_rent * 100
n_days = day_f["dteday"].nunique()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Penyewaan", fmt(total_rent))
k2.metric("Rata-rata per Hari", fmt(avg_daily))
k3.metric("Jumlah Hari", fmt(n_days))
k4.metric("Porsi Pengguna Casual", f"{casual_share:.1f}%")

st.divider()

tab1, tab2, tab3, tab4 = st.tabs(
    ["⏰ Pola per Jam", "🌦️ Musim & Cuaca", "📈 Tren Bulanan", "🔍 Analisis Lanjutan"]
)

# ----------------------------------------------------------------------
# Tab 1: Pola per jam (Pertanyaan 1)
# ----------------------------------------------------------------------
with tab1:
    st.subheader("Kapan jam puncak penyewaan sepeda?")
    hourly = hour_f.groupby(["day_type", "hr"], observed=True)["cnt"].mean().unstack(0)

    fig, ax = plt.subplots(figsize=(10, 4.5))
    colors = {"Hari Kerja": C_PRIMARY, "Akhir Pekan/Libur": C_ACCENT}
    for col in hourly.columns:
        s = hourly[col].dropna()
        ax.plot(s.index, s.values, marker="o", lw=2.4, color=colors[col], label=col)
        peak_hr = int(s.idxmax())
        ax.annotate(
            f"Puncak {peak_hr:02d}:00\n({s.max():.0f})",
            xy=(peak_hr, s.max()),
            xytext=(peak_hr + 0.6, s.max() + 25),
            fontsize=9,
            color=colors[col],
            arrowprops=dict(arrowstyle="-", color=colors[col]),
        )
    ax.set_xticks(range(0, 24, 2))
    ax.set_xticklabels([f"{h:02d}" for h in range(0, 24, 2)])
    ax.set_xlabel("Jam dalam sehari")
    ax.set_ylabel("Rata-rata penyewaan per jam")
    ax.set_title("Rata-rata penyewaan per jam: hari kerja vs akhir pekan/libur", loc="left", fontweight="bold")
    ax.legend(frameon=False)
    sns.despine()
    st.pyplot(fig)
    plt.close(fig)

    lines = []
    for col in hourly.columns:
        s = hourly[col].dropna()
        top3 = ", ".join(f"{int(h):02d}:00 ({v:.0f})" for h, v in s.nlargest(3).items())
        lines.append(f"- **{col}** — tiga jam teratas: {top3}")
    st.markdown("\n".join(lines))
    st.caption(
        "Hari kerja punya dua puncak (komuter pagi & sore), sedangkan akhir pekan/libur "
        "membentuk satu puncak landai pada siang hari."
    )

# ----------------------------------------------------------------------
# Tab 2: Musim & cuaca (Pertanyaan 2)
# ----------------------------------------------------------------------
with tab2:
    st.subheader("Seberapa besar pengaruh musim dan cuaca?")
    by_season = day_f.groupby("season_label", observed=True)["cnt"].mean()
    by_weather = day_f.groupby("weather_label", observed=True)["cnt"].mean()

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    ax = axes[0]
    colors_s = [C_PRIMARY if v == by_season.max() else C_MUTED for v in by_season.values]
    bars = ax.bar(by_season.index.astype(str), by_season.values, color=colors_s)
    ax.bar_label(bars, labels=[fmt(v) for v in by_season.values], padding=3, fontsize=9)
    ax.set_title("Rata-rata penyewaan harian per musim", loc="left", fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("Penyewaan per hari")
    ax.set_ylim(0, by_season.max() * 1.18)

    ax = axes[1]
    if "Cerah" in by_weather.index:
        ref = by_weather["Cerah"]
        labels_w = [
            fmt(v) if w == "Cerah" else f"{fmt(v)}\n({(v / ref - 1) * 100:+.1f}%)"
            for w, v in by_weather.items()
        ]
    else:
        labels_w = [fmt(v) for v in by_weather.values]
    colors_w = [C_ACCENT if v == by_weather.min() else C_MUTED for v in by_weather.values]
    bars = ax.bar(by_weather.index.astype(str), by_weather.values, color=colors_w)
    ax.bar_label(bars, labels=labels_w, padding=3, fontsize=9)
    ax.set_title("Rata-rata penyewaan harian per kondisi cuaca", loc="left", fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_ylim(0, by_weather.max() * 1.25)
    ax.tick_params(axis="x", labelsize=9)
    sns.despine()
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    corr = day_f[["cnt", "temp_c", "hum_pct", "windspeed_kmh"]].corr()["cnt"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Korelasi dengan suhu", f"{corr['temp_c']:.2f}")
    c2.metric("Korelasi dengan kelembapan", f"{corr['hum_pct']:.2f}")
    c3.metric("Korelasi dengan kecepatan angin", f"{corr['windspeed_kmh']:.2f}")
    st.caption("Persentase pada grafik cuaca dihitung terhadap rata-rata hari Cerah pada data terfilter.")

# ----------------------------------------------------------------------
# Tab 3: Tren bulanan (Pertanyaan 3)
# ----------------------------------------------------------------------
with tab3:
    st.subheader("Bagaimana pertumbuhan penyewaan 2012 dibanding 2011?")
    pivot = day_f.pivot_table(
        index="month", columns="year", values=["cnt", "casual", "registered"], aggfunc="sum"
    )
    years_available = sorted(day_f["year"].unique())

    fig, ax = plt.subplots(figsize=(10, 4.5))
    palette = {2011: C_MUTED, 2012: C_PRIMARY}
    for y in years_available:
        s = pivot["cnt"][y].dropna()
        ax.plot(s.index, s.values, marker="o", lw=2.4, color=palette.get(y, C_PRIMARY), label=str(y))
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(MONTHS)
    ax.set_xlabel("Bulan")
    ax.set_ylabel("Total penyewaan")
    ax.set_title("Total penyewaan bulanan", loc="left", fontweight="bold")
    ax.legend(title="Tahun", frameon=False)
    sns.despine()
    st.pyplot(fig)
    plt.close(fig)

    if 2011 in years_available and 2012 in years_available:
        months_both = pivot["cnt"].dropna().index
        yoy = pd.DataFrame(
            {
                "Total": (pivot["cnt"][2012] / pivot["cnt"][2011] - 1) * 100,
                "Casual": (pivot["casual"][2012] / pivot["casual"][2011] - 1) * 100,
                "Registered": (pivot["registered"][2012] / pivot["registered"][2011] - 1) * 100,
            }
        ).loc[months_both]

        fig, ax = plt.subplots(figsize=(10, 4.2))
        x = np.arange(len(yoy))
        w = 0.38
        ax.bar(x - w / 2, yoy["Casual"], w, color=C_ACCENT, label="Casual")
        ax.bar(x + w / 2, yoy["Registered"], w, color=C_PRIMARY, label="Registered")
        ax.set_xticks(x)
        ax.set_xticklabels([MONTHS[m - 1] for m in yoy.index])
        ax.set_ylabel("Pertumbuhan YoY (%)")
        ax.set_title("Pertumbuhan YoY 2012 vs 2011 per tipe pengguna", loc="left", fontweight="bold")
        ax.legend(frameon=False)
        sns.despine()
        st.pyplot(fig)
        plt.close(fig)

        total_2011 = day_f.loc[day_f["year"] == 2011, "cnt"].sum()
        total_2012 = day_f.loc[day_f["year"] == 2012, "cnt"].sum()
        if total_2011 > 0:
            st.markdown(
                f"- Total penyewaan pada periode terfilter: **{fmt(total_2011)}** (2011) → "
                f"**{fmt(total_2012)}** (2012), tumbuh **{(total_2012 / total_2011 - 1) * 100:.1f}%**."
            )
        st.markdown(
            f"- Bulan pertumbuhan tertinggi: **{MONTHS[int(yoy['Total'].idxmax()) - 1]}** "
            f"({yoy['Total'].max():.1f}%); terendah: **{MONTHS[int(yoy['Total'].idxmin()) - 1]}** "
            f"({yoy['Total'].min():.1f}%)."
        )
        st.caption(
            "Pertumbuhan awal tahun terlihat sangat tinggi karena basis 2011 masih rendah "
            "(sistem baru berkembang). Bandingkan juga dengan bulan-bulan pertengahan tahun."
        )
    else:
        st.info("Perbandingan YoY membutuhkan data 2011 dan 2012. Perluas rentang tanggal pada filter.")

# ----------------------------------------------------------------------
# Tab 4: Analisis lanjutan (binning / manual grouping)
# ----------------------------------------------------------------------
with tab4:
    st.subheader("Binning suhu & heatmap hari × jam")
    day_adv = day_f.copy()
    day_adv["temp_group"] = pd.cut(
        day_adv["temp_c"], bins=[-np.inf, 10, 20, 30, np.inf], labels=TEMP_LABELS, right=False
    )
    by_temp = day_adv.groupby("temp_group", observed=True)["cnt"].agg(["mean", "count"])

    col_a, col_b = st.columns([1, 1.6])
    with col_a:
        fig, ax = plt.subplots(figsize=(5, 4.2))
        colors_t = [C_PRIMARY if v == by_temp["mean"].max() else C_MUTED for v in by_temp["mean"]]
        bars = ax.barh(by_temp.index.astype(str), by_temp["mean"], color=colors_t)
        ax.bar_label(
            bars,
            labels=[f"{fmt(m)}  (n={int(n)} hari)" for m, n in zip(by_temp["mean"], by_temp["count"])],
            padding=3,
            fontsize=8.5,
        )
        ax.invert_yaxis()
        ax.set_xlim(0, by_temp["mean"].max() * 1.45)
        ax.set_xlabel("Rata-rata penyewaan per hari")
        ax.set_title("Penyewaan menurut kelompok suhu", loc="left", fontweight="bold", fontsize=11)
        sns.despine()
        st.pyplot(fig)
        plt.close(fig)

    with col_b:
        heat = hour_f.pivot_table(
            index="weekday_name", columns="hr", values="cnt", aggfunc="mean", observed=False
        )
        fig, ax = plt.subplots(figsize=(8.5, 4.2))
        sns.heatmap(heat, cmap="YlGnBu", ax=ax, cbar_kws={"label": "Rata-rata penyewaan"})
        ax.set_xlabel("Jam")
        ax.set_ylabel("")
        ax.tick_params(axis="y", rotation=0)
        ax.set_title("Rata-rata penyewaan per jam menurut hari", loc="left", fontweight="bold", fontsize=11)
        st.pyplot(fig)
        plt.close(fig)

    st.caption("Kelompok suhu dibuat dengan teknik binning (pd.cut); heatmap menunjukkan intensitas permintaan.")

with st.expander("Lihat data (hasil filter)"):
    st.dataframe(day_f.head(200))

st.caption("Sumber data: Capital Bikeshare via Fanaee-T & Gama (2013). Dashboard dibuat dengan Streamlit.")
