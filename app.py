import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time

st.set_page_config(page_title="ICU Early Warning Dashboard", layout="wide")

st.title("ICU EARLY WARNING DASHBOARD")
st.caption("Monitoring Pasien Secara Real-Time dengan Tren Grafik")

# Data Kronologi Observasi 6 Jam Pasien
data_skenario = [
    {"jam": "08.00", "hr": 92,  "td": "118/76", "map": 90, "rr": 20, "spo2": 98, "suhu": 37.5, "status": "STABIL", "ews": 2, "warna": "#28A745", "text": "white", "Rekomendasi": "• Monitor tanda vital\n• Observasi berkala setiap shift\n• Pertahankan terapi dokter"},
    {"jam": "10.00", "hr": 108, "td": "102/68", "map": 79, "rr": 24, "spo2": 96, "suhu": 38.2, "status": "WASPADA", "ews": 5, "warna": "#FFAA00", "text": "black", "Rekomendasi": "• Tingkatkan frekuensi observasi (tiap 1-2 jam)\n• Laporkan perkembangan ke Dokter Jaga\n• Monitor perfusi jaringan"},
    {"jam": "12.00", "hr": 126, "td": "86/54",  "map": 65, "rr": 30, "spo2": 92, "suhu": 38.7, "status": "RISIKO TINGGI", "ews": 8, "warna": "#FF8C00", "text": "white", "Rekomendasi": "• Persiapan alat resusitasi di dekat bed\n• Monitoring tanda vital secara kontinu\n• Kolaborasi evaluasi dengan tim medis intensif"},
    {"jam": "14.00", "hr": 142, "td": "70/42",  "map": 51, "rr": 34, "spo2": 88, "suhu": 39.2, "status": "KRITIS", "ews": 12, "warna": "#FF4B4B", "text": "white", "Rekomendasi": "• AKTIVASI CODE BLUE SEGERA!\n• Lakukan tindakan resusitasi dan bebaskan jalan napas\n• Siapkan kesiapan mesin ventilator"}
]

if 'indeks_simulasi' not in st.session_state:
    st.session_state.indeks_simulasi = 0
if 'berjalan' not in st.session_state:
    st.session_state.berjalan = False

st.markdown("### ⚙️ Kontrol Simulasi")
c1, c2 = st.columns(2)
with c1:
    if st.button("▶️ Mulai Jalankan Simulasi"):
        st.session_state.berjalan = True
with c2:
    if st.button("🔄 Reset ke Jam 08.00"):
        st.session_state.indeks_simulasi = 0
        st.session_state.berjalan = False
        st.rerun()

idx = st.session_state.indeks_simulasi
p = data_skenario[idx]

st.markdown("---")
kolom_kiri, kolom_tengah, kolom_kanan = st.columns([1.2, 3, 1.2])

with kolom_kiri:
    st.subheader("📋 Data Pasien")
    st.markdown(f"""
    * **Nama:** Tn. A (58 Tahun)
    * **No. Bed:** ICU Bed 03
    * **Diagnosis:** Sepsis Pneumonia
    * **Jam Observasi:** Pukul {p['jam']} WIB
    * **Dokter DPJP:** dr. Alin Edwar, Sp.An
    * **Perawat Jaga:** Ns. Desta, S.Kep
    """)

with kolom_tengah:
    st.markdown(f"""
    <div style="background-color:{p['warna']}; padding:18px; border-radius:8px; text-align:center; margin-bottom:15px;">
        <h2 style="color:{p['text']}; margin:0; font-weight:bold;">KONDISI PASIEN: {p['status']}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    t1, t2, t3 = st.columns(3)
    t1.metric("Heart Rate (HR)", f"{p['hr']} bpm", "Normal: 60-100")
    t2.metric("Blood Pressure (BP)", f"{p['td']} mmHg", "Normal: 120/80")
    t3.metric("MAP", f"{p['map']} mmHg", "Normal: >65")
    
    t4, t5, t6 = st.columns(3)
    t4.metric("Respiratory Rate (RR)", f"{p['rr']} x/menit", "Normal: 12-20")
    t5.metric("Saturasi Oksigen (SpO2)", f"{p['spo2']} %", "Normal: 95-100")
    t6.metric("Temperature (Suhu)", f"{p['suhu']} °C", "Normal: 36.5-37.5")
    
    # --- BAGIAN GRAFIK TREN ---
    st.markdown("---")
    st.subheader("📈 Grafik Tren Perburukan Tanda Vital")
    
    histori = data_skenario[:idx+1]
    df_histori = pd.DataFrame(histori)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_histori['jam'], y=df_histori['hr'], name='Heart Rate (bpm)', line=dict(color='#FF4B4B', width=3)))
    fig.add_trace(go.Scatter(x=df_histori['jam'], y=df_histori['map'], name='MAP (mmHg)', line=dict(color='#0083B0', width=3)))
    fig.add_trace(go.Scatter(x=df_histori['jam'], y=df_histori['spo2'], name='SpO2 (%)', line=dict(color='#28A745', width=3)))
    
    fig.update_layout(template="plotly_dark", height=300, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("💡 Instruksi / Rekomendasi Klinik Perawat:")
    st.info(p['Rekomendasi'])

with kolom_kanan:
    st.subheader("🎯 Skor EWS")
    st.markdown(f"""
    <div style="background-color:#1E1E1E; padding:30px; border-radius:10px; border:3px solid {p['warna']}; text-align:center;">
        <h1 style="color:{p['warna']}; font-size: 70px; margin:0; font-weight:bold;">{p['ews']}</h1>
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    
    st.write("**Panduan Klasifikasi Skor:**")
    st.markdown("""
    * 🟢 **0 - 4** : Risiko Rendah (Stabil)
    * 🟡 **5 - 6** : Risiko Sedang (Waspada)
    * 🟠 **7 - 8** : Risiko Tinggi
    * 🔴 **>= 9** : Status Kritis
    """)

if p['status'] == "KRITIS":
    st.error("🚨 EMERGENCY! Terjadi perburukan klinis hebat (Syok Sepsis). Bunyi alarm diaktifkan!")
    st.audio("https://www.soundjay.com/buttons/sounds/alarm-clock-elapsed-01.mp3", autoplay=True)

if st.session_state.berjalan and st.session_state.indeks_simulasi < 3:
    time.sleep(4)  
    st.session_state.indeks_simulasi += 1
    st.rerun()
