import streamlit as st
import pandas as pd
from datetime import timedelta
import re

# ======================
# KONFIGURASI HALAMAN
# ======================
st.set_page_config(
    page_title="Estimasi Pengiriman",
    page_icon="📦",
    layout="wide"
)

# ======================
# BACA DATA
# ======================
df = pd.read_excel("rawdata.xlsx")

# ======================
# CSS
# ======================
st.markdown("""
<style>
h1 {
    color: #0E4C92;
}

/* Dropdown Soft Gold */
div[data-baseweb="select"] > div {
    background-color: #E6D3A3 !important;
    border-radius: 8px;
}

/* Area Tabel */
[data-testid="stDataFrame"] {
    background-color: #F5E6D3;
}
</style>
""", unsafe_allow_html=True)

# ======================
# HEADER + LOGO
# ======================
col1, col2 = st.columns([1, 5])

with col1:
    st.image("logo.jpeg", width=100)

with col2:
    st.title("Cek Estimasi Pengiriman")
    st.caption("Pilih kota tujuan dan tanggal kirim untuk melihat estimasi pengiriman")

# ======================
# DAFTAR KOTA
# ======================
kota_list = sorted(df["Nama_Kota"].dropna().unique())

# ======================
# INPUT KOTA
# ======================
kota_pilihan = st.selectbox(
    "Pilih Kota Tujuan",
    options=kota_list,
    index=None,
    placeholder="Ketik nama kota..."
)

# ======================
# INPUT TANGGAL KIRIM
# ======================
tanggal_kirim = st.date_input(
    "Masukan Tanggal Kirim"
)

# ======================
# CARD KOTA TUJUAN
# ======================
if kota_pilihan:
    st.markdown(f"""
    <div style="
        background-color:#F5E6D3;
        padding:15px;
        border-radius:10px;
        border-left:5px solid #C8A97E;
        margin-top:10px;
        margin-bottom:15px;
        font-size:18px;
        font-weight:bold;
        color:#4E342E;
    ">
        📍 Kota Tujuan : {kota_pilihan}
    </div>
    <div> 
         ⚠️ Data estimasi dapat berubah sewaktu-waktu sesuai pembaruan operasional   
    </div>
    """, unsafe_allow_html=True)

# ======================
# FUNGSI HITUNG TANGGAL TIBA
# ======================
def hitung_tanggal_tiba(estimasi, tanggal_kirim):
    try:
        angka = re.findall(r'\d+', str(estimasi))

        if len(angka) >= 2:
            min_hari = int(angka[0])
            max_hari = int(angka[1])

            tgl_awal = tanggal_kirim + timedelta(days=min_hari)
            tgl_akhir = tanggal_kirim + timedelta(days=max_hari)

            return f"{tgl_awal.strftime('%d %b %Y')} - {tgl_akhir.strftime('%d %b %Y')}"

    except:
        pass

    return "-"

# ======================
# TAMPILKAN HASIL
# ======================
if kota_pilihan:

    row = df[df["Nama_Kota"] == kota_pilihan].iloc[0]

    layanan = [
        "JNE-Reg",
        "Yes",
        "Sps",
        "JTR",
        "Bosspack",
        "Regpack",
        "Jagopack",
        "Bigpack"
    ]

    estimasi_list = [
        row["JNE-Reg"],
        row["Yes"],
        row["Sps"],
        row["JTR"],
        row["Bosspack"],
        row["Regpack"],
        row["Jagopack"],
        row["Bigpack"]
    ]

    perkiraan_tiba = [
        hitung_tanggal_tiba(est, tanggal_kirim)
        for est in estimasi_list
    ]

    hasil = pd.DataFrame({
        "Layanan": layanan,
        "Estimasi": estimasi_list,
        "Perkiraan Sampai": perkiraan_tiba
    })

    st.subheader(f"Estimasi ke {kota_pilihan}")

    styled_df = (
        hasil.style
        .set_table_styles([
            {
                "selector": "th",
                "props": [
                    ("background-color", "#C8A97E"),
                    ("color", "white"),
                    ("font-weight", "bold")
                ]
            }
        ])
        .set_properties(**{
            "background-color": "#F5E6D3",
            "color": "#4E342E"
        })
    )

    st.dataframe(
        styled_df,
        hide_index=True,
        use_container_width=True
    )

# ======================
# FOOTER
# ======================
st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown("""
<div style="
    background-color:#E6D3A3;
    padding:12px;
    border-radius:10px;
    text-align:center;
    color:#5D4037;
    font-size:14px;
">
    Estimasi Pengiriman Godeliva Gift <br>
    Data estimasi dapat berubah sewaktu-waktu sesuai pembaruan operasional. <br><br>
    Ruko Aniva Grande G1 No. 7, Gading Serpong, Banten, Medang, Kec. Pagedangan, Kabupaten Tangerang, Banten 15325 <br>
    Copyright © 2024 Godeliva Gift. All rights reserved.
</div>
""", unsafe_allow_html=True)
