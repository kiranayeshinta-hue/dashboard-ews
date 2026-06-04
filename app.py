import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time

# Konfigurasi Halaman Dashboard Utama
st.set_page_config(page_title="Central EWS Dashboard", layout="wide")

st.title("🏥 Central Monitoring System - Early Warning Score (EWS)")
st.subheader("Simulasi Real-Time Perburukan Hemodinamik Pasien")
st.markdown("---")

# Inisialisasi tempat penyimpanan data sementara
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=['Waktu', 'Nadi', 'Napas', 'Saturasi', 'Sistolik', 'EWS'])
if 'step' not in st.session_state:
    st.session_state.step = 0

# Tombol Kontrol Jalannya Simulasi
col_ctrl1, col_ctrl2 = st.columns(2)
with col_ctrl1:
    run_sim = st.checkbox("Mulai Monitoring Real-Time (Skenario 30-60 Detik)")
with col_ctrl2:
    if st.button("Reset Simulasi"):
        st.session_state.history = pd.DataFrame(columns=['Waktu', 'Nadi', 'Napas', 'Saturasi', 'Sistolik', 'EWS'])
        st.session_state.step = 0
        st.rerun()

# Logika AI Pembuat Data Dummy (Mensimulasikan Pasien yang Mengalami Perburukan)
if run_sim:
    step = st.session_state.step
    t = pd.Timestamp.now().strftime('%H:%M:%S')
    
    # SKENARIO KLINIS: Pasien perlahan drop dari Stabil -> Warning -> Syok Kritis
    if step < 8:    # Fase 1: Pasien Stabil (Normal)
        nadi = int(np.random.normal(78, 3))
        napas = int(np.random.normal(16, 1))
        spo2 = int(np.random.normal(98, 1))
        sistolik = int(np.random.normal(120, 4))
    elif step < 18: # Fase 2: Mulai Memburuk (Takhikardia & Takhipnea)
        nadi = int(np.random.normal(105, 4))
        napas = int(np.random.normal(22, 1))
        spo2 = int(np.random.normal(93, 1))
        sistolik = int(np.random.normal(104, 5))
    else:           # Fase 3: Kondisi Kritis (Gagal Nafas/Syok Sepsis)
        nadi = int(np.random.normal(132, 4))
        napas = int(np.random.normal(27, 1))
        spo2 = int(np.random.normal(86, 2))
        sistolik = int(np.random.normal(84, 4))
        
    spo2 = min(100, max(40, spo2))
    
    # Perhitungan Skor EWS Otomatis berdasarkan Parameter Klinis Jurnal Kelompok
    ews_score = 0
    if nadi >= 130 or nadi <= 40: ews_score += 3
    elif (111 <= nadi <= 129) or (41 <= nadi <= 50): ews_score += 2
    elif (91 <= nadi <= 110) or (51 <= nadi <= 60): ews_score += 1
    
    if napas >= 25 or napas <= 8: ews_score += 3
    elif 21 <= napas <= 24: ews_score += 2
    elif 9 <= napas <= 11: ews_score += 1
        
    if spo2 < 92: ews_score += 3
    elif 92 <= spo2 <= 93: ews_score += 2
    elif 94 <= spo2 <= 95: ews_score += 1
        
    if sistolik <= 90 or sistolik >= 220: ews_score += 3
    elif 91 <= sistolik <= 100: ews_score += 2
    elif 101 <= sistolik <= 110: ews_score += 1

    # Memasukkan data ke tabel riwayat tren
    new_data = pd.DataFrame([[t, nadi, napas, spo2, sistolik, ews_score]], 
                            columns=['Waktu', 'Nadi', 'Napas', 'Saturasi', 'Sistolik', 'EWS'])
    st.session_state.history = pd.concat([st.session_state.history, new_data], ignore_index=True)
    st.session_state.step += 1

# Tampilan Utama Dashboard jika data sudah mulai berjalan
if not st.session_state.history.empty:
    latest = st.session_state.history.iloc[-1]
    df_hist = st.session_state.history.tail(15)
    
    if latest['EWS'] >= 5:
        bg_color = "#FF4B4B" # Merah Menyala
        text_color = "white"
        status_pasien = "CRITICAL / RISIKO TINGGI (PERBURUKAN HEMODINAMIK)"
        respon_klinis = "⚠️ AKTIVASI CODE BLUE! Laporkan segera ke Dokter DPJP, siapkan resusitasi & pindahkan ke ICU."
    elif 1 <= latest['EWS'] <= 4:
        bg_color = "#FFAA00" # Kuning Warning
        text_color = "black"
        status_pasien = "WARNING / RISIKO SEDANG"
        respon_klinis = "⚡ Tingkatkan frekuensi monitoring berkala (tiap 1-2 jam). Laporkan ke Dokter Jaga Ruangan."
    else:
        bg_color = "#28A745" # Hijau Stabil
        text_color = "white"
        status_pasien = "STABIL / NORMAL"
        respon_klinis = "✅ Lanjutkan monitoring rutin standar keperawatan per shift (minimal tiap 8 jam)."

    st.markdown(f"""
    <div style="background-color:{bg_color}; padding:25px; border-radius:10px; text-align:center;">
        <h1 style="color:{text_color}; margin:0; font-family:sans-serif;">TOTAL SKOR EWS: {latest['EWS']}</h1>
        <h2 style="color:{text_color}; margin:5px 0; font-family:sans-serif;">STATUS: {status_pasien}</h2>
        <h4 style="color:{text_color}; margin:5px 0 0 0; font-family:sans-serif;">REKOMENDASI RESPON KLINIS: {respon_klinis}</h4>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>### 📊 Tanda-Tanda Vital Pasien Saat Ini", unsafe_allow_html=True)
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(label="❤️ Denyut Nadi (Heart Rate)", value=f"{latest['Nadi']} bpm")
    m2.metric(label="🫁 Frekuensi Napas (Respiratory Rate)", value=f"{latest['Napas']} x/menit")
    m3.metric(label="🩸 Saturasi Oksigen (SpO2)", value=f"{latest['Saturasi']} %")
    m4.metric(label="📉 Tekanan Darah (Sistolik)", value=f"{latest['Sistolik']} mmHg")
    
    st.markdown("---")
    st.markdown("### 📈 Tren Grafik Parameter Dinamis (Monitoring Berkelanjutan)")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_hist['Waktu'], y=df_hist['Nadi'], name="Nadi (HR)", line=dict(color='#FF4B4B', width=3)))
    fig.add_trace(go.Scatter(x=df_hist['Waktu'], y=df_hist['Napas'], name="Napas (RR)", line=dict(color='#0066FF', width=3)))
    fig.add_trace(go.Scatter(x=df_hist['Waktu'], y=df_hist['Saturasi'], name="Saturasi (SpO2)", line=dict(color='#28A745', width=3)))
    fig.add_trace(go.Scatter(x=df_hist['Waktu'], y=df_hist['Sistolik'], name="Sistolik BP", line=dict(color='#800080', width=3)))
    
    fig.update_layout(height=380, margin=dict(l=20, r=20, t=10, b=20), legend_orientation="h")
    st.plotly_chart(fig, use_container_width=True)

    if run_sim and st.session_state.step < 30:
        time.sleep(1.5)
        st.rerun()
else:
    st.info("💡 Silakan centang kotak 'Mulai Monitoring Real-Time' di atas untuk melihat visualisasi pergerakan data pasien.")