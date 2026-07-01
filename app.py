import streamlit as st
import pandas as pd
from datetime import timedelta
import re
import time
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

# ======================
# KONFIGURASI HALAMAN
# ======================
st.set_page_config(
    page_title="Estimasi Pengiriman",
    page_icon="📦",
    layout="wide"
)

# ======================
# BACA DATA (4 SHEET)
# ======================
df_estimasi = pd.read_excel(
    "rawdata.xlsx",
    sheet_name="Estimasi"
)

df_harga = pd.read_excel(
    "rawdata.xlsx",
    sheet_name="Harga1kg"
)

df_cargo = pd.read_excel(
    "rawdata.xlsx",
    sheet_name="Cargo"
)

df_patokan = pd.read_excel(
    "rawdata.xlsx",
    sheet_name="Patokan_Kecamatan"
)

# ======================
# CSS
# ======================
st.markdown("""
<style>

h1{
    color:#0E4C92;
}

/* Dropdown */
div[data-baseweb="select"] > div{
    background-color:#E6D3A3 !important;
    border-radius:8px;
}

/* Number Input */
div[data-testid="stNumberInput"] input{
    background-color:#FFF8E8;
}

/* Date Input */
div[data-testid="stDateInput"] input{
    background-color:#FFF8E8;
}

/* Dataframe */
[data-testid="stDataFrame"]{
    background-color:#F5E6D3;
}

</style>
""", unsafe_allow_html=True)

# ======================
# HEADER
# ======================
col1, col2 = st.columns([1,5])

with col1:
    st.image("logo.jpeg", width=100)

with col2:
    st.title("Cek Estimasi Pengiriman")
    st.caption(
        "Pilih kota tujuan, tanggal kirim, dan berat kiriman untuk melihat estimasi serta tarif pengiriman."
    )

# ======================
# DAFTAR KOTA
# ======================
kota_list = sorted(
    df_estimasi["Nama_Kota"]
    .dropna()
    .unique()
)

# ======================
# INPUT
# ======================

col1, col2, col3 = st.columns(3)

with col1:

    kota_pilihan = st.selectbox(
        "Pilih Kota Tujuan",
        options=kota_list,
        index=None,
        placeholder="Ketik nama kota..."
    )

with col2:

    tanggal_kirim = st.date_input(
        "Masukkan Tanggal Kirim"
    )

with col3:

    berat = st.number_input(
        "Masukkan Berat (Kg)",
        min_value=1,
        value=1,
        step=1
    )

# ======================
# CARD KOTA TUJUAN
# ======================
if kota_pilihan:

    # Ambil data patokan kecamatan
    row_patokan = df_patokan[
        df_patokan["Nama_Kota"] == kota_pilihan
    ].iloc[0]

    lion_patokan = row_patokan["Lion Parcel"]
    jne_patokan = row_patokan["JNE"]

    st.markdown(f"""
    <div style="
        background-color:#F5E6D3;
        padding:15px;
        border-radius:10px;
        border-left:5px solid #C8A97E;
        margin-top:10px;
        margin-bottom:5px;
        font-size:18px;
        font-weight:bold;
        color:#4E342E;
    ">
        📍 Kota Tujuan : {kota_pilihan}
    </div>

    <div style="
        margin-left:8px;
        margin-bottom:15px;
        color:#6D4C41;
        font-size:13px;
        line-height:1.7;
    ">
        • Patokan Kecamatan Lion Parcel : <b>{lion_patokan}</b><br>
        • Patokan Kecamatan JNE : <b>{jne_patokan}</b>
    </div>

    """, unsafe_allow_html=True)

# ======================
# FORMAT RUPIAH
# ======================
def rupiah(angka):

    if pd.isna(angka):
        return "-"

    try:
        return "Rp{:,.0f}".format(float(angka)).replace(",", ".")
    except:
        return "-"

# ======================
# HITUNG TANGGAL TIBA
# ======================
def hitung_tanggal_tiba(estimasi, tanggal_kirim):

    try:

        angka = re.findall(r'\d+', str(estimasi))

        if len(angka) >= 2:

            min_hari = int(angka[0])
            max_hari = int(angka[1])

            awal = tanggal_kirim + timedelta(days=min_hari)
            akhir = tanggal_kirim + timedelta(days=max_hari)

            return f"{awal.strftime('%d %b %Y')} - {akhir.strftime('%d %b %Y')}"

        elif len(angka) == 1:

            hari = int(angka[0])

            tiba = tanggal_kirim + timedelta(days=hari)

            return tiba.strftime("%d %b %Y")

    except:
        pass

    return "-"

