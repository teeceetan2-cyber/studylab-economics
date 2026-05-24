import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from math import ceil

st.set_page_config(page_title="StudyLab — Economics", page_icon="📊", layout="wide")

# ─── Styling ───
st.markdown("""
<style>
    .stApp { background: #0f1117; color: #e0e0e0; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    h1, h2, h3 { color: #f0f0f0; }
    .stSelectbox label, .stNumberInput label, .stSlider label { color: #ccc; }
    .result-card {
        background: linear-gradient(135deg, #1a1d2a, #252840);
        border: 1px solid #3a3f5c;
        border-radius: 12px; padding: 20px; margin: 16px 0;
    }
    .result-card h4 { color: #7c8cf0; margin-top: 0; }
    .result-value { font-size: 1.8em; font-weight: bold; color: #5ceb9a; }
    .result-label { color: #999; font-size: 0.9em; }
    .sub-result { font-size: 1.2em; color: #bbb; }
    .tax-bracket-bar { height: 6px; border-radius: 3px; margin: 4px 0; }
    .disclaimer {
        background: #2a1f1f; border-left: 4px solid #f0ad4e;
        padding: 10px 16px; border-radius: 6px; font-size: 0.85em; color: #ddd;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ─── Constants ───
PTKP_TABLE = {
    "TK/0": 54_000_000, "TK/1": 58_500_000, "TK/2": 63_000_000, "TK/3": 67_500_000,
    "K/0": 58_500_000,  "K/1": 63_000_000,  "K/2": 67_500_000,  "K/3": 72_000_000,
    "K/I/0": 58_500_000, "K/I/1": 63_000_000, "K/I/2": 67_500_000, "K/I/3": 72_000_000,
}

PROGRESSIVE_TAX = [
    (0, 60_000_000, 0.05),
    (60_000_000, 250_000_000, 0.15),
    (250_000_000, 500_000_000, 0.25),
    (500_000_000, 5_000_000_000, 0.30),
    (5_000_000_000, float('inf'), 0.35),
]

# TER Categories based on PTKP status (PMK 168/2023)
TER_CATEGORY = {
    "TK/0": "A", "TK/1": "A", "TK/2": "B", "TK/3": "B",
    "K/0": "A", "K/1": "B", "K/2": "B", "K/3": "C",
    "K/I/0": "A", "K/I/1": "B", "K/I/2": "C", "K/I/3": "C",
}

# TER Monthly Rates (percentage) by category & gross income bracket (monthly)
TER_A = [
    (0, 5_400_000, 0.0),
    (5_400_000, 5_650_000, 0.25),
    (5_650_000, 5_950_000, 0.50),
    (5_950_000, 6_300_000, 0.75),
    (6_300_000, 6_750_000, 1.0),
    (6_750_000, 7_100_000, 1.25),
    (7_100_000, 7_500_000, 1.50),
    (7_500_000, 7_950_000, 1.75),
    (7_950_000, 8_450_000, 2.0),
    (8_450_000, 9_050_000, 2.25),
    (9_050_000, 9_700_000, 2.50),
    (9_700_000, 10_500_000, 3.0),
    (10_500_000, 11_300_000, 3.5),
    (11_300_000, 12_500_000, 4.0),
    (12_500_000, 13_700_000, 5.0),
    (13_700_000, 15_100_000, 6.0),
    (15_100_000, 16_900_000, 7.0),
    (16_900_000, 19_500_000, 8.0),
    (19_500_000, 22_100_000, 9.0),
    (22_100_000, 25_100_000, 10.0),
    (25_100_000, 28_800_000, 11.0),
    (28_800_000, 34_200_000, 12.0),
    (34_200_000, 40_100_000, 13.0),
    (40_100_000, 47_000_000, 14.0),
    (47_000_000, 54_100_000, 15.0),
    (54_100_000, 62_500_000, 16.0),
    (62_500_000, 71_100_000, 17.0),
    (71_100_000, 80_900_000, 18.0),
    (80_900_000, 91_800_000, 19.0),
    (91_800_000, 105_000_000, 20.0),
    (105_000_000, 122_500_000, 22.0),
    (122_500_000, 147_000_000, 25.0),
    (147_000_000, 187_500_000, 30.0),
    (187_500_000, 250_500_000, 35.0),
    (250_500_000, float('inf'), 40.0),
]

TER_B = [
    (0, 6_200_000, 0.0),
    (6_200_000, 6_500_000, 0.25),
    (6_500_000, 6_850_000, 0.50),
    (6_850_000, 7_300_000, 0.75),
    (7_300_000, 7_750_000, 1.0),
    (7_750_000, 8_200_000, 1.25),
    (8_200_000, 8_800_000, 1.50),
    (8_800_000, 9_400_000, 1.75),
    (9_400_000, 10_000_000, 2.0),
    (10_000_000, 10_700_000, 2.25),
    (10_700_000, 11_400_000, 2.50),
    (11_400_000, 12_200_000, 3.0),
    (12_200_000, 13_100_000, 3.5),
    (13_100_000, 14_200_000, 4.0),
    (14_200_000, 15_500_000, 5.0),
    (15_500_000, 16_900_000, 6.0),
    (16_900_000, 18_700_000, 7.0),
    (18_700_000, 21_200_000, 8.0),
    (21_200_000, 23_700_000, 9.0),
    (23_700_000, 26_600_000, 10.0),
    (26_600_000, 30_000_000, 11.0),
    (30_000_000, 35_000_000, 12.0),
    (35_000_000, 41_000_000, 13.0),
    (41_000_000, 47_900_000, 14.0),
    (47_900_000, 55_900_000, 15.0),
    (55_900_000, 65_700_000, 16.0),
    (65_700_000, 76_700_000, 17.0),
    (76_700_000, 89_100_000, 18.0),
    (89_100_000, 103_000_000, 19.0),
    (103_000_000, 121_000_000, 20.0),
    (121_000_000, 143_500_000, 22.0),
    (143_500_000, 178_500_000, 25.0),
    (178_500_000, 233_500_000, 30.0),
    (233_500_000, 320_000_000, 35.0),
    (320_000_000, float('inf'), 40.0),
]

TER_C = [
    (0, 7_700_000, 0.0),
    (7_700_000, 8_600_000, 0.25),
    (8_600_000, 9_400_000, 0.50),
    (9_400_000, 10_300_000, 0.75),
    (10_300_000, 11_300_000, 1.0),
    (11_300_000, 12_300_000, 1.25),
    (12_300_000, 13_300_000, 1.50),
    (13_300_000, 14_500_000, 1.75),
    (14_500_000, 15_800_000, 2.0),
    (15_800_000, 17_200_000, 2.25),
    (17_200_000, 19_000_000, 2.50),
    (19_000_000, 21_400_000, 3.0),
    (21_400_000, 24_000_000, 3.5),
    (24_000_000, 27_000_000, 4.0),
    (27_000_000, 30_600_000, 5.0),
    (30_600_000, 35_000_000, 6.0),
    (35_000_000, 40_000_000, 7.0),
    (40_000_000, 46_500_000, 8.0),
    (46_500_000, 54_000_000, 9.0),
    (54_000_000, 63_000_000, 10.0),
    (63_000_000, 73_500_000, 11.0),
    (73_500_000, 87_000_000, 12.0),
    (87_000_000, 105_000_000, 13.0),
    (105_000_000, 127_000_000, 14.0),
    (127_000_000, 155_000_000, 15.0),
    (155_000_000, 190_000_000, 16.0),
    (190_000_000, 233_000_000, 17.0),
    (233_000_000, 287_000_000, 18.0),
    (287_000_000, 356_000_000, 19.0),
    (356_000_000, 447_000_000, 20.0),
    (447_000_000, 569_000_000, 22.0),
    (569_000_000, 745_000_000, 25.0),
    (745_000_000, 1_040_000_000, 30.0),
    (1_040_000_000, 1_460_000_000, 35.0),
    (1_460_000_000, float('inf'), 40.0),
]

TER_MAP = {"A": TER_A, "B": TER_B, "C": TER_C}

BPJS_KES_PERSEN = 0.05  # 5% total (4% employer + 1% employee)
BPJS_TK_PERSEN = {
    "JKK": 0.0024, "JKM": 0.003, "JP": 0.02, "JHT": 0.057,
}

# ─── Helper Functions ───

def fmt_idr(val):
    if abs(val) >= 1_000_000_000:
        return f"Rp {val/1e9:.2f} M"
    elif abs(val) >= 1_000_000:
        return f"Rp {val/1e6:.2f} jt"
    else:
        return f"Rp {val:,.0f}"

def calc_progressive_tax(pkp):
    tax = 0
    breakdown = []
    for low, high, rate in PROGRESSIVE_TAX:
        if pkp <= low:
            break
        taxable = min(pkp, high) - low
        layer = taxable * rate
        tax += layer
        breakdown.append((low, high, taxable, rate, layer))
    return tax, breakdown

def get_ter_rate(category, gross_monthly):
    table = TER_MAP.get(category, TER_C)
    for low, high, rate in table:
        if low <= gross_monthly < high:
            return rate / 100
    return 0

def calc_pph21_ter(gross_monthly, ptkp_status):
    category = TER_CATEGORY.get(ptkp_status, "C")
    ter_rate = get_ter_rate(category, gross_monthly)
    pph_monthly = gross_monthly * ter_rate
    pph_yearly = pph_monthly * 12
    return pph_monthly, pph_yearly, category, ter_rate

def calc_pph21_annual(gross_yearly, ptkp_status):
    ptkp = PTKP_TABLE.get(ptkp_status, 54_000_000)
    biaya_jabatan = min(gross_yearly * 0.05, 6_000_000)
    netto = gross_yearly - biaya_jabatan
    pkp = max(0, netto - ptkp)
    tax, breakdown = calc_progressive_tax(pkp)
    return tax, pkp, ptkp, biaya_jabatan, breakdown

def idr_input(label, min_val=0, max_val=1_000_000_000_000, step=100000, value=0, help_text="", **kwargs):
    return st.number_input(label, min_value=min_val, max_value=max_val, step=step, value=value, format="%d", help=help_text, **kwargs)


# ─── Navigation ───

CATEGORIES = {
    "Perpajakan Indonesia": ["PPh 21 (TER)", "PPh 21 Tahunan", "PPN (VAT)", "PPh Final", "PPh Badan", "PBB", "Take Home Pay"],
    "Ekonomi Makro & Mikro": ["GDP Calculator", "Inflasi Kalkulator", "Break-Even Point", "Elastisitas Permintaan", "Depresiasi Aset", "Bunga Majemuk"],
    "Basic Accounting": ["📋 Accounting Dashboard", "📐 Accounting Equation"],
}

def sidebar_nav():
    with st.sidebar:
        st.markdown("# 📊 StudyLab")
        st.markdown("### Economics")
        st.divider()
        cats = list(CATEGORIES.keys())
        sel_cat = st.selectbox("Kategori", cats, label_visibility="collapsed")
        sel_topic = st.radio("Topik", CATEGORIES[sel_cat], label_visibility="collapsed")
        st.divider()
        st.markdown("<small style='color:#666'>Data pajak berdasarkan PMK 168/2023 & PP 58/2023</small>", unsafe_allow_html=True)
        st.markdown("<small style='color:#555'>⚠️ Bukan saran resmi, hanya alat bantu belajar</small>", unsafe_allow_html=True)
        return sel_cat, sel_topic


# ═══════════════════════════════════════════════════════════════
#  PAGE RENDERERS
# ═══════════════════════════════════════════════════════════════

def render_pph21_ter():
    st.header("🧾 PPh 21 — Tarif Efektif Rata-rata (TER)")
    st.markdown("Berdasarkan **PP 58/2023** & **PMK 168/2023**. Gunakan untuk hitung potongan PPh 21 **bulanan**.")

    col1, col2 = st.columns(2)
    with col1:
        gross = idr_input("Gaji Bruto per Bulan (Rp)", min_val=0, value=5_000_000, step=500_000,
                          help_text="Gaji pokok + tunjangan tetap sebelum potongan")
    with col2:
        ptkp_status = st.selectbox("Status PTKP", list(PTKP_TABLE.keys()), index=0,
                                   help="Status kawin + tanggungan (K/1 = kawin 1 anak, TK/0 = tidak kawin 0 tanggungan, dll)")

    if gross > 0:
        pph_m, pph_y, cat, ter_rate = calc_pph21_ter(gross, ptkp_status)

        st.markdown(f"**Kategori TER:** {cat}")

        # TER Rate indicator
        ter_pct = ter_rate * 100
        st.markdown(f"**Tarif Efektif:** {ter_pct:.2f}% dari gaji bruto")

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown(f"""<div class="result-card"><h4>PPh 21 Bulanan</h4><div class="result-value">{fmt_idr(pph_m)}</div><div class="result-label">per bulan</div></div>""", unsafe_allow_html=True)
        with col_b:
            st.markdown(f"""<div class="result-card"><h4>PPh 21 Tahunan</h4><div class="result-value">{fmt_idr(pph_y)}</div><div class="result-label">estimasi 12 bulan</div></div>""", unsafe_allow_html=True)
        with col_c:
            net = gross - pph_m
            st.markdown(f"""<div class="result-card"><h4>Take Home Pay</h4><div class="result-value">{fmt_idr(net)}</div><div class="result-label">gaji bersih/bulan (sebelum BPJS)</div></div>""", unsafe_allow_html=True)

        # Visual: Gaji vs Pajak
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Take Home Pay", y=["Bulanan"], x=[net], orientation='h',
                             marker_color='#5ceb9a', text=f"Rp {net:,.0f}", textposition='inside'))
        fig.add_trace(go.Bar(name="PPh 21", y=["Bulanan"], x=[pph_m], orientation='h',
                             marker_color='#ff6b6b', text=f"Rp {pph_m:,.0f}", textposition='inside'))
        fig.update_layout(height=200, barmode='stack', showlegend=True,
                          plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                          font_color='#ccc', xaxis_title="Rupiah", margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("Masukkan gaji bruto untuk memulai perhitungan.")

    st.markdown("""<div class="disclaimer">⚠️ Kalkulator ini menggunakan Tarif Efektif Rata-rata (TER) per PMK 168/2023. 
    Untuk akurasi sempurna, konsultasikan dengan konsultan pajak atau gunakan e-Filing DJP.</div>""", unsafe_allow_html=True)


def render_pph21_annual():
    st.header("🧾 PPh 21 — Hitung Tahunan (Progresif)")
    st.markdown("Metode **tarif progresif Pasal 17** — cocok untuk perhitungan tahunan / SPT Tahunan.")

    col1, col2 = st.columns(2)
    with col1:
        gross_y = idr_input("Penghasilan Bruto Setahun (Rp)", min_val=0, value=120_000_000, step=1_000_000)
    with col2:
        ptkp_status = st.selectbox("Status PTKP", list(PTKP_TABLE.keys()), index=0, key="ptkp_annual")

    if gross_y > 0:
        tax, pkp, ptkp, biaya_jabatan, breakdown = calc_pph21_annual(gross_y, ptkp_status)

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown(f"""<div class="result-card"><h4>PKP</h4><div class="result-value">{fmt_idr(pkp)}</div><div class="result-label">Penghasilan Kena Pajak</div></div>""", unsafe_allow_html=True)
        with col_b:
            st.markdown(f"""<div class="result-card"><h4>PPh 21 Setahun</h4><div class="result-value">{fmt_idr(tax)}</div><div class="result-label">Pajak terutang</div></div>""", unsafe_allow_html=True)
        with col_c:
            st.markdown(f"""<div class="result-card"><h4>Biaya Jabatan</h4><div class="result-value">{fmt_idr(biaya_jabatan)}</div><div class="result-label">maks Rp 6jt/tahun</div></div>""", unsafe_allow_html=True)

        st.markdown(f"**PTKP:** {fmt_idr(ptkp)} ({ptkp_status})")

        # Tax breakdown table
        rows = []
        for low, high, taxable, rate, layer in breakdown:
            high_display = "∞" if high == float('inf') else fmt_idr(high)
            rows.append({
                "Lapisan": f"{fmt_idr(low)} - {high_display}",
                "PKP Kena Pajak": fmt_idr(taxable),
                "Tarif": f"{rate*100:.0f}%",
                "PPh": fmt_idr(layer),
            })
        st.markdown("**Detail Tarif Progresif:**")
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

        # Donut chart
        fig = go.Figure(data=[go.Pie(
            labels=["Take Home Pay", "PPh 21"],
            values=[gross_y - tax, tax],
            marker_colors=['#5ceb9a', '#ff6b6b'],
            textinfo='label+percent',
            hole=0.4
        )])
        fig.update_layout(height=350, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#ccc')
        st.plotly_chart(fig, width="stretch")


def render_ppn():
    st.header("🧾 PPN — Pajak Pertambahan Nilai")
    st.markdown("Hitung PPN terutang atas barang / jasa kena pajak.")

    col1, col2, col3 = st.columns(3)
    with col1:
        dpp = idr_input("Dasar Pengenaan Pajak (DPP) Rp", min_val=0, value=10_000_000, step=1_000_000,
                        help_text="Nilai sebelum PPN (harga barang/jasa)")
    with col2:
        ppn_rate = st.select_slider("Tarif PPN", options=[11, 12], value=11,
                                    help="PPN 11% (kebanyakan BKP/JKP) atau 12% (barang mewah tertentu)")
    with col3:
        ppn_rate_display = ppn_rate / 100
        jumlah_ppn = dpp * ppn_rate_display
        total = dpp + jumlah_ppn
        st.metric("PPN Terutang", fmt_idr(jumlah_ppn))
        st.metric("Total Termasuk PPN", fmt_idr(total))

    if dpp > 0:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"""<div class="result-card"><h4>DPP (Harga)</h4><div class="result-value">{fmt_idr(dpp)}</div><div class="result-label">Nilai barang/jasa</div></div>""", unsafe_allow_html=True)
        with col_b:
            st.markdown(f"""<div class="result-card"><h4>Total + PPN</h4><div class="result-value">{fmt_idr(total)}</div><div class="result-label">Termasuk PPN {ppn_rate}%</div></div>""", unsafe_allow_html=True)

        # Waterfall chart
        fig = go.Figure(go.Waterfall(
            name="PPN",
            orientation="v",
            measure=["relative", "total"],
            x=["DPP", f"Total + PPN {ppn_rate}%"],
            y=[dpp, jumlah_ppn],
            text=[fmt_idr(dpp), fmt_idr(jumlah_ppn)],
            connector={"line": {"color": "#666"}},
            decreasing={"marker": {"color": "#ff6b6b"}},
            increasing={"marker": {"color": "#5ceb9a"}},
        ))
        fig.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#ccc')
        st.plotly_chart(fig, width="stretch")

        # Reverse calculation
        st.divider()
        st.subheader("🔄 Hitung DPP dari Total Termasuk PPN")
        total_inc = idr_input("Total (sudah termasuk PPN) Rp", min_val=0, value=11_100_000, step=1_000_000, key="ppn_reverse")
        if total_inc > 0:
            dpp_reverse = total_inc / (1 + ppn_rate_display)
            ppn_reverse = total_inc - dpp_reverse
            col_r1, col_r2 = st.columns(2)
            col_r1.metric("DPP", fmt_idr(dpp_reverse))
            col_r2.metric("PPN", fmt_idr(ppn_reverse))


def render_pph_final():
    st.header("🧾 PPh Final — Pajak Penghasilan Final")
    st.markdown("PPh Final atas penghasilan tertentu (sewa, konstruksi, pengalihan tanah).")

    jenis = st.selectbox("Jenis Penghasilan", [
        "Sewa Tanah/Bangunan",
        "Jasa Konstruksi — Kecil (<= 4.5M)",
        "Jasa Konstruksi — Besar (> 4.5M, tanpa kualifikasi)",
        "Jasa Konstruksi — Besar (dengan kualifikasi)",
        "Pengalihan Hak Tanah/Bangunan",
        "UMKM (Peredaran Bruto ≤ 4.8M)",
    ])

    rates = {
        "Sewa Tanah/Bangunan": 0.10,
        "Jasa Konstruksi — Kecil (<= 4.5M)": 0.02,
        "Jasa Konstruksi — Besar (> 4.5M, tanpa kualifikasi)": 0.04,
        "Jasa Konstruksi — Besar (dengan kualifikasi)": 0.06,
        "Pengalihan Hak Tanah/Bangunan": 0.025,
        "UMKM (Peredaran Bruto ≤ 4.8M)": 0.005,
    }
    rate = rates[jenis]

    penghasilan = idr_input("Nilai Bruto / Peredaran Bruto (Rp)", min_val=0, value=100_000_000, step=10_000_000)
    if penghasilan > 0:
        pph = penghasilan * rate
        st.markdown(f"""<div class="result-card">
            <h4>PPh Final Terutang</h4>
            <div class="result-value">{fmt_idr(pph)}</div>
            <div class="result-label">Tarif {rate*100:.1f}% × {fmt_idr(penghasilan)}</div>
        </div>""", unsafe_allow_html=True)

        fig = go.Figure(data=[go.Pie(
            labels=["Penghasilan Bersih", "PPh Final"],
            values=[penghasilan - pph, pph],
            marker_colors=['#5ceb9a', '#ff6b6b'],
            textinfo='label+percent',
            hole=0.4
        )])
        fig.update_layout(height=300, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#ccc')
        st.plotly_chart(fig, width="stretch")


def render_pph_badan():
    st.header("🏢 PPh Badan — Pajak Penghasilan Wajib Pajak Badan")
    st.markdown("Hitung PPh terutang untuk badan usaha berdasarkan omzet.")

    jenis_wp = st.radio("Jenis Wajib Pajak Badan",
        ["UMKM (peredaran bruto ≤ Rp 4,8 M)", "Non-UMKM (peredaran bruto > Rp 4,8 M)"],
        horizontal=True)

    col1, col2 = st.columns(2)
    with col1:
        omzet = idr_input("Peredaran Bruto Setahun (Rp)", min_val=0, value=5_000_000_000, step=500_000_000)
    with col2:
        if "Non-UMKM" in jenis_wp:
            biaya = idr_input("Biaya/Beban Fiskal Setahun (Rp)", min_val=0, value=3_000_000_000, step=500_000_000,
                              help_text="Biaya yang dapat dikurangkan secara fiskal")

    if omzet > 0:
        if "UMKM" in jenis_wp:
            tarif = 0.005
            pkp_label = "Peredaran Bruto"
            pkp_val = omzet
        else:
            tarif = 0.22
            pkp_val = max(0, omzet - biaya)
            pkp_label = "Penghasilan Kena Pajak"

        pph = pkp_val * tarif

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown(f"""<div class="result-card"><h4>PKP</h4><div class="result-value">{fmt_idr(pkp_val)}</div><div class="result-label">{pkp_label}</div></div>""", unsafe_allow_html=True)
        with col_b:
            st.markdown(f"""<div class="result-card"><h4>PPh Badan</h4><div class="result-value">{fmt_idr(pph)}</div><div class="result-label">Tarif {tarif*100:.1f}%</div></div>""", unsafe_allow_html=True)
        with col_c:
            st.markdown(f"""<div class="result-card"><h4>Laba Bersih</h4><div class="result-value">{fmt_idr(pkp_val - pph)}</div><div class="result-label">Setelah Pajak</div></div>""", unsafe_allow_html=True)

        st.markdown(f"**Tarif Efektif:** {tarif*100:.1f}%")

        # Tax rate comparison
        if "Non-UMKM" in jenis_wp:
            st.divider()
            st.subheader("📊 Perbandingan Tarif")
            tax_comparison = pd.DataFrame({
                "Skema": ["Non-UMKM (22%)", "UMKM (0.5%)"],
                "PPh Terutang": [fmt_idr(pkp_val * 0.22), fmt_idr(omzet * 0.005)],
            })
            st.dataframe(tax_comparison, width="stretch", hide_index=True)
            st.caption("Perbandingan dengan skenario seandainya WP Badan memenuhi syarat UMKM untuk omzet yang sama.")


def render_pbb():
    st.header("🏠 PBB — Pajak Bumi dan Bangunan")
    st.markdown("Hitung PBB terutang atas tanah dan/atau bangunan.")

    col1, col2 = st.columns(2)
    with col1:
        njop_tanah = idr_input("NJOP Tanah (Rp)", min_val=0, value=500_000_000, step=50_000_000)
        njop_bangunan = idr_input("NJOP Bangunan (Rp)", min_val=0, value=200_000_000, step=50_000_000)
    with col2:
        njoptkp = idr_input("NJOPTKP (Rp)", min_val=0, value=12_000_000, step=1_000_000,
                            help_text="Nilai Jual Objek Pajak Tidak Kena Pajak (umumnya Rp 12jt untuk 1 WP per tahun)")
        st.info("NJOPTKP umumnya Rp 12.000.000 per WP per tahun untuk objek di satu Kab/Kota.")

    if njop_tanah + njop_bangunan > 0:
        total_njop = njop_tanah + njop_bangunan
        njop_tkp = max(0, total_njop - njoptkp)
        njkp_rate = 0.40 if njop_tkp >= 1_000_000_000 else 0.20  # NJKP: 40% untuk > 1M, 20% untuk ≤ 1M
        njkp = njop_tkp * njkp_rate
        pbb = njkp * 0.005  # 0.5%

        st.markdown(f"""<div class="result-card">
            <h4>PBB Terutang</h4>
            <div class="result-value">{fmt_idr(pbb)}</div>
            <div class="result-label">per tahun</div>
        </div>""", unsafe_allow_html=True)

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Total NJOP", fmt_idr(total_njop))
        with col_b:
            st.metric("NJOP - NJOPTKP", fmt_idr(njop_tkp))
        with col_c:
            st.metric("NJKP (tarif {:.0f}%)".format(njkp_rate*100), fmt_idr(njkp))

        # Bar chart
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Nilai", x=["NJOP Tanah", "NJOP Bangunan", "Total NJOP", "PBB Terutang"],
                             y=[njop_tanah, njop_bangunan, total_njop, pbb],
                             marker_color=['#5ceb9a', '#7c8cf0', '#f0ad4e', '#ff6b6b']))
        fig.update_layout(height=350, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                          font_color='#ccc', yaxis_title="Rupiah", margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, width="stretch")


def render_take_home_pay():
    st.header("💰 Take Home Pay Simulator")
    st.markdown("Simulasi **gaji bersih** setelah potongan PPh 21, BPJS Kesehatan & BPJS Ketenagakerjaan.")

    col1, col2 = st.columns(2)
    with col1:
        gross = idr_input("Gaji Bruto per Bulan (Rp)", min_val=0, value=8_000_000, step=500_000,
                          help_text="Gaji pokok + tunjangan tetap")
    with col2:
        ptkp_status = st.selectbox("Status PTKP", list(PTKP_TABLE.keys()), index=2, key="thp_ptkp")

    with col1:
        ikut_bpjs_kes = st.checkbox("Ikut BPJS Kesehatan", value=True,
                                     help="Potongan 1% dari gaji (4% ditanggung perusahaan)")
    with col2:
        ikut_bpjs_tk = st.checkbox("Ikut BPJS Ketenagakerjaan", value=True)

    if gross > 0:
        # PPh 21 via TER
        pph_m, _, cat, ter_rate = calc_pph21_ter(gross, ptkp_status)

        # BPJS Kesehatan (1% karyawan)
        bpjs_kes = gross * 0.01 if ikut_bpjs_kes else 0
        bpjs_kes_perusahaan = gross * 0.04 if ikut_bpjs_kes else 0

        # BPJS Ketenagakerjaan (JHT 2% karyawan, JP 1% karyawan)
        bpjs_tk_karyawan = 0
        bpjs_tk_perusahaan = 0
        if ikut_bpjs_tk:
            bpjs_tk_karyawan = gross * 0.02  # JHT
            bpjs_tk_karyawan += gross * 0.01  # JP
            bpjs_tk_perusahaan = gross * 0.0024  # JKK
            bpjs_tk_perusahaan += gross * 0.003   # JKM
            bpjs_tk_perusahaan += gross * 0.037   # JHT perusahaan
            bpjs_tk_perusahaan += gross * 0.01    # JP perusahaan

        total_potongan = pph_m + bpjs_kes + bpjs_tk_karyawan
        thp = gross - total_potongan

        st.divider()

        # Results
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown(f"""<div class="result-card"><h4>Gaji Bruto</h4><div class="result-value">{fmt_idr(gross)}</div><div class="result-label">per bulan</div></div>""", unsafe_allow_html=True)
        with col_b:
            st.markdown(f"""<div class="result-card"><h4>Total Potongan</h4><div class="result-value" style="color:#ff6b6b">{fmt_idr(total_potongan)}</div><div class="result-label">{total_potongan/gross*100:.1f}% dari gaji</div></div>""", unsafe_allow_html=True)
        with col_c:
            st.markdown(f"""<div class="result-card"><h4>Take Home Pay 💵</h4><div class="result-value">{fmt_idr(thp)}</div><div class="result-label">gaji bersih diterima</div></div>""", unsafe_allow_html=True)

        # Potongan details
        st.subheader("📋 Rincian Potongan")
        pot_rows = [
            {"Potongan": "PPh 21 (TER)", "Karyawan": fmt_idr(pph_m), "Perusahaan": "-", "Total": fmt_idr(pph_m)},
        ]
        if ikut_bpjs_kes:
            pot_rows.append({"Potongan": "BPJS Kesehatan", "Karyawan": fmt_idr(bpjs_kes), "Perusahaan": fmt_idr(bpjs_kes_perusahaan), "Total": fmt_idr(bpjs_kes + bpjs_kes_perusahaan)})
        if ikut_bpjs_tk:
            pot_rows.append({"Potongan": "BPJS TK (JHT+JP)", "Karyawan": fmt_idr(bpjs_tk_karyawan), "Perusahaan": fmt_idr(bpjs_tk_perusahaan), "Total": fmt_idr(bpjs_tk_karyawan + bpjs_tk_perusahaan)})
        pot_rows.append({"Potongan": "**TOTAL**", "Karyawan": f"**{fmt_idr(total_potongan)}**", "Perusahaan": f"**{fmt_idr(bpjs_kes_perusahaan + bpjs_tk_perusahaan)}**", "Total": f"**{fmt_idr(total_potongan + bpjs_kes_perusahaan + bpjs_tk_perusahaan)}**"})

        st.dataframe(pd.DataFrame(pot_rows), width="stretch", hide_index=True)

        # Waterfall chart
        fig = go.Figure(go.Waterfall(
            name="Take Home Pay",
            orientation="v",
            measure=["relative", "relative", "relative", "total"],
            x=["Gaji Bruto", "PPh 21", "BPJS", "Take Home Pay"],
            y=[gross, -pph_m, -(bpjs_kes + bpjs_tk_karyawan), 0],
            text=[fmt_idr(gross), fmt_idr(pph_m), fmt_idr(bpjs_kes + bpjs_tk_karyawan), fmt_idr(thp)],
            connector={"line": {"color": "#666", "width": 2}},
            decreasing={"marker": {"color": "#ff6b6b"}},
            increasing={"marker": {"color": "#5ceb9a"}},
            totals={"marker": {"color": "#7c8cf0"}},
        ))
        fig.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#ccc')
        st.plotly_chart(fig, width="stretch")


def render_gdp():
    st.header("📈 GDP Calculator")
    st.markdown("Hitung **Produk Domestik Bruto** menggunakan pendekatan pengeluaran (Y = C + I + G + (X − M)).")

    col1, col2 = st.columns(2)
    with col1:
        consumption = idr_input("Konsumsi (C) Rp", min_val=0, value=100_000_000_000, step=10_000_000_000, help_text="Pengeluaran konsumsi rumah tangga")
        investment = idr_input("Investasi (I) Rp", min_val=0, value=50_000_000_000, step=10_000_000_000, help_text="Investasi bisnis & modal tetap")
    with col2:
        govt = idr_input("Pengeluaran Pemerintah (G) Rp", min_val=0, value=30_000_000_000, step=10_000_000_000)
        export_val = idr_input("Ekspor (X) Rp", min_val=0, value=40_000_000_000, step=10_000_000_000)
        import_val = idr_input("Impor (M) Rp", min_val=0, value=20_000_000_000, step=10_000_000_000)

    if consumption or investment or govt:
        gdp = consumption + investment + govt + (export_val - import_val)
        net_exp = export_val - import_val

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown(f"""<div class="result-card"><h4>GDP Nominal</h4><div class="result-value">{fmt_idr(gdp)}</div><div class="result-label">Y = C + I + G + (X − M)</div></div>""", unsafe_allow_html=True)
        with col_b:
            st.markdown(f"""<div class="result-card"><h4>Net Ekspor</h4><div class="result-value">{fmt_idr(net_exp)}</div><div class="result-label">X − M</div></div>""", unsafe_allow_html=True)
        with col_c:
            contributions = {
                "Konsumsi (C)": consumption,
                "Investasi (I)": investment,
                "Pemerintah (G)": govt,
                "Net Ekspor (X−M)": net_exp,
            }
            max_contrib = max(contributions.values()) if max(contributions.values()) > 0 else 1

        # Horizontal bar chart of components
        fig = go.Figure()
        for label, val in contributions.items():
            pct = val / gdp * 100 if gdp > 0 else 0
            fig.add_trace(go.Bar(
                name=label, y=["GDP Components"], x=[val],
                orientation='h', text=f"{label}: {fmt_idr(val)} ({pct:.1f}%)",
                textposition='inside', textfont=dict(size=11),
                insidetextanchor='start',
            ))
        fig.update_layout(height=200, barmode='stack', showlegend=True,
                          plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                          font_color='#ccc', margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, width="stretch")

        # Pie chart
        fig2 = go.Figure(data=[go.Pie(
            labels=list(contributions.keys()),
            values=list(contributions.values()),
            textinfo='label+percent',
            hole=0.4,
            marker=dict(colors=px.colors.qualitative.Set2)
        )])
        fig2.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#ccc')
        st.plotly_chart(fig2, width="stretch")


def render_inflasi():
    st.header("📊 Inflasi Kalkulator")
    st.markdown("Hitung **tingkat inflasi** berdasarkan perubahan Indeks Harga Konsumen (IHK/CPI).")

    tab1, tab2 = st.tabs(["CPI Method", "Price Basket Method"])

    with tab1:
        st.subheader("Metode CPI / IHK")
        col1, col2 = st.columns(2)
        with col1:
            cpi_prev = st.number_input("CPI / IHK Periode Sebelumnya", min_value=0.0, value=105.5, step=0.1, format="%.2f")
        with col2:
            cpi_now = st.number_input("CPI / IHK Periode Sekarang", min_value=0.0, value=108.2, step=0.1, format="%.2f")

        if cpi_prev > 0:
            inflasi = (cpi_now - cpi_prev) / cpi_prev * 100
            st.markdown(f"""<div class="result-card">
                <h4>Tingkat Inflasi</h4>
                <div class="result-value">{inflasi:+.2f}%</div>
                <div class="result-label">CPI {cpi_prev:.1f} → {cpi_now:.1f}</div>
            </div>""", unsafe_allow_html=True)

            # Trend gauge
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=inflasi,
                number={"suffix": "%", "font": {"color": "#ccc"}},
                delta={"reference": 0},
                gauge={
                    "axis": {"range": [-5, 20], "tickfont": {"color": "#999"}},
                    "bar": {"color": "#ff6b6b" if inflasi > 0 else "#5ceb9a"},
                    "steps": [
                        {"range": [-5, 0], "color": "#2a3a2a"},
                        {"range": [0, 3], "color": "#2a3a2a"},
                        {"range": [3, 10], "color": "#3a2a2a"},
                        {"range": [10, 20], "color": "#4a1a1a"},
                    ],
                    "threshold": {"line": {"color": "white", "width": 4}, "value": inflasi},
                }
            ))
            fig.update_layout(height=300, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#ccc')
            st.plotly_chart(fig, width="stretch")

            # Inflation impact
            st.divider()
            st.subheader("💵 Dampak Inflasi terhadap Nilai Uang")
            nominal = idr_input("Nilai Uang Awal (Rp)", min_val=0, value=1_000_000, step=100_000, key="inflasi_val")
            if nominal > 0:
                real_val = nominal / (1 + inflasi / 100)
                st.markdown(f"""<div class="result-card">
                    <h4>Nilai Riil Setelah Inflasi</h4>
                    <div class="result-value">{fmt_idr(real_val)}</div>
                    <div class="result-label">Rp {nominal:,.0f} dulu → setara Rp {real_val:,.0f} sekarang (inflasi {inflasi:.2f}%)</div>
                </div>""", unsafe_allow_html=True)

    with tab2:
        st.subheader("Metode Basket Harga")
        st.markdown("Masukkan harga barang-barang di basket untuk menghitung inflasi.")
        n_barang = st.number_input("Jumlah barang", min_value=1, max_value=10, value=5, key="n_barang_basket")

        basket_data = []
        for i in range(n_barang):
            col1, col2, col3 = st.columns(3)
            with col1:
                nama = st.text_input(f"Nama Barang #{i+1}", value=f"Barang {i+1}", key=f"basket_n_{i}")
            with col2:
                harga_lama = st.number_input(f"Harga Dulu ({nama})", min_value=0.0, value=10000.0, step=1000.0, key=f"basket_l_{i}")
            with col3:
                harga_baru = st.number_input(f"Harga Sekarang ({nama})", min_value=0.0, value=11000.0, step=1000.0, key=f"basket_b_{i}")
            basket_data.append((nama, harga_lama, harga_baru))

        if basket_data:
            total_lama = sum(h[1] for h in basket_data)
            total_baru = sum(h[2] for h in basket_data)
            inflasi_basket = (total_baru - total_lama) / total_lama * 100

            st.markdown(f"""<div class="result-card">
                <h4>Inflasi Basket</h4>
                <div class="result-value">{inflasi_basket:+.2f}%</div>
                <div class="result-label">Total basket: {fmt_idr(total_lama)} → {fmt_idr(total_baru)}</div>
            </div>""", unsafe_allow_html=True)

            # Table
            df = pd.DataFrame(basket_data, columns=["Barang", "Harga Dulu", "Harga Sekarang"])
            df["Perubahan"] = df["Harga Sekarang"] - df["Harga Dulu"]
            df["%"] = (df["Perubahan"] / df["Harga Dulu"] * 100).round(2)
            st.dataframe(df, width="stretch", hide_index=True)


def render_bep():
    st.header("📊 Break-Even Point (BEP)")
    st.markdown("Hitung BEP dalam unit dan rupiah, serta visualisasikan.")

    col1, col2, col3 = st.columns(3)
    with col1:
        fixed_cost = idr_input("Biaya Tetap (FC) Rp", min_val=0, value=50_000_000, step=5_000_000)
    with col2:
        var_cost = idr_input("Biaya Variabel per Unit (VC) Rp", min_val=0, value=25_000, step=5_000)
    with col3:
        price = idr_input("Harga Jual per Unit (P) Rp", min_val=0, value=50_000, step=5_000)

    if price > var_cost > 0 and fixed_cost > 0:
        contribution = price - var_cost
        bep_units = ceil(fixed_cost / contribution)
        bep_revenue = bep_units * price

        # Margin of Safety simulation
        actual_units = st.number_input("Proyeksi Penjualan (unit)", min_value=0, value=bep_units + 5000, step=100)

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown(f"""<div class="result-card"><h4>BEP (unit)</h4><div class="result-value">{bep_units:,}</div><div class="result-label">unit</div></div>""", unsafe_allow_html=True)
        with col_b:
            st.markdown(f"""<div class="result-card"><h4>BEP (Rp)</h4><div class="result-value">{fmt_idr(bep_revenue)}</div><div class="result-label">pendapatan</div></div>""", unsafe_allow_html=True)
        with col_c:
            if actual_units > 0:
                profit = (price - var_cost) * actual_units - fixed_cost
                mos = (actual_units - bep_units) / actual_units * 100 if actual_units > 0 else 0
                st.markdown(f"""<div class="result-card"><h4>Laba/(Rugi)</h4><div class="result-value" style="color:{'#5ceb9a' if profit >=0 else '#ff6b6b'}">{fmt_idr(profit)}</div><div class="result-label">Margin of Safety: {mos:.1f}%</div></div>""", unsafe_allow_html=True)

        # BEP Chart
        units_range = np.arange(0, max(actual_units * 1.5, bep_units * 2, 100), max(1, max(actual_units, bep_units) // 50))
        tr = price * units_range
        tc = fixed_cost + var_cost * units_range

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=units_range, y=tr, name="Total Revenue (TR)", line=dict(color="#5ceb9a", width=2)))
        fig.add_trace(go.Scatter(x=units_range, y=tc, name="Total Cost (TC)", line=dict(color="#ff6b6b", width=2)))
        fig.add_trace(go.Scatter(x=[bep_units], y=[bep_revenue], mode="markers",
                                 name=f"BEP: {bep_units:,} units",
                                 marker=dict(color="#f0ad4e", size=12, symbol="star")))
        fig.add_hline(y=0, line_color="#444", line_width=0.5)
        fig.update_layout(height=400,
                          plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                          font_color='#ccc', xaxis_title="Units", yaxis_title="Rupiah",
                          hovermode="x unified")
        st.plotly_chart(fig, width="stretch")

    elif price <= var_cost:
        st.warning("⚠️ Harga jual harus lebih besar dari biaya variabel per unit.")
    else:
        st.info("Masukkan biaya tetap, biaya variabel, dan harga jual.")


def render_elastisitas():
    st.header("📈 Elastisitas Permintaan")
    st.markdown("Hitung **koefisien elastisitas harga permintaan** (Price Elasticity of Demand).")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Kondisi Awal")
        p1 = st.number_input("Harga Awal (P1)", min_value=0.0, value=10000.0, step=1000.0, format="%.0f")
        q1 = st.number_input("Kuantitas Awal (Q1)", min_value=0.0, value=100.0, step=10.0, format="%.0f")
    with col2:
        st.subheader("Kondisi Baru")
        p2 = st.number_input("Harga Baru (P2)", min_value=0.0, value=12000.0, step=1000.0, format="%.0f")
        q2 = st.number_input("Kuantitas Baru (Q2)", min_value=0.0, value=80.0, step=10.0, format="%.0f")

    if p1 > 0 and q1 > 0 and p2 > 0 and q2 > 0:
        # Midpoint method
        delta_p = p2 - p1
        delta_q = q2 - q1
        avg_p = (p1 + p2) / 2
        avg_q = (q1 + q2) / 2

        if avg_p != 0 and avg_q != 0:
            elastisitas = (delta_q / avg_q) / (delta_p / avg_p)
        else:
            elastisitas = 0

        # Jenis elastisitas
        if abs(elastisitas) == 0:
            jenis = "Perfectly Inelastic"
            desc = "Permintaan tidak berubah saat harga berubah"
        elif abs(elastisitas) < 1:
            jenis = "Inelastic"
            desc = "Permintaan kurang responsif terhadap perubahan harga"
        elif abs(elastisitas) == 1:
            jenis = "Unit Elastic"
            desc = "Perubahan kuantitas proporsional dengan perubahan harga"
        elif abs(elastisitas) < float('inf'):
            jenis = "Elastic"
            desc = "Permintaan sangat responsif terhadap perubahan harga"
        else:
            jenis = "Perfectly Elastic"
            desc = "Permintaan berubah drastis dengan perubahan harga"

        # Total Revenue
        tr1 = p1 * q1
        tr2 = p2 * q2

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown(f"""<div class="result-card"><h4>Koefisien Elastisitas</h4><div class="result-value">{elastisitas:+.4f}</div><div class="result-label">{jenis}</div></div>""", unsafe_allow_html=True)
        with col_b:
            st.markdown(f"""<div class="result-card"><h4>Total Revenue Awal</h4><div class="result-value">{fmt_idr(tr1)}</div><div class="result-label">P1 × Q1</div></div>""", unsafe_allow_html=True)
        with col_c:
            st.markdown(f"""<div class="result-card"><h4>Total Revenue Baru</h4><div class="result-value">{fmt_idr(tr2)}</div><div class="result-label">P2 × Q2</div></div>""", unsafe_allow_html=True)

        st.info(f"**{jenis}** — {desc}")

        # Demand curve
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[q1, q2], y=[p1, p2], mode="lines+markers",
                                 name="Demand Curve",
                                 line=dict(color="#7c8cf0", width=2),
                                 marker=dict(size=10, color=["#5ceb9a", "#ff6b6b"]),
                                 text=[f"E1: P={p1:,.0f}, Q={q1:,.0f}", f"E2: P={p2:,.0f}, Q={q2:,.0f}"]))

        fig.update_layout(height=400,
                          plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                          font_color='#ccc', xaxis_title="Quantity", yaxis_title="Price",
                          xaxis=dict(range=[0, max(q1, q2) * 1.5]),
                          yaxis=dict(range=[0, max(p1, p2) * 1.5]))
        st.plotly_chart(fig, width="stretch")

        # Revenue comparison
        st.divider()
        st.subheader("🔄 Perbandingan")
        df_el = pd.DataFrame({
            "": ["Awal (P1, Q1)", "Baru (P2, Q2)", "Perubahan"],
            "Harga": [f"Rp {p1:,.0f}", f"Rp {p2:,.0f}", f"{delta_p:+,.0f}"],
            "Kuantitas": [f"{q1:,.0f}", f"{q2:,.0f}", f"{delta_q:+,.0f}"],
            "Total Revenue": [f"Rp {tr1:,.0f}", f"Rp {tr2:,.0f}", f"Rp {tr2-tr1:+,.0f}"],
        })
        st.dataframe(df_el, width="stretch", hide_index=True)


def render_depresiasi():
    st.header("🏗️ Depresiasi Aset")
    st.markdown("Hitung penyusutan aset tetap dengan berbagai metode.")

    col1, col2, col3 = st.columns(3)
    with col1:
        cost = idr_input("Harga Perolehan Aset (Rp)", min_val=0, value=500_000_000, step=10_000_000)
    with col2:
        salvage = idr_input("Nilai Sisa (Rp)", min_val=0, value=50_000_000, step=5_000_000)
    with col3:
        useful_life = st.number_input("Masa Manfaat (tahun)", min_value=1, max_value=100, value=10, step=1)

    metode = st.radio("Metode Depresiasi", ["Straight Line", "Declining Balance", "Sum of Years Digits"], horizontal=True)

    if cost > salvage and useful_life > 0:
        years = list(range(1, useful_life + 1))

        if metode == "Straight Line":
            depr_annual = (cost - salvage) / useful_life
            depr_schedule = [depr_annual] * useful_life

        elif metode == "Declining Balance":
            rate_d = 2 / useful_life  # double declining
            book_val = cost
            depr_schedule = []
            for _ in range(useful_life - 1):
                d = book_val * rate_d
                depr_schedule.append(d)
                book_val -= d
            depr_schedule.append(book_val - salvage)  # last year catch-up
            depr_schedule = [max(0, d) for d in depr_schedule]

        else:  # Sum of Years Digits
            soyd = useful_life * (useful_life + 1) / 2
            depr_schedule = []
            for y in range(1, useful_life + 1):
                depr = (cost - salvage) * (useful_life - y + 1) / soyd
                depr_schedule.append(depr)

        # Build table
        book_val = cost
        schedule_rows = []
        for y, d in enumerate(depr_schedule, 1):
            book_val = max(salvage, book_val - d) if y > 1 else cost - d
            schedule_rows.append({
                "Tahun": y,
                "Depresiasi": fmt_idr(d),
                "Akumulasi": fmt_idr(cost - max(salvage, book_val - d if y == 1 else book_val + d - cost if y > 1 else 0)),
                "Nilai Buku": fmt_idr(max(salvage, book_val)),
            })

        total_depr = sum(depr_schedule)

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"""<div class="result-card"><h4>Depresiasi per Tahun</h4><div class="result-value">{fmt_idr(depr_schedule[0])}</div><div class="result-label">{metode}</div></div>""", unsafe_allow_html=True)
        with col_b:
            st.markdown(f"""<div class="result-card"><h4>Total Depresiasi</h4><div class="result-value">{fmt_idr(total_depr)}</div><div class="result-label">{useful_life} tahun</div></div>""", unsafe_allow_html=True)

        st.dataframe(pd.DataFrame(schedule_rows), width="stretch", hide_index=True)

        # Chart
        fig = go.Figure()
        fig.add_trace(go.Bar(x=years, y=depr_schedule, name="Depresiasi per Tahun", marker_color="#7c8cf0"))
        book_values = [max(salvage, cost - sum(depr_schedule[:i])) for i in range(len(depr_schedule))]
        fig.add_trace(go.Scatter(x=years, y=book_values, name="Nilai Buku",
                                 line=dict(color="#5ceb9a", width=2), mode="lines+markers"))
        fig.add_hline(y=salvage, line_dash="dash", line_color="#f0ad4e",
                      annotation_text=f"Nilai Sisa: {fmt_idr(salvage)}")
        fig.update_layout(height=400,
                          plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                          font_color='#ccc', xaxis_title="Tahun", yaxis_title="Rupiah",
                          hovermode="x unified")
        st.plotly_chart(fig, width="stretch")

    elif cost <= salvage:
        st.warning("⚠️ Harga perolehan harus lebih besar dari nilai sisa.")


def render_bunga_majemuk():
    st.header("💹 Bunga Majemuk (Compound Interest)")
    st.markdown("Hitung nilai masa depan, nilai sekarang, atau angsuran pinjaman.")

    mode = st.radio("Kalkulasi", ["Future Value (FV)", "Present Value (PV)", "Angsuran Pinjaman (PMT)"], horizontal=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        principal = idr_input("Principal / PV (Rp)", min_val=0, value=100_000_000, step=10_000_000, key="bunga_principal")
    with col2:
        rate = st.number_input("Suku Bunga (% per tahun)", min_value=0.0, value=12.0, step=0.5, format="%.2f")
    with col3:
        period = st.number_input("Periode (tahun)", min_value=1.0, value=5.0, step=0.5, format="%.1f")

    compound_freq = st.selectbox("Frekuensi Bunga Majemuk", ["Tahunan (1x)", "Semester (2x)", "Kuartal (4x)", "Bulanan (12x)", "Harian (365x)"], index=3)
    freq_map = {"Tahunan (1x)": 1, "Semester (2x)": 2, "Kuartal (4x)": 4, "Bulanan (12x)": 12, "Harian (365x)": 365}
    n = freq_map[compound_freq]

    annual_rate = rate / 100

    if mode == "Future Value (FV)":
        fv = principal * (1 + annual_rate / n) ** (n * period)
        interest_earned = fv - principal

        st.markdown(f"""<div class="result-card">
            <h4>Future Value</h4>
            <div class="result-value">{fmt_idr(fv)}</div>
            <div class="result-label">Investasi Rp {principal:,.0f} → Rp {fv:,.0f} dalam {period:.0f} tahun</div>
        </div>""", unsafe_allow_html=True)

        # Show effective annual rate
        ear = (1 + annual_rate / n) ** n - 1
        st.info(f"**Effective Annual Rate (EAR):** {ear*100:.4f}% (nominal {rate:.2f}%)")

    elif mode == "Present Value (PV)":
        fv_target = idr_input("Target Future Value (Rp)", min_val=0, value=200_000_000, step=10_000_000, key="bunga_fv")
        if fv_target > 0:
            pv = fv_target / (1 + annual_rate / n) ** (n * period)
            st.markdown(f"""<div class="result-card">
                <h4>Present Value</h4>
                <div class="result-value">{fmt_idr(pv)}</div>
                <div class="result-label">Butuh Rp {pv:,.0f} sekarang untuk dapat Rp {fv_target:,.0f} dalam {period:.0f} tahun</div>
            </div>""", unsafe_allow_html=True)
            principal = pv

    else:  # PMT — Angsuran Pinjaman
        if principal > 0 and annual_rate > 0:
            pmt = principal * (annual_rate / n) * (1 + annual_rate / n) ** (n * period) / ((1 + annual_rate / n) ** (n * period) - 1)
            total_payment = pmt * n * period
            total_interest = total_payment - principal

            st.markdown(f"""<div class="result-card">
                <h4>Angsuran per Bulan</h4>
                <div class="result-value">{fmt_idr(pmt)}</div>
                <div class="result-label">Pinjaman {fmt_idr(principal)} / {period:.0f} tahun / {rate:.2f}%</div>
            </div>""", unsafe_allow_html=True)
            col_x, col_y = st.columns(2)
            with col_x:
                st.metric("Total Pembayaran", fmt_idr(total_payment))
                st.metric("Total Bunga", fmt_idr(total_interest))

            # Amortization schedule (first 12 months + summary)
            schedule = []
            balance = principal
            monthly_rate = annual_rate / n
            for month in range(1, min(int(n * period) + 1, int(n * period) + 1)):
                interest_pmt = balance * monthly_rate
                principal_pmt = pmt - interest_pmt
                balance = max(0, balance - principal_pmt)
                schedule.append({"Bulan": month, "Angsuran": fmt_idr(pmt),
                                 "Bunga": fmt_idr(interest_pmt), "Pokok": fmt_idr(principal_pmt),
                                 "Sisa": fmt_idr(balance)})
                if month >= 60 and int(n * period) > 60:
                    schedule = schedule[:60]
                    schedule.append({"Bulan": "...", "Angsuran": "...", "Bunga": "...", "Pokok": "...", "Sisa": "..."})
                    schedule.append({"Bulan": int(n * period), "Angsuran": fmt_idr(pmt),
                                     "Bunga": fmt_idr(interest_pmt), "Pokok": fmt_idr(principal_pmt),
                                     "Sisa": fmt_idr(balance)})
                    break

            st.subheader("📋 Jadwal Amortisasi")
            with st.expander("Lihat detail angsuran"):
                st.dataframe(pd.DataFrame(schedule), width="stretch", hide_index=True)

    # Compound growth chart
    years_range = np.arange(0, period + 0.5, 0.5)
    values = [principal * (1 + annual_rate / n) ** (n * y) for y in years_range]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=years_range, y=values, name="Growth",
                             fill='tozeroy', line=dict(color="#7c8cf0", width=2)))
    fig.add_trace(go.Scatter(x=[0, period], y=[principal, values[-1]], mode="markers",
                             marker=dict(color=["#5ceb9a", "#ff6b6b"], size=10),
                             text=[f"PV: {fmt_idr(principal)}", f"FV: {fmt_idr(values[-1])}"]))
    fig.update_layout(height=400,
                      plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                      font_color='#ccc', xaxis_title="Tahun", yaxis_title="Nilai (Rp)",
                      hovermode="x unified")
    st.plotly_chart(fig, width="stretch")


# ═══════════════════════════════════════════════════════════════
#  ACCOUNTING — General Journal, Ledger, Trial Balance
# ═══════════════════════════════════════════════════════════════

# ─── Chart of Accounts ───

SERVICE_ACCOUNTS = {
    "Assets": ["Cash", "Accounts Receivable", "Supplies", "Prepaid Insurance", "Equipment", "Accum. Depreciation - Equipment"],
    "Liabilities": ["Accounts Payable", "Salaries Payable", "Unearned Revenue"],
    "Equity": ["Owner's Capital", "Owner's Drawings", "Income Summary"],
    "Revenue": ["Service Revenue"],
    "Expenses": ["Salaries Expense", "Supplies Expense", "Rent Expense", "Insurance Expense",
                 "Depreciation Expense", "Utilities Expense", "Advertising Expense", "Miscellaneous Expense"],
}

TRADING_ACCOUNTS = {
    "Assets": ["Cash", "Accounts Receivable", "Merchandise Inventory", "Supplies", "Prepaid Insurance",
               "Equipment", "Accum. Depreciation - Equipment", "Building", "Accum. Depreciation - Building"],
    "Liabilities": ["Accounts Payable", "Salaries Payable", "Unearned Revenue", "Notes Payable"],
    "Equity": ["Owner's Capital", "Owner's Drawings", "Income Summary"],
    "Revenue": ["Sales Revenue", "Service Revenue"],
    "COGS": ["Cost of Goods Sold", "Purchases", "Purchase Returns", "Purchase Discounts",
              "Freight In", "Sales Returns", "Sales Discounts"],
    "Expenses": ["Salaries Expense", "Supplies Expense", "Rent Expense", "Insurance Expense",
                 "Depreciation Expense", "Utilities Expense", "Advertising Expense", "Interest Expense",
                 "Miscellaneous Expense"],
}

# All accounts flat list for dropdowns
ALL_SERVICE_ACCOUNTS = []
for items in SERVICE_ACCOUNTS.values():
    ALL_SERVICE_ACCOUNTS.extend(items)

ALL_TRADING_ACCOUNTS = []
for items in TRADING_ACCOUNTS.values():
    ALL_TRADING_ACCOUNTS.extend(items)

def get_account_type(account_name, company_type):
    """Get the classification of an account (Asset, Liability, Equity, Revenue, Expense, COGS)."""
    chart = TRADING_ACCOUNTS if company_type == "Trading" else SERVICE_ACCOUNTS
    for cat, accounts in chart.items():
        if account_name in accounts:
            return cat
    return "Other"

def get_account_normal_balance(account_type):
    """Return 'Debit' or 'Credit' for normal balance side."""
    debit_types = ["Assets", "Expenses", "COGS", "Owner's Drawings"]
    credit_types = ["Liabilities", "Equity", "Revenue", "Owner's Capital"]
    if account_type in debit_types:
        return "Debit"
    return "Credit"

def init_journal_state():
    """Initialize session state for journal entries."""
    if "journal_entries" not in st.session_state:
        st.session_state.journal_entries = []
    if "journal_ref_counter" not in st.session_state:
        st.session_state.journal_ref_counter = 1
    if "company_type" not in st.session_state:
        st.session_state.company_type = "Service"


# ─── Accounting Dashboard (All-in-One) ───

def render_accounting_dashboard():
    st.header("📋 Accounting Dashboard")
    st.markdown("All-in-one: post journal entries, view ledger, and check trial balance on one page.")

    init_journal_state()

    company_type = st.radio("Company Type", ["Service", "Trading"], horizontal=True,
                            help="Service: for service-based businesses. Trading: includes merchandising accounts.")
    st.session_state.company_type = company_type
    available_accounts = ALL_TRADING_ACCOUNTS if company_type == "Trading" else ALL_SERVICE_ACCOUNTS
    filtered = [e for e in st.session_state.journal_entries if e.get("company_type") == company_type]

    # ════════════════════════════════════════
    # SECTION 1: New Journal Entry
    # ════════════════════════════════════════
    with st.expander("📝 New Journal Entry", expanded=True):
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            entry_date = st.date_input("Date", key="dash_date")
        with col_d2:
            entry_desc = st.text_input("Description", placeholder="e.g., Paid rent", key="dash_desc")

        num_lines = st.number_input("Lines", min_value=2, max_value=6, value=2, step=1, key="dash_lines")

        entry_lines = []
        total_debit = 0
        total_credit = 0

        cols = st.columns([3, 2, 2])
        cols[0].markdown("**Account**")
        cols[1].markdown("**Debit**")
        cols[2].markdown("**Credit**")

        for i in range(int(num_lines)):
            cols = st.columns([3, 2, 2])
            with cols[0]:
                acc = st.selectbox(f"A{i+1}", available_accounts, key=f"da_acc_{i}", label_visibility="collapsed")
            with cols[1]:
                deb = st.number_input(f"Db{i+1}", min_value=0, value=0, step=10000, format="%d", key=f"da_db_{i}", label_visibility="collapsed")
            with cols[2]:
                cred = st.number_input(f"Cr{i+1}", min_value=0, value=0, step=10000, format="%d", key=f"da_cr_{i}", label_visibility="collapsed")
            entry_lines.append({"account": acc, "debit": deb, "credit": cred})
            total_debit += deb
            total_credit += cred

        if total_debit > 0 or total_credit > 0:
            diff = total_debit - total_credit
            if abs(diff) < 1:
                st.success(f"✅ Balanced: Debit = Credit = Rp {total_debit:,.0f}")
            else:
                st.error(f"❌ Unbalanced! Diff: Rp {abs(diff):,.0f}")

        if st.button("📌 Post Entry", type="primary",
                     disabled=abs(total_debit - total_credit) > 0.5 or total_debit == 0):
            ref = f"JU-{st.session_state.journal_ref_counter:03d}"
            st.session_state.journal_entries.append({
                "date": entry_date.strftime("%Y-%m-%d"),
                "description": entry_desc,
                "entries": [e for e in entry_lines if e["debit"] > 0 or e["credit"] > 0],
                "reference": ref,
                "company_type": company_type,
            })
            st.session_state.journal_ref_counter += 1
            st.success(f"✅ Entry {ref} posted!")
            st.rerun()

    # ════════════════════════════════════════
    # SECTION 2: Journal Records
    # ════════════════════════════════════════
    st.divider()
    st.subheader("📖 Journal Records")

    if st.button("🗑️ Clear All", key="dash_clear"):
        st.session_state.journal_entries = []
        st.session_state.journal_ref_counter = 1
        st.rerun()

    if not filtered:
        st.info("No entries yet. Post your first entry above!")
    else:
        for entry in filtered:
            ref = entry["reference"]
            with st.expander(f"**{ref}** — {entry['date']} | {entry['description']}", expanded=False):
                rows = []
                for line in entry["entries"]:
                    rows.append({
                        "Account": line["account"],
                        "Debit": f"Rp {line['debit']:,.0f}" if line['debit'] > 0 else "",
                        "Credit": f"Rp {line['credit']:,.0f}" if line['credit'] > 0 else "",
                    })
                st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
                if st.button(f"Delete {ref}", key=f"dd_{ref}"):
                    st.session_state.journal_entries = [
                        e for e in st.session_state.journal_entries if e["reference"] != ref
                    ]
                    st.rerun()

    # ════════════════════════════════════════
    # SECTION 3: General Ledger Preview
    # ════════════════════════════════════════
    if filtered:
        st.divider()
        st.subheader("📒 Ledger Preview")

        # Build ledger
        ledger = {}
        for entry in filtered:
            for line in entry["entries"]:
                acc = line["account"]
                if acc not in ledger:
                    ledger[acc] = []
                ledger[acc].append({"date": entry["date"], "ref": entry["reference"],
                                     "debit": line["debit"], "credit": line["credit"]})

        sel_acc = st.selectbox("Select account to view", sorted(ledger.keys()), key="dash_ledger_acc")
        if sel_acc:
            entries = ledger[sel_acc]
            balance = 0
            rows = []
            for e in entries:
                balance += e["debit"] - e["credit"]
                side = "Dr" if balance >= 0 else "Cr"
                rows.append({
                    "Date": e["date"], "Ref": e["ref"],
                    "Debit": f"Rp {e['debit']:,.0f}" if e['debit'] > 0 else "",
                    "Credit": f"Rp {e['credit']:,.0f}" if e['credit'] > 0 else "",
                    "Balance": f"Rp {abs(balance):,.0f} {side}",
                })
            st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

    # ════════════════════════════════════════
    # SECTION 4: Trial Balance Preview
    # ════════════════════════════════════════
    if filtered:
        st.divider()
        st.subheader("⚖️ Trial Balance Preview")

        balances = {}
        for entry in filtered:
            for line in entry["entries"]:
                acc = line["account"]
                if acc not in balances:
                    balances[acc] = 0
                balances[acc] += line["debit"] - line["credit"]

        class_order = {"Assets": 0, "Liabilities": 1, "Equity": 2, "Revenue": 3, "COGS": 4, "Expenses": 5}
        sorted_accs = sorted(balances.keys(),
                             key=lambda a: (class_order.get(get_account_type(a, company_type), 99), a))

        tb_rows = []
        t_dr, t_cr = 0, 0
        for acc in sorted_accs:
            bal = balances[acc]
            dr = bal if bal >= 0 else 0
            cr = abs(bal) if bal < 0 else 0
            t_dr += dr
            t_cr += cr
            tb_rows.append({
                "Account": acc,
                "Debit": f"Rp {dr:,.0f}" if dr > 0 else "",
                "Credit": f"Rp {cr:,.0f}" if cr > 0 else "",
            })

        st.dataframe(pd.DataFrame(tb_rows), width="stretch", hide_index=True)

        col_t1, col_t2, col_t3 = st.columns(3)
        balanced = abs(t_dr - t_cr) < 1
        with col_t1:
            st.metric("Total Debit", f"Rp {t_dr:,.0f}")
        with col_t2:
            st.metric("Total Credit", f"Rp {t_cr:,.0f}")
        with col_t3:
            st.metric("Status", "✅ Balanced" if balanced else "❌ Unbalanced")


# ═══════════════════════════════════════════════════════════════
#  ACCOUNTING EQUATION
# ═══════════════════════════════════════════════════════════════

def render_accounting_equation():
    st.header("📐 Accounting Equation")
    st.markdown("""
    The foundation of double-entry bookkeeping:
    """)

    # Core Equation Card
    st.markdown(f"""
    <div class="result-card" style="text-align:center;padding:24px;">
        <span style="font-size:2em;font-weight:bold;color:#5ceb9a;">Assets</span>
        <span style="font-size:2em;color:#7c8cf0;"> = </span>
        <span style="font-size:2em;font-weight:bold;color:#f0ad4e;">Liabilities</span>
        <span style="font-size:2em;color:#7c8cf0;"> + </span>
        <span style="font-size:2em;font-weight:bold;color:#ff6b6b;">Equity</span>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🧮 Calculator", "📊 Transaction Analyzer", "💡 Quick Reference"])

    # ─── Tab 1: Calculator ───
    with tab1:
        st.markdown("Enter any **two** values to compute the third.")

        col_a, col_l, col_e = st.columns(3)
        with col_a:
            assets = st.number_input("Assets (Rp)", min_value=0.0, value=0.0, step=100_000.0,
                                     format="%f", key="ae_assets")
        with col_l:
            liabilities = st.number_input("Liabilities (Rp)", min_value=0.0, value=0.0, step=100_000.0,
                                          format="%f", key="ae_liab")
        with col_e:
            equity = st.number_input("Equity (Rp)", min_value=0.0, value=0.0, step=100_000.0,
                                     format="%f", key="ae_equity")

        # Determine which values are filled
        filled = sum([1 for v in [assets, liabilities, equity] if v > 0])

        if filled >= 2:
            # Solve for missing
            if assets > 0 and liabilities > 0 and equity == 0:
                equity = assets - liabilities
                mode = "Equity = Assets − Liabilities"
            elif assets > 0 and equity > 0 and liabilities == 0:
                liabilities = assets - equity
                mode = "Liabilities = Assets − Equity"
            elif liabilities > 0 and equity > 0 and assets == 0:
                assets = liabilities + equity
                mode = "Assets = Liabilities + Equity"
            else:
                # All three filled — verify
                mode = "Verification"

            diff = assets - (liabilities + equity)
            balanced = abs(diff) < 0.01

            st.divider()

            # Results
            res_a, res_b, res_c = st.columns(3)
            with res_a:
                st.markdown(f"""<div class="result-card">
                    <h4>Assets</h4>
                    <div class="result-value">Rp {assets:,.0f}</div>
                </div>""", unsafe_allow_html=True)
            with res_b:
                st.markdown(f"""<div class="result-card">
                    <h4>Liabilities</h4>
                    <div class="result-value">Rp {liabilities:,.0f}</div>
                </div>""", unsafe_allow_html=True)
            with res_c:
                st.markdown(f"""<div class="result-card">
                    <h4>Equity</h4>
                    <div class="result-value">Rp {equity:,.0f}</div>
                </div>""", unsafe_allow_html=True)

            st.info(f"📌 {mode}")

            # Balanced indicator
            if balanced:
                st.success(f"✅ **Equation is BALANCED** — Rp {assets:,.0f} = Rp {liabilities:,.0f} + Rp {equity:,.0f}")
            else:
                st.error(f"❌ **Equation is UNBALANCED** by Rp {abs(diff):,.0f}")
                st.markdown(f"<div style='text-align:center;font-size:1.2em'>"
                            f"Rp {liabilities + equity:,.0f} (L+E) ≠ Rp {assets:,.0f} (A)</div>",
                            unsafe_allow_html=True)

            # Horizontal stacked bar
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name="Liabilities",
                x=["Equation"],
                y=[liabilities],
                marker_color="#f0ad4e",
                text=f"Rp {liabilities:,.0f}" if liabilities > 0 else "",
                textposition="inside",
                hovertemplate="Liabilities: Rp %{y:,.0f}<extra></extra>"
            ))
            fig.add_trace(go.Bar(
                name="Equity",
                x=["Equation"],
                y=[equity],
                marker_color="#ff6b6b",
                text=f"Rp {equity:,.0f}" if equity > 0 else "",
                textposition="inside",
                hovertemplate="Equity: Rp %{y:,.0f}<extra></extra>"
            ))
            fig.update_layout(
                barmode="stack",
                title="<b>Liabilities + Equity</b>",
                height=250,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#ccc",
                showlegend=True,
                margin=dict(l=10, r=10, t=40, b=10),
                xaxis=dict(showticklabels=True),
                yaxis=dict(title="Rupiah", tickformat=",.0f")
            )
            st.plotly_chart(fig, use_container_width=True)

            # Also show Assets bar for comparison
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                name="Assets",
                x=["Assets"],
                y=[assets],
                marker_color="#5ceb9a",
                text=f"Rp {assets:,.0f}",
                textposition="inside",
                hovertemplate="Assets: Rp %{y:,.0f}<extra></extra>"
            ))
            fig2.add_trace(go.Bar(
                name="Liabilities + Equity",
                x=["Liabilities + Equity"],
                y=[liabilities + equity],
                marker_color="#7c8cf0",
                text=f"Rp {liabilities + equity:,.0f}",
                textposition="inside",
                hovertemplate="L+E: Rp %{y:,.0f}<extra></extra>"
            ))
            fig2.update_layout(
                title="<b>Side-by-Side Comparison</b>",
                height=250,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#ccc",
                showlegend=True,
                margin=dict(l=10, r=10, t=40, b=10),
                yaxis=dict(title="Rupiah", tickformat=",.0f")
            )
            st.plotly_chart(fig2, use_container_width=True)

        elif filled == 1:
            st.warning("⚠️ Enter at least **two** values to compute the third.")
        else:
            st.info("👆 Enter values above to start.")

    # ─── Tab 2: Transaction Analyzer ───
    with tab2:
        st.markdown("See how common transactions affect the accounting equation.")

        TRANSACTIONS = [
            ("Owner invests Rp 10,000,000 cash into business",
             "Assets (Cash) +10,000,000", "Liabilities: 0", "Equity (Capital) +10,000,000",
             10_000_000, 0, 10_000_000),
            ("Purchase equipment for Rp 5,000,000 cash",
             "Assets (Equipment) +5,000,000 | Assets (Cash) −5,000,000", "Liabilities: 0", "Equity: 0",
             0, 0, 0),
            ("Purchase supplies on credit Rp 2,000,000",
             "Assets (Supplies) +2,000,000", "Liabilities (Accounts Payable) +2,000,000", "Equity: 0",
             2_000_000, 2_000_000, 0),
            ("Provide services for Rp 3,000,000 cash",
             "Assets (Cash) +3,000,000", "Liabilities: 0", "Equity (Revenue) +3,000,000",
             3_000_000, 0, 3_000_000),
            ("Pay Rp 1,000,000 rent in cash",
             "Assets (Cash) −1,000,000", "Liabilities: 0", "Equity (Expense) −1,000,000",
             -1_000_000, 0, -1_000_000),
            ("Borrow Rp 15,000,000 from bank",
             "Assets (Cash) +15,000,000", "Liabilities (Notes Payable) +15,000,000", "Equity: 0",
             15_000_000, 15_000_000, 0),
            ("Owner withdraws Rp 2,000,000 for personal use",
             "Assets (Cash) −2,000,000", "Liabilities: 0", "Equity (Drawings) −2,000,000",
             -2_000_000, 0, -2_000_000),
            ("Pay Rp 500,000 of accounts payable",
             "Assets (Cash) −500,000", "Liabilities (Accounts Payable) −500,000", "Equity: 0",
             -500_000, -500_000, 0),
            ("Receive Rp 4,000,000 advance payment from customer",
             "Assets (Cash) +4,000,000", "Liabilities (Unearned Revenue) +4,000,000", "Equity: 0",
             4_000_000, 4_000_000, 0),
            ("Depreciation of equipment Rp 800,000",
             "Assets (Accum. Depr.) −800,000", "Liabilities: 0", "Equity (Depr. Expense) −800,000",
             -800_000, 0, -800_000),
        ]

        # Running totals
        if "ae_running_a" not in st.session_state:
            st.session_state.ae_running_a = 0
            st.session_state.ae_running_l = 0
            st.session_state.ae_running_e = 0

        col_tx, col_rn = st.columns([2, 1])

        with col_tx:
            selected = st.selectbox(
                "Select a transaction to analyze:",
                [t[0] for t in TRANSACTIONS],
                index=None,
                placeholder="Choose a transaction...",
                key="ae_tx_select"
            )

        if selected:
            tx = next(t for t in TRANSACTIONS if t[0] == selected)
            _, da, dl, de, ca, cl, ce = tx

            st.markdown(f"""<div class="result-card">
                <h4>{selected}</h4>
                <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-top:12px;">
                    <div style="background:#1a2a1a;padding:12px;border-radius:8px;border:1px solid #3a6a3a;">
                        <div style="color:#5ceb9a;font-weight:bold">📈 Assets</div>
                        <div style="color:#ddd;font-size:0.9em;margin-top:4px">{da}</div>
                        <div style="color:#5ceb9a;font-size:1.2em;font-weight:bold;margin-top:6px">Δ Rp {ca:+,.0f}</div>
                    </div>
                    <div style="background:#2a281a;padding:12px;border-radius:8px;border:1px solid #6a5a3a;">
                        <div style="color:#f0ad4e;font-weight:bold">📉 Liabilities</div>
                        <div style="color:#ddd;font-size:0.9em;margin-top:4px">{dl}</div>
                        <div style="color:#f0ad4e;font-size:1.2em;font-weight:bold;margin-top:6px">Δ Rp {cl:+,.0f}</div>
                    </div>
                    <div style="background:#2a1a1a;padding:12px;border-radius:8px;border:1px solid #6a3a3a;">
                        <div style="color:#ff6b6b;font-weight:bold">📊 Equity</div>
                        <div style="color:#ddd;font-size:0.9em;margin-top:4px">{de}</div>
                        <div style="color:#ff6b6b;font-size:1.2em;font-weight:bold;margin-top:6px">Δ Rp {ce:+,.0f}</div>
                    </div>
                </div>
                <div style="text-align:center;margin-top:16px;padding:10px;background:#1a1d2a;border-radius:8px;">
                    <span style="color:#7c8cf0;font-weight:bold">Equation: </span>
                    <span style="color:#5ceb9a">ΔA = Rp {ca:+,.0f}</span>
                    <span style="color:#7c8cf0"> = </span>
                    <span style="color:#f0ad4e">ΔL = Rp {cl:+,.0f}</span>
                    <span style="color:#7c8cf0"> + </span>
                    <span style="color:#ff6b6b">ΔE = Rp {ce:+,.0f}</span>
                </div>
            </div>""", unsafe_allow_html=True)

            with col_rn:
                if st.button("➕ Apply to Running Total", use_container_width=True, key="ae_apply"):
                    st.session_state.ae_running_a += ca
                    st.session_state.ae_running_l += cl
                    st.session_state.ae_running_e += ce

        else:
            with col_rn:
                pass

        # Running total display
        st.divider()
        st.subheader("📊 Running Total")

        r_a = st.session_state.ae_running_a
        r_l = st.session_state.ae_running_l
        r_e = st.session_state.ae_running_e
        r_balanced = abs(r_a - (r_l + r_e)) < 0.01

        cols = st.columns(4)
        cols[0].metric("Assets", f"Rp {r_a:,.0f}", delta=None)
        cols[1].metric("Liabilities", f"Rp {r_l:,.0f}", delta=None)
        cols[2].metric("Equity", f"Rp {r_e:,.0f}", delta=None)
        cols[3].metric("Status", "✅ Balanced" if r_balanced else "❌ Unbalanced",
                        delta=None if r_balanced else f"Off by Rp {abs(r_a - r_l - r_e):,.0f}")

        if r_balanced and (r_a > 0 or r_l > 0 or r_e > 0):
            st.success(f"✅ **A = L + E** → Rp {r_a:,.0f} = Rp {r_l:,.0f} + Rp {r_e:,.0f}")

        c1, c2, _ = st.columns([1, 1, 3])
        if c1.button("🔄 Reset", use_container_width=True, key="ae_reset"):
            st.session_state.ae_running_a = 0
            st.session_state.ae_running_l = 0
            st.session_state.ae_running_e = 0
            st.rerun()

    # ─── Tab 3: Quick Reference ───
    with tab3:
        st.markdown("""
        ### Key Formulas

        | Formula | Description |
        |---------|-------------|
        | **A = L + E** | **Accounting Equation** — the foundation |
        | **L = A − E** | Solve for Liabilities |
        | **E = A − L** | Solve for Equity (Net Assets) |
        | **E = C + R − Eₓ − D** | Expanded: Capital + Revenue − Expenses − Drawings |

        ### Expanded Accounting Equation
        """)
        st.markdown(f"""
        <div class="result-card" style="text-align:center;padding:20px;">
            <span style="font-size:1.4em;font-weight:bold;color:#5ceb9a;">Assets</span>
            <span style="font-size:1.4em;color:#7c8cf0;"> = </span>
            <span style="font-size:1.4em;font-weight:bold;color:#f0ad4e;">Liabilities</span>
            <span style="font-size:1.4em;color:#7c8cf0;"> + </span>
            <span style="font-size:1.4em;color:#ff6b6b;">Owner's Capital</span>
            <span style="font-size:1.4em;color:#7c8cf0;"> + </span>
            <span style="font-size:1.4em;color:#5ceb9a;">Revenues</span>
            <span style="font-size:1.4em;color:#7c8cf0;"> − </span>
            <span style="font-size:1.4em;color:#f0ad4e;">Expenses</span>
            <span style="font-size:1.4em;color:#7c8cf0;"> − </span>
            <span style="font-size:1.4em;color:#ff6b6b;">Drawings</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        ### Debit & Credit Rules

        | Account Type | Increases | Decreases | Normal Balance |
        |-------------|-----------|-----------|----------------|
        | **Assets** | Debit (Dr) | Credit (Cr) | Debit |
        | **Liabilities** | Credit (Cr) | Debit (Dr) | Credit |
        | **Equity (Capital)** | Credit (Cr) | Debit (Dr) | Credit |
        | **Revenue** | Credit (Cr) | Debit (Dr) | Credit |
        | **Expenses** | Debit (Dr) | Credit (Cr) | Debit |

        ### Golden Rule
        > **For every transaction, total debits must equal total credits.**
        > This ensures the accounting equation always stays balanced.
        """)


