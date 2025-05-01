import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime
import threading
import time
import io

# Konfigurasi halaman utama
st.set_page_config(page_title="Kalkulator & Tracker BMI", layout="centered")

# Sidebar navigasi
st.sidebar.title("🏠 Navigasi")
halaman = st.sidebar.radio("Pilih Halaman", ["Kalkulator BMI", "Histori BMI", "Dashboard Mini", "Analisis Tambahan Tubuh"])

st.write("### 📅 Jadwal Cek BMI")

interval = st.slider("Pilih interval cek ulang (hari):", min_value=3, max_value=30, value=7)

def cek_jadwal_ulang(histori_df, interval_hari):
    if len(histori_df) == 0:
        return "⚠️ Belum ada data BMI sebelumnya."
    histori_df["Waktu"] = pd.to_datetime(histori_df["Waktu"])
    terakhir = histori_df["Waktu"].max()
    sekarang = datetime.datetime.now()
    selisih = sekarang - terakhir

    if selisih.days >= interval_hari:
        return f"⚠️ Sudah {selisih.days} hari sejak cek terakhir.\n💡 Waktunya cek ulang BMI!"
    else:
        cek_berikutnya = terakhir + datetime.timedelta(days=interval_hari)
        return f"✅ Terakhir dicatat {selisih.days} hari lalu.\n📆 Cek selanjutnya: {cek_berikutnya.strftime('%d %B %Y')}"

if os.path.exists("histori_bmi.csv"):
    df_histori = pd.read_csv("histori_bmi.csv")
    pesan_cek = cek_jadwal_ulang(df_histori, interval)
    st.info(pesan_cek)
    
def rekomendasi_bmi(kategori):
    if kategori == "Kurus":
        return """💡 *Rekomendasi untuk kategori Kurus*:
- Konsumsi makanan tinggi protein dan kalori sehat (nasi merah, alpukat, telur, daging tanpa lemak).
- Tambahkan cemilan sehat (kacang, smoothies).
- Lakukan latihan kekuatan (push-up, squat, angkat beban ringan).
- Periksa kondisi kesehatan jika sulit naik berat badan."""
    elif kategori == "Normal (Ideal)":
        return """💡 *Rekomendasi untuk kategori Ideal*:
- Pertahankan pola makan seimbang (sayur, buah, protein, karbohidrat kompleks).
- Olahraga teratur minimal 3–4 kali per minggu (jalan cepat, lari ringan, yoga).
- Cukup tidur dan kurangi stres.
- Hindari perubahan berat drastis."""
    elif kategori == "Berat Badan Berlebih":
        return """💡 *Rekomendasi untuk kategori Berat Badan Berlebih*:
- Kurangi konsumsi gula dan lemak jenuh.
- Perbanyak sayuran, air putih, dan buah.
- Mulai olahraga ringan (berjalan, berenang) dan tingkatkan perlahan.
- Catat asupan kalori harian untuk pemantauan."""
    else:  # Obesitas
        return """💡 *Rekomendasi untuk kategori Obesitas*:
- Konsultasi ke ahli gizi jika memungkinkan.
- Fokus pada defisit kalori sehat (hindari diet ekstrem).
- Olahraga low-impact (aqua gym, yoga, sepeda statis).
- Prioritaskan tidur cukup dan manajemen stres."""

