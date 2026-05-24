# 📊 StudyLab — Economics

Interactive economics, taxation, and accounting tools built with Streamlit.

## Features

### 🇮🇩 Perpajakan Indonesia (Indonesian Taxation)
- **PPh 21 (TER)** — Monthly income tax using Tarif Efektif Rata-rata (PMK 168/2023)
- **PPh 21 Tahunan** — Annual progressive tax (Pasal 17)
- **PPN (VAT)** — Value Added Tax calculator
- **PPh Final** — Final income tax (e.g., rental, construction)
- **PPh Badan** — Corporate income tax
- **PBB** — Land & building tax
- **Take Home Pay** — Net salary after deductions

### 📈 Ekonomi Makro & Mikro (Macro & Micro Economics)
- **GDP Calculator** — Calculate GDP using expenditure approach
- **Inflasi Kalkulator** — Inflation calculator & purchasing power
- **Break-Even Point** — BEP analysis (units & rupiah)
- **Elastisitas Permintaan** — Price elasticity of demand
- **Depresiasi Aset** — Asset depreciation (straight-line, declining balance)
- **Bunga Majemuk** — Compound interest & future value

### 📋 Basic Accounting
- **Accounting Dashboard** — All-in-one: Chart of Accounts, General Journal, Ledger, Trial Balance

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

Or deploy on **Streamlit Cloud**: connect this repo and set entry point to `app.py`.

## Stack
- **Streamlit** — interactive web UI
- **Plotly** — data visualization
- **NumPy / Pandas** — numerical computation

> ⚠️ *Tax data based on PMK 168/2023 & PP 58/2023. Not official tax advice — educational tool only.*