# ======================
# HITUNG TARIF REGULER
# ======================
def hitung_reguler(harga_perkg, berat):

    try:

        if pd.isna(harga_perkg):
            return "-", "-"

        harga_perkg = float(harga_perkg)

        total = harga_perkg * berat

        return (
            f"{rupiah(harga_perkg)}/Kg",
            rupiah(total)
        )

    except:
        return "-", "-"

# ======================
# HITUNG TARIF JTR
# ======================
def hitung_jtr(dasar, tambahan, berat):

    try:

        if pd.isna(dasar):
            return "-", "-"

        dasar = float(dasar)
        tambahan = float(tambahan)

        if berat <= 10:

            total = dasar

        else:

            total = dasar + ((berat - 10) * tambahan)

        tarif = (
            f"1-10 Kg : {rupiah(dasar)}\n"
            f",Berat >10 Kg : +{rupiah(tambahan)}/Kg"
        )
        return tarif, rupiah(total)

    except:
        return "-", "-"

# ======================
# HITUNG TARIF SPS
# ======================
def hitung_sps(dasar, tambahan, berat):

    try:

        if pd.isna(dasar):
            return "-", "-"

        dasar = float(dasar)
        tambahan = float(tambahan)

        if berat == 1:

            total = dasar

        else:

            total = dasar + ((berat - 1) * tambahan)

        tarif = (
            f"1 Kg : {rupiah(dasar)}"
            f",Berikutnya : +{rupiah(tambahan)}/Kg"
        )
        return tarif, rupiah(total)

    except:
        return "-", "-"
    
# ======================
# TAMPILKAN HASIL
# ======================
if kota_pilihan:

    with st.spinner("Memuat estimasi terbaru..."):
        time.sleep(0.7)

    st.success(f"✅ Data estimasi untuk {kota_pilihan} berhasil dimuat")

    # ======================
    # AMBIL DATA DARI SEMUA SHEET
    # ======================

    row_estimasi = df_estimasi[
        df_estimasi["Nama_Kota"] == kota_pilihan
    ].iloc[0]

    row_harga = df_harga[
        df_harga["Nama_Kota"] == kota_pilihan
    ].iloc[0]

    row_cargo = df_cargo[
        df_cargo["Nama_Kota"] == kota_pilihan
    ].iloc[0]

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

    estimasi = [
        row_estimasi["JNE-Reg"],
        row_estimasi["Yes"],
        row_estimasi["Sps"],
        row_estimasi["JTR"],
        row_estimasi["Bosspack"],
        row_estimasi["Regpack"],
        row_estimasi["Jagopack"],
        row_estimasi["Bigpack"]
    ]

    tanggal_tiba = [
        hitung_tanggal_tiba(x, tanggal_kirim)
        for x in estimasi
    ]

    tarif = []
    total = []

    # ======================
    # HITUNG SEMUA TARIF
    # ======================

    for layanan_item in layanan:

        # ----------------------
        # JTR
        # ----------------------
        if layanan_item == "JTR":

            t, h = hitung_jtr(
                row_cargo["JTR_Dasar"],
                row_cargo["JTR_Tambahan"],
                berat
            )

        # ----------------------
        # SPS
        # ----------------------
        elif layanan_item == "Sps":

            t, h = hitung_sps(
                row_cargo["Sps_Dasar"],
                row_cargo["Sps_Tambahan"],
                berat
            )

        # ----------------------
        # REGULER
        # ----------------------
        else:

            t, h = hitung_reguler(
                row_harga[layanan_item],
                berat
            )

        tarif.append(t)
        total.append(h)

    # ======================
    # JIKA ESTIMASI "-"
    # MAKA TARIF & TOTAL "-"
    # ======================

    for i in range(len(estimasi)):

        if (
            str(estimasi[i]).strip() == "-"
            or
            str(estimasi[i]).lower() == "nan"
        ):

            tarif[i] = "-"
            total[i] = "-"
            tanggal_tiba[i] = "-"

    # ======================
    # DATAFRAME
    # ======================

    hasil = pd.DataFrame({

        "Layanan": layanan,

        "Estimasi":
            estimasi,

        "Perkiraan Sampai":
            tanggal_tiba,

        "Tarif":
            tarif,

        "Total Harga":
            total

    })

    # ======================
    # STYLING TABEL
    # ======================

    st.subheader(f"Estimasi ke {kota_pilihan}")

    styled_df = (
        hasil.style

        .set_table_styles([

            {
                "selector": "th",
                "props": [
                    ("background-color", "#C8A97E"),
                    ("color", "white"),
                    ("font-weight", "bold"),
                    ("text-align", "center")
                ]
            }

        ])

        .set_properties(**{
            "background-color": "#F5E6D3",
            "color": "#4E342E",
            "text-align": "center"
        })

    )

    st.dataframe(
        styled_df,
        hide_index=True,
        use_container_width=True
    )


    # ======================
    # DISCLAIMER
    # ======================

    st.markdown("""
    <div style="
        margin-top:10px;
        text-align:left;
        color:#8D6E63;
        font-size:13px;
        font-style:italic;
    ">
    ⚠️ Data estimasi hari dan harga yang ditampilkan tidak spesifik ke kecamatan tertentu melainkan ke perwakilan kecamatan di tengah kota yang dipilih.
    </div>
    """, unsafe_allow_html=True)

    # ======================
    # INFORMASI TARIF
    # ======================

    with st.expander("📖 Penjelasan Perhitungan Tarif"):

        st.markdown("""

**JNE REG / YES / Bosspack / Regpack / Jagopack / Bigpack**

> Total Harga = Tarif per Kg × Berat Kiriman

---

**JTR (Cargo)**

- Berat **1 - 10 Kg** menggunakan **Tarif Dasar**
- Berat **>10 Kg** akan dikenakan tambahan tarif **setiap kenaikan 1 Kg**

Contoh:

> Tarif Dasar = Rp120.000

> Tambahan = Rp12.000/Kg

- 8 Kg = Rp120.000
- 10 Kg = Rp120.000
- 11 Kg = Rp132.000
- 12 Kg = Rp144.000

---

**SPS**

- Harga pada kolom **SPS Dasar** berlaku untuk **1 Kg pertama**
- Berat berikutnya akan ditambah sesuai **SPS Tambahan**

Contoh:

> SPS Dasar = Rp25.000

> SPS Tambahan = Rp20.000/Kg

- 1 Kg = Rp25.000
- 2 Kg = Rp45.000
- 3 Kg = Rp65.000

""")

