import streamlit as st
import joblib
import time
import requests
import json
import numpy as np

st.markdown("""
    <style>
    .progress-container {
        background: #444;
        border-radius: 8px;
        width: 100%;
        height: 20px;
        overflow: hidden;
        margin-bottom: 12px;
    }

    .progress-bar {
        height: 100%;
        border-radius: 8px;
        background: linear-gradient(90deg,#00ffcc,#0099ff);
        transition: width 1s ease-in-out;
    }
    .progress-label {
        color: #ffd700;
        font-weight: bold;
        margin-bottom: 5px;
        display: block;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Selamat Datang di Quiz Prediksi Jenis Pembalap Kamu!")
st.write("Jawab pertanyaan berikut, agar bisa aku tebak kamu tipikal pembalap Endurance, Rally, atau Nascar!")

def get_ai_response(messages_payload):
    if 'API_KEY' in st.secrets:
        api_key = st.secrets['API_KEY']
    else:
        st.error("API Key tidak ditemukan!")
    time.sleep(2)
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        data=json.dumps({
            "model": "deepseek/deepseek-chat-v3.1:free",
            "messages": messages_payload,
            "max_tokens": 3000,
            "temperature": 0.7,
        })
    )
    if response.status_code == 200:
        answer = response.json()["choices"][0]["message"]["content"]
        return answer
    else:
        if response.status_code == 401:
            st.error("API key tidak valid atau sudah kadaluarsa. Periksa kembali API Key Anda.")
            return None
        if response.status_code == 429:
            st.error("Anda mengalami rate limit atau kuota API. Mohon tunggu lagi dalam beberapa detik/menit.")
            return None
        if response.status_code >= 400:
            st.error(f"Error {response.status_code}: {response.text}")
            return None

nama = st.text_input("Masukkan Nama Kamu:")
st.markdown("""
            <h3>Pertanyaan 1</h3>
            """,
            unsafe_allow_html=True)
pertanyaan1 = st.slider("Berapa kecepatan maksimal yang kamu sukai saat mengemudi?", 0.00, 100.00)
st.markdown("""
            <h3>Pertanyaan 2</h3>
            """,
            unsafe_allow_html=True)
pertanyaan2 = st.slider("Berapa umur kamu?", 20, 60)
st.markdown("""
            <h3>Pertanyaan 3</h3>
            """,
            unsafe_allow_html=True)
pertanyaan3 = st.slider("Berapa persentase kesiapan kamu dalam berkendara di jalanan?", 0, 100)
st.markdown("""
            <h3>Pertanyaan 4</h3>
            """,
            unsafe_allow_html=True)
pertanyaan4 = st.slider("Berapa resiko kamu terkena kecelakaan dalam perjalanan?", 0.00, 5.00)
st.markdown("""
            <h3>Pertanyaan 5</h3>
            """,
            unsafe_allow_html=True)
pertanyaan5 = st.slider("Berapa lama kamu menghabiskan waktu saat berkendara (per minggu)?", 1, 7)
st.markdown("""
            <h3>Pertanyaan 6</h3>
            """,
            unsafe_allow_html=True)
pertanyaan6 = st.slider("Berapa rating pengetahuan kamu tentang mobil?", 0.00, 5.00)
st.markdown("""
            <h3>Pertanyaan 7</h3>
            """,
            unsafe_allow_html=True)
pertanyaan7 = st.radio("Apa tipe jalanan kamu saat berkendara?",
    ["Berkelok-kelok", "Putaran Pendek", "Terjal dan Bergelombang"])
st.markdown("""
            <h3>Pertanyaan 8</h3>
            """,
            unsafe_allow_html=True)
pertanyaan8 = st.radio("Apa merek mobil favoritmu?",
    ["Toyota", "Chevrolet", "Lancia", "Mitsubishi", "BMW", "Mercedes-Benz"])
st.markdown("""
            <h3>Pertanyaan 9</h3>
            """,
            unsafe_allow_html=True)
pertanyaan9 = st.radio("Apa Kepribadian kamu saat berkendara?", 
    ["Berani", "Adaptif", "Presisi", "Disiplin", "Fokus", "Strategis"])

if nama == "":
    st.warning("Silakan masukkan nama kamu untuk memulai kuis.")
    st.stop()

class Pembalap:
    def __init__(self, nama, kecepatan, umur, pengalaman, resiko, durasi, pengetahuan, tipe_jalanan, mobil_favorit, kepribadian):
        self.nama = nama
        self.kecepatan = kecepatan
        self.umur = umur
        self.pengalaman = pengalaman
        self.resiko = resiko
        self.durasi = durasi
        self.pengetahuan = pengetahuan
        self.tipe_jalanan = tipe_jalanan
        self.mobil_favorit = mobil_favorit
        self.kepribadian = kepribadian

    def to_input_array(self, label_mapping, ordered_cols):
        raw_input = {
            "Kecepatan_Rata2": self.kecepatan,
            "Umur_Pengendara": self.umur,
            "Pengalaman_Pengendara": self.pengalaman,
            "Resiko_Kecelakaan": self.resiko,
            "Durasi_Perjalanan": self.durasi,
            "Pengetahuan_Mobil": self.pengetahuan,
            "Tipe_Jalanan": self.tipe_jalanan,
            "Mobil_Favorit": self.mobil_favorit,
            "Kepribadian": self.kepribadian
        }
        for col, mapping in label_mapping.items():
            if col in raw_input:
                val = raw_input[col]
                raw_input[col] = mapping.get(val, -1)
        return np.array([[raw_input[col] for col in ordered_cols]])

if st.button("Submit"):

    model = joblib.load('model.pkl')
    label = joblib.load("labeling.pkl")
    ordered_cols = [
        "Kecepatan_Rata2","Umur_Pengendara","Pengalaman_Pengendara",
        "Resiko_Kecelakaan","Durasi_Perjalanan","Pengetahuan_Mobil",
        "Tipe_Jalanan","Mobil_Favorit","Kepribadian"
    ]

    pembalap = Pembalap(
        nama,
        pertanyaan1, pertanyaan2, pertanyaan3, pertanyaan4,
        pertanyaan5, pertanyaan6, pertanyaan7, pertanyaan8, pertanyaan9
    )

    input_array = pembalap.to_input_array(label, ordered_cols)
    prediction = model.predict(input_array)
    proba = model.predict_proba(input_array)[0]
    class_names = ["Endurance", "Rally", "Nascar"]
    
    st.markdown("### Hasil Prediksi")
    st.markdown("**Probabilitas Prediksi:**")

    colors = ['#00ffcc', '#ff4444', '#0099ff']  

    for cls, p, color in zip(["Endurance", "Rally", "Nascar"], proba, colors):
        persen = p * 100
        st.markdown(f"""
            <div style="margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span style="font-weight: bold;">{cls}</span>
                    <span>{persen:.2f}%</span>
                </div>
                <div class="progress-container">
                    <div class="progress-bar" style="width:{persen:.2f}%; background: {color};"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    if prediction[0] == 0:
        hasil = "Endurance"
        prompt = [
            {"role": "system", "content": "Kamu adalah asisten yang sangat ahli dalam menjelaskan tipe pembalap Endurance."},
            {"role": "user", "content": f"Saya adalah tipe pembalap Endurance. Jelaskan secara detail karakteristik, gaya mengemudi, mobil favorit, pembalap yang aktif, dan keunggulan tipe pembalap Endurance."}
        ]
        deskripsi = get_ai_response(prompt)
        gambar = "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExOW81MzNuc3p3ZmMzOXgxMm10c294OXRoc3V2OGxyc3B0M2JxcHZxcyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/tiJ2ZG86IC7p6/giphy.gif"  
    elif prediction[0] == 1:
        hasil = "Rally"
        prompt = [
            {"role": "system", "content": "Kamu adalah asisten yang sangat ahli dalam menjelaskan tipe pembalap Rally."},
            {"role": "user", "content": f"Saya adalah tipe pembalap Rally. Jelaskan secara detail karakteristik, gaya mengemudi, mobil favorit, pembalap yang aktif, dan keunggulan tipe pembalap Rally."}
        ]
        deskripsi = get_ai_response(prompt)
        gambar = "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExOTRuMjljeDk5NXRibTFpMHYwb29paGFtbmJ2cWVsOXl6YWZ2MDc4ZCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/yflXLFvJHTG36/giphy.gif"
    else:
        hasil = "Nascar"
        prompt = [
            {"role": "system", "content": "Kamu adalah asisten yang sangat ahli dalam menjelaskan tipe pembalap Nascar."},
            {"role": "user", "content": f"Saya adalah tipe pembalap Nascar. Jelaskan secara detail karakteristik, gaya mengemudi, mobil favorit, pembalap yang aktif, dan keunggulan tipe pembalap Nascar."}
        ]
        deskripsi = get_ai_response(prompt)
        gambar = "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExdDN2cTdqb2plZ2diY215bGxjaWJ2c3FibWgwdHVjcnpjaXFpZHVrZyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/XKKa6o1IuDrHxT2QqQ/giphy.gif"
    

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#1f1c2c,#928dab);
                padding:25px;border-radius:20px;color:#fff;">
        <h2 style="text-align:center;color:#ffd700;font-weight:900;-webkit-text-stroke:0.5px #ffaa00;">Halo {nama}!</h2>
        <h3 style="text-align:center;color:#ffd700;">Kamu adalah tipe pembalap: {hasil}</h3>
        <div style="text-align:center;margin-bottom:20px;">
            <img src="{gambar}" alt="{hasil}" 
                style="width:50%;border-radius:15px;box-shadow:0px 4px 20px rgba(0,0,0,0.5);">
        </div>
        <div style="font-size:16px;line-height:1.5;margin-bottom:20px;">
            {deskripsi}
        </div>
    </div>
""", unsafe_allow_html=True)