# ═══════════════════════════════════════════════════════════════

def main():
    cat, topic = sidebar_nav()

    st.markdown(f"<p style='color:#7c8cf0;font-size:0.9em'>{cat}</p>", unsafe_allow_html=True)

    render_map = {
        "PPh 21 (TER)": render_pph21_ter,
        "PPh 21 Tahunan": render_pph21_annual,
        "PPN (VAT)": render_ppn,
        "PPh Final": render_pph_final,
        "PPh Badan": render_pph_badan,
        "PBB": render_pbb,
        "Take Home Pay": render_take_home_pay,
        "GDP Calculator": render_gdp,
        "Inflasi Kalkulator": render_inflasi,
        "Break-Even Point": render_bep,
        "Elastisitas Permintaan": render_elastisitas,
        "Depresiasi Aset": render_depresiasi,
        "Bunga Majemuk": render_bunga_majemuk,
        "📋 Accounting Dashboard": render_accounting_dashboard,
        "📐 Accounting Equation": render_accounting_equation,
    }

    if topic in render_map:
        render_map[topic]()

    # Footer disclaimer
    st.divider()
    st.markdown("""
    <div style="text-align:center;color:#555;font-size:0.8em;padding:20px 0">
        📊 <b>StudyLab — Economics</b> | Data pajak berdasarkan PMK 168/2023 &amp; PP 58/2023 | 
        ⚠️ Alat bantu belajar, bukan konsultasi pajak resmi | 
        <a href="https://github.com/teeceetan2-cyber/studylab-economics" style="color:#7c8cf0">GitHub</a>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