# ===========================
# 1. HALAMAN KALKULATOR BMI
# ===========================
if halaman == "Kalkulator BMI":
    st.title("🧮 Kalkulator Indeks Massa Tubuh (BMI)")

    st.write("## Masukkan Data Anda")
    col1, col2 = st.columns(2)
    with col1:
        berat_badan = st.number_input("Berat Badan (kg)", min_value=0.0, value=1.0, step=0.1)
        gender = st.selectbox("Jenis Kelamin", options=["Laki-laki", "Perempuan"])
    with col2:
        tinggi_badan = st.number_input("Tinggi Badan (cm)", min_value=0.0, value=1.0, step=0.1)
        kondisi = st.selectbox("Kondisi Khusus", options=["Tidak Ada", "Atlet", "Ibu Hamil"])

    # Hitung BMI
    if tinggi_badan > 0:
        tinggi_meter = tinggi_badan / 100
        bmi = berat_badan / (tinggi_meter ** 2)
    else:
        bmi = 0

    # Kategori BMI
    def kategori_bmi(bmi, gender, kondisi):
        if kondisi == "Atlet":
            return "BMI tidak akurat untuk atlet"
        if kondisi == "Ibu Hamil":
            return "BMI tidak berlaku untuk ibu hamil"
        if gender == "Perempuan":
            if bmi < 18.0:
                return "Kurus"
            elif bmi < 24.0:
                return "Normal (Ideal)"
            elif bmi < 29.0:
                return "Berat Badan Berlebih"
            else:
                return "Obesitas"
        else:
            if bmi < 18.5:
                return "Kurus"
            elif bmi < 25:
                return "Normal (Ideal)"
            elif bmi < 30:
                return "Berat Badan Berlebih"
            else:
                return "Obesitas"

    kategori = kategori_bmi(bmi, gender, kondisi)

    # Berat Ideal
    bmi_target = 22 if gender == "Laki-laki" else 21.5
    berat_ideal = bmi_target * (tinggi_meter ** 2)
    selisih = berat_badan - berat_ideal

    # Tampilkan hasil
    st.subheader("📊 Hasil Perhitungan")
    col1, col2 = st.columns(2)
    col1.metric("BMI Anda", f"{bmi:.2f}")
    col2.metric("Kategori", kategori)

    st.info(f"Berat ideal Anda seharusnya sekitar **{berat_ideal:.1f} kg**.")
    if kategori in ["Berat Badan Berlebih", "Obesitas"]:
        st.warning(f"Anda disarankan menurunkan berat badan sekitar **{selisih:.1f} kg**.")
        
    st.write("### 🍽️ Rekomendasi Gaya Hidup")
    saran = rekomendasi_bmi(kategori)
    st.markdown(saran)

    # Grafik BMI
    st.write("## 📉 Grafik Posisi BMI Anda")
    fig, ax = plt.subplots(figsize=(10, 2))
    ax.axvspan(10, 18.5, color="lightblue", alpha=0.5, label="Kurus")
    ax.axvspan(18.5, 24.9, color="lightgreen", alpha=0.5, label="Normal")
    ax.axvspan(25, 29.9, color="gold", alpha=0.5, label="Berat Berlebih")
    ax.axvspan(30, 40, color="salmon", alpha=0.5, label="Obesitas")
    ax.axvline(bmi, color="black", linestyle="--", linewidth=5)
    ax.set_xlim(10, 40)
    ax.set_yticks([])
    ax.set_xlabel("BMI")
    ax.set_title("Posisi BMI Anda")
    ax.legend()
    st.pyplot(fig)

    # Export grafik
    if st.button("💾 Simpan Grafik sebagai Gambar"):
        fig.savefig("grafik_bmi.png")
        st.success("Grafik berhasil disimpan sebagai `grafik_bmi.png` di folder yang sama.")

    # Simpan histori ke file CSV
    data = {
        "Waktu": [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        "Berat (kg)": [berat_badan],
        "Tinggi (cm)": [tinggi_badan],
        "Gender": [gender],
        "Kondisi": [kondisi],
        "BMI": [round(bmi, 2)],
        "Kategori": [kategori],
    }
    df_baru = pd.DataFrame(data)
    if os.path.exists("histori_bmi.csv"):
        df_lama = pd.read_csv("histori_bmi.csv")
        df = pd.concat([df_lama, df_baru], ignore_index=True)
    else:
        df = df_baru
    df.to_csv("histori_bmi.csv", index=False)
    
    # Di dalam halaman Kalkulator BMI, setelah menyimpan histori dan membuat dataframe df
    # Tambahkan fitur ekspor Excel dan download grafik

    st.write("## 📤 Ekspor & Unduh Data")

    # Ekspor ke Excel
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Histori BMI')
        writer.close()
        st.download_button(
            label="⬇️ Unduh Histori BMI (Excel)",
            data=buffer.getvalue(),
            file_name="histori_bmi.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # Simpan grafik sebagai gambar lalu tampilkan tombol unduh
    grafik_buffer = io.BytesIO()
    fig.savefig(grafik_buffer, format='png')
    st.download_button(
        label="🖼️ Unduh Grafik BMI Anda (PNG)",
        data=grafik_buffer.getvalue(),
        file_name="grafik_bmi.png",
        mime="image/png"
    )

    st.write("### 📊 Grafik Perbandingan BMI dan Standar WHO")

    # Data standar WHO
    bmi_kategori = {
        "Kurus": 18.5,
        "Normal": 24.9,
        "Berlebih": 29.9,
        "Obesitas": 35
    }

    fig, ax = plt.subplots()
    kategori_labels = list(bmi_kategori.keys())
    nilai_batas = list(bmi_kategori.values())

    # Tambahkan BMI pengguna
    kategori_labels.append("BMI Anda")
    nilai_batas.append(bmi)

    bar_colors = ['skyblue', 'lightgreen', 'orange', 'red', 'purple']

    ax.bar(kategori_labels, nilai_batas, color=bar_colors)
    ax.axhline(y=bmi, color='purple', linestyle='--', label=f'BMI Anda: {bmi:.2f}')
    ax.set_ylabel('Nilai BMI')
    ax.set_title('Perbandingan BMI Anda dengan Standar WHO')
    ax.legend()

    st.pyplot(fig)


# ===========================
# 2. HALAMAN HISTORI BMI
# ===========================
elif halaman == "Histori BMI":
    st.title("📜 Riwayat BMI Anda")
    if os.path.exists("histori_bmi.csv"):
        df = pd.read_csv("histori_bmi.csv")
        st.dataframe(df, use_container_width=True)

        st.write("## 📈 Grafik Perkembangan BMI")
        fig, ax = plt.subplots()
        df["Waktu"] = pd.to_datetime(df["Waktu"])
        df = df.sort_values("Waktu")
        ax.plot(df["Waktu"], df["BMI"], marker='o')
        ax.set_title("Perubahan BMI dari Waktu ke Waktu")
        ax.set_ylabel("BMI")
        ax.set_xlabel("Tanggal")
        ax.grid(True)
        st.pyplot(fig)
    else:
        st.warning("Belum ada data histori. Silakan isi data di halaman 'Kalkulator BMI'.")

# ===========================
# 3. HALAMAN DASHBOARD MINI
# ===========================
elif halaman == "Dashboard Mini":
    st.title("📊 Dashboard Mini BMI")

    if os.path.exists("histori_bmi.csv"):
        df = pd.read_csv("histori_bmi.csv")
        rata2_bmi = df["BMI"].mean()
        terakhir = df.iloc[-1]
        jumlah_data = len(df)

        st.subheader("📌 Ringkasan")
        col1, col2, col3 = st.columns(3)
        col1.metric("Rata-rata BMI", f"{rata2_bmi:.2f}")
        col2.metric("Terakhir", f"{terakhir['BMI']} ({terakhir['Kategori']})")
        col3.metric("Jumlah Catatan", jumlah_data)

        st.subheader("🔎 Tren BMI")
        fig, ax = plt.subplots()
        df["Waktu"] = pd.to_datetime(df["Waktu"])
        ax.plot(df["Waktu"], df["BMI"], marker="o")
        ax.set_title("Tren BMI Anda")
        ax.set_ylabel("BMI")
        ax.grid(True)
        st.pyplot(fig)
    else:
        st.info("Data belum tersedia. Masukkan data terlebih dahulu di halaman Kalkulator BMI.")
        

# ===========================
# 4. Fitur Tambahan: BMR, TDEE, Persentase Lemak Tubuh, WHR
# ===========================
elif halaman == "Analisis Tambahan Tubuh":
    st.title("Analisis Tambahan Tubuh")
    
    st.write("## Masukkan Data Anda")
    st.write("Hitung BMR, TDEE, Lemak Tubuh, WHR")
    st.write("Basal Metabolic Rate (BMR) adalah jumlah kalori yang dibutuhkan tubuh untuk menjalankan fungsi dasar tubuh saat istirahat.")
    st.write("Total Daily Energy Expenditure (TDEE) adalah jumlah total energi atau kalori yang dibakar tubuh dalam sehari")
    st.write("Waist-to-Hip Ratio (WHR) atau dikenal sebagai Rasio Lingkar Pinggang terhadap Pinggul, untuk menentukan proporsi lemak tubuh yang terdistribusi")    
    
    col1, col2 = st.columns(2)
    with col1:
        berat_badan_input = st.number_input("Berat (kg)", min_value=0.0, value=0.0, step=0.1)
        tinggi_badan_input = st.number_input("Tinggi (cm)", min_value=0.0, value=0.0, step=0.1)
        usia = st.number_input("Usia (tahun)", min_value=0, value=0, step=1)
        gender_input = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"], key="gender_input")
    with col2:
        aktivitas = st.selectbox("Tingkat Aktivitas", ["Sedentari", "Ringan", "Sedang", "Berat", "Ekstrem"])
        lingkar_pinggang = st.number_input("Lingkar Pinggang (cm)", min_value=0.0, value=0.0, step=0.1)
        lingkar_leher = st.number_input("Lingkar Leher (cm)", min_value=0.0, value=0.0, step=0.1)
        lingkar_pinggul = None
    
    st.write("Petunjuk Cara Mengukur Lingkar Pinggang dan Pinggul:")
    st.write("**Lingkar Pinggang**: Ukur di titik terkecil antara tulang rusuk dan panggul, atau tepat di atas pusar")
    st.write("**Lingkar Panggul**: Ukur di titik terlebar bokong")
    
    st.write("Keterangan Kategori Aktivitas:")
    st.write("- Sedentari (kerja kantoran/minim gerak)")
    st.write("- Ringan (1-3 hari olahraga/minggu)")
    st.write("- Sedang (3-5 hari olahraga/minggu)")
    st.write("- Berat (6-7 hari/rutin olahraga setiap hari)")
    st.write("- Ekstrem (Atlet profesional atau dua kali latihan per hari))")
    
    if gender_input == "Perempuan":
        lingkar_pinggul = st.number_input("Lingkar Pinggul (cm)", min_value=0, value=0.0, step=0.1)
            
    tujuan_kalori = st.selectbox("Tujuan Kalori Harian", ["Pertahankan Berat Badan", "Penurunan Berat Badan (Defisit 500 kkal)", "Kenaikan Massa (Surplus 500 kkal)"])

    if st.button("Hitung Analisis Tubuh"):
        try: 
            if berat_badan_input <= 0 or tinggi_badan_input <= 0 or usia <= 0:
                raise ValueError("Input berat, tinggi, dan usia harus lebih dari 0")
                
            # BMR
            if gender_input == "Laki-laki":
                bmr = 10 * berat_badan_input + 6.25 * tinggi_badan_input - 5 * usia + 5
            else: # Perempuan
                bmr = 10 * berat_badan_input + 6.25 * tinggi_badan_input - 5 * usia - 161

            # TDEE multiplier
            aktivitas_dict = {
                "Sedentari": 1.2,
                "Ringan": 1.375,
                "Sedang": 1.55,
                "Berat": 1.725,
                "Ekstrem": 1.9
            }
            tdee = bmr * aktivitas_dict[aktivitas]
                
            # Kalori sesuai tujuan
            if tujuan_kalori == "Pertahankan Berat Badan":
                kalori_harian = tdee
            elif tujuan_kalori == "Penurunan Berat Badan (Defisit 500 kkal)":
                kalori_harian = tdee - 500
            else:
                kalori_harian = tdee + 500

            # Persentase lemak tubuh
            if gender_input == "Laki-laki":
                body_fat = 495 / (1.0324 - 0.19077 * (np.log10(lingkar_pinggang - lingkar_leher)) + 0.15456 * (np.log10(tinggi_badan_input))) - 450
            else: # Perempuan
                body_fat = 495 / (1.29579 - 0.35004 * (np.log10(lingkar_pinggang + lingkar_pinggul - lingkar_leher)) + 0.221 * (np.log10(tinggi_badan_input))) - 450

            # WHR
            if gender_input == "Perempuan" and lingkar_pinggul != 0:
                whr = lingkar_pinggang / lingkar_pinggul
            elif gender_input == "Laki-laki":
                whr = lingkar_pinggang / (lingkar_pinggul if lingkar_pinggul else lingkar_pinggang)
            else:
                whr = 0
                    
            # Interpretasi WHR
            risiko = ""
            if gender_input == "Laki-laki":
                if whr >= 0.90:
                    risiko = "Risiko tinggi penyakit kardiovaskular"
                else:
                    risiko = "Normal"
            else:
                if whr >= 0.85:
                    risiko = "Risiko tinggi penyakit kardiovaskular"
                else:
                    risiko = "Normal"

            st.subheader("Hasil Analisis Tambahan")
            st.write(f"**BMR:** {bmr:.2f} kkal/hari")
            st.write(f"**TDEE:** {tdee:.2f} kkal/hari")
            st.write(f"**Kalori Harian sesuai Tujuan:** {kalori_harian:.2f} kkal")
            st.write(f"**Persentase Lemak Tubuh:** {body_fat:.2f}%")
            st.write(f"**WHR (Waist-to-Hip Ratio):** {whr:.2f} → {risiko}")
                
            # Grafik komparatif lemak tubuh
            fig, ax = plt.subplots(figsize=(5,3))
            kategori = ["Lemak Tubuh Anda", "Rata-rata Ideal"]
            nilai = [body_fat, 18 if gender_input == "Laki-laki" else 25]
            warna = ['orange', 'green']
            ax.bar(kategori, nilai, color=warna)
            ax.set_ylabel("Persentase %")
            ax.set_title("Perbandingan Lemak Tubuh")
            st.pyplot(fig)
                
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")

# ===========================
# SETTING FITUR LANJUTAN: RESET & PENGATURAN
# ===========================
st.sidebar.title("⚙️ Pengaturan")

# Fitur reset histori BMI
with st.sidebar.expander("🔁 Reset / Hapus Histori BMI"):
    if st.button("🗑️ Hapus Semua Histori BMI"):
        if os.path.exists("histori_bmi.csv"):
            os.remove("histori_bmi.csv")
            st.success("Histori BMI berhasil dihapus.")
        else:
            st.warning("Belum ada histori untuk dihapus.")

# Pengaturan nilai default input berat & tinggi
with st.sidebar.expander("⚙️ Pengaturan Input Default"):
    default_berat = st.number_input("Berat default (kg)", min_value=0.0, value=0.0, key="default_berat_input")
    default_tinggi = st.number_input("Tinggi default (cm)", min_value=0.0, value=0.0, key="default_tinggi_input")