# ======================
# DOWNLOAD PDF
# ======================

    st.markdown("""
    <div style="
        margin-top:10px;
        text-align:left;
        color:#8D6E63;
        font-size:13px;
        font-style:italic;
    ">
    Klik tombol di bawah untuk mengunduh ringkasan estimasi pengiriman dalam format PDF.
    </div>
    """, unsafe_allow_html=True)

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    story = []

    story.append(Paragraph("<b>Godeliva Gift Serpong</b>", styles["Title"]))
    story.append(Paragraph("<b>Estimasi Harga dan Pengiriman</b>", styles["Title"]))
    story.append(Paragraph("<br/>", styles["Normal"]))
    story.append(Paragraph("=========================================================", styles["Title"]))

    story.append(Paragraph(f"<b>Kota Tujuan :</b> {kota_pilihan}", styles["Normal"]))
    story.append(Paragraph(f"<b>Tanggal Kirim :</b> {tanggal_kirim.strftime('%d-%m-%Y')}", styles["Normal"]))
    story.append(Paragraph(f"<b>Berat :</b> {berat} Kg", styles["Normal"]))
    story.append(Paragraph("=========================================================", styles["Normal"]))
    story.append(Paragraph("<br/>", styles["Normal"]))

    for _, row in hasil.iterrows():

        story.append(
            Paragraph(
                f"""
    <b>{row['Layanan']}</b><br/>
    Estimasi : {row['Estimasi']}<br/>
    Perkiraan Sampai : {row['Perkiraan Sampai']}<br/>
    Tarif : {row['Tarif']}<br/>
    <b>Total Harga :</b> {row['Total Harga']}
    <br/><br/>
    """,
                styles["BodyText"]
            )
        )

    doc.build(story)

    pdf = buffer.getvalue()

    buffer.close()

    st.download_button(
        "📄 Download Ringkasan PDF",
        data=pdf,
        file_name=f"Estimasi_{kota_pilihan}.pdf",
        mime="application/pdf",
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
    Ruko Aniva Grande G1 No. 7,
    Gading Serpong, Banten,
    Medang, Kec. Pagedangan,
    Kabupaten Tangerang,
    Banten 15325
    <br><br>
    Copyright © 2026
    Godeliva Gift.
    All rights reserved.
</div>
""", unsafe_allow_html=True)
