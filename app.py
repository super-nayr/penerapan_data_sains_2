import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
import os

# Set page config - harus menjadi perintah Streamlit pertama
st.set_page_config(
    page_title="Analisis Prediktif Status Mahasiswa",
    page_icon="✨",
    layout="wide"
)

# --- INFORMASI DI SIDEBAR ---
# Menghapus foto dan hanya menampilkan informasi teks di sidebar
st.sidebar.title("Tentang Sistem Ini")
st.sidebar.info(
    """
    Sistem ini menggunakan model Machine Learning (XGBoost) untuk menganalisis dan memprediksi 
    potensi dropout seorang mahasiswa berdasarkan data historis. 
    
    Tujuannya adalah untuk memberikan intervensi dini dan dukungan yang tepat sasaran.
    """
)
st.sidebar.markdown("---")
st.sidebar.markdown("Dibuat dengan ❤️ oleh **Imnayr**")


# --- CUSTOM CSS UNTUK TAMPILAN ELEGAN ---
st.markdown("""
    <style>
        /* Mengubah font utama */
        html, body, [class*="st-"] {
            font-family: 'Source Sans Pro', sans-serif;
        }

        /* Background utama */
        .main { 
            background-color: #0E1117; /* Warna dasar dark mode Streamlit */
            color: #FAFAFA;
        }

        /* Styling header */
        h1, h2, h3, h4, h5 {
            color: #FAFAFA;
        }
        
        /* Styling expander sebagai "card" */
        [data-testid="stExpander"] {
            background-color: #262730;
            border-radius: 10px;
            border: 1px solid #41444f;
            margin-bottom: 15px;
        }

        /* Styling tombol submit */
        .stButton>button {
            border: 2px solid #00A9B7;
            border-radius: 10px;
            background-color: transparent;
            color: #00A9B7;
            font-weight: bold;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            background-color: #00A9B7;
            color: white;
        }

        /* Styling kotak hasil prediksi */
        .prediction-box {
            padding: 25px;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-top: 10px;
            border-width: 2px;
            border-style: solid;
        }
        .high-risk {
            background-color: #4a2121;
            border-color: #EF5350;
        }
        .low-risk {
            background-color: #1e3b30;
            border-color: #66BB6A;
        }
        .prediction-box h3 {
            color: white;
            margin-bottom: 10px;
        }
        .prediction-box p {
            font-size: 16px;
            color: #d1d1d1;
        }
    </style>
""", unsafe_allow_html=True)

# --- FUNGSI PEMUATAN MODEL ---
@st.cache_resource
def load_artifacts():
    model_path = 'model_dropout_xgboost.pkl'
    scaler_path = 'scaler.pkl'
    
    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        st.error(f"File tidak ditemukan. Pastikan '{model_path}' dan '{scaler_path}' ada di folder yang sama.")
        return None, None
        
    try:
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        return model, scaler
    except Exception as e:
        st.error(f"Gagal memuat model atau scaler: {e}")
        return None, None

model, scaler = load_artifacts()

# --- JUDUL APLIKASI ---
st.title("✨ Analisis Prediktif Status Mahasiswa")
st.markdown("##### Sistem Cerdas Berbasis Machine Learning untuk Intervensi Dini")
st.markdown("---")


# --- FORM INPUT ---
if model and scaler:
    with st.form("prediction_form"):
        st.header("📝 Formulir Data Mahasiswa")

        col1, col2 = st.columns(2, gap="large")

        with col1:
            with st.expander("📋 Informasi Dasar Mahasiswa", expanded=True):
                marital_status_mapping = {
                    "Lajang (Single)": 1, "Menikah (Married)": 2, "Duda/Janda (Widower)": 3,
                    "Bercerai (Divorced)": 4, "Hidup Bersama (Facto union)": 5, "Pisah Resmi (Legally separated)": 6,
                }
                marital_status = st.selectbox("Status Pernikahan", options=list(marital_status_mapping.keys()))

                gender_mapping = {"Pria (Male)": 1, "Wanita (Female)": 0}
                gender = st.selectbox("Jenis Kelamin", options=list(gender_mapping.keys()))
                
                age_at_enrollment = st.number_input("Usia Saat Pendaftaran", min_value=17, max_value=70, value=20)
                
                daytime_evening_attendance_mapping = {"Kuliah Siang (Daytime)": 1, "Kuliah Malam (Evening)": 0}
                daytime_evening_attendance = st.selectbox("Waktu Kehadiran", options=list(daytime_evening_attendance_mapping.keys()))
            
            with st.expander("🎓 Kualifikasi & Latar Belakang"):
                previous_qualification_mapping = {
                    "Pendidikan Menengah (Secondary education)": 1, "Sarjana (Bachelor's degree)": 2, "Gelar (Degree)": 3,
                    "Magister (Master's)": 4, "Doktor (Doctorate)": 5, "Pernah Kuliah (Frequency of higher education)": 6,
                    "Kelas 12 Belum Selesai": 9, "Kelas 11 Belum Selesai": 10, "Lainnya - Kelas 11": 12,
                    "Pendidikan Dasar Siklus 3": 19, "Kursus Spesialisasi Teknologi": 39, "Kursus Teknis Profesional Tinggi": 42
                }
                previous_qualification = st.selectbox("Kualifikasi Pendidikan Sebelumnya", options=list(previous_qualification_mapping.keys()))
                previous_qualification_grade = st.number_input("Nilai Kualifikasi Sebelumnya", min_value=0.0, max_value=200.0, value=120.0)
                
                occupation_mapping = {
                    "Tidak Tersedia": 0, "Eksekutif & Manajer": 1, "Profesional": 2, "Teknisi & Asosiasi Profesional": 3,
                    "Staf Administrasi": 4, "Jasa Pribadi, Perlindungan, Keamanan": 5, "Penjual": 6,
                    "Petani & Pekerja Terampil di Pertanian": 7, "Pekerja Terampil di Industri, Konstruksi, Pengrajin": 8,
                    "Operator Mesin & Pekerja Rakitan": 9, "Pekerja Tidak Terampil": 10, "Situasi Lain": 90
                }
                mothers_occupation = st.selectbox("Pekerjaan Ibu", options=list(occupation_mapping.keys()), index=4)
                fathers_occupation = st.selectbox("Pekerjaan Ayah", options=list(occupation_mapping.keys()), index=4)

        with col2:
            with st.expander("📚 Informasi Akademik & Pendaftaran", expanded=True):
                course_mapping = {
                    "Teknologi Produksi Biofuel": 33, "Desain Animasi dan Multimedia": 171, "Ilmu Sosial (Malam)": 8014,
                    "Agronomi": 9003, "Desain Komunikasi": 9070, "Keperawatan Hewan": 9085, "Teknik Informatika": 9119,
                    "Equinokultur": 9130, "Manajemen": 9147, "Ilmu Sosial": 9238, "Pariwisata": 9254,
                    "Keperawatan": 9500, "Kesehatan Gigi": 9556, "Manajemen Periklanan dan Pemasaran": 9670,
                    "Jurnalisme dan Komunikasi": 9773, "Pendidikan Dasar": 9853, "Manajemen (Malam)": 9991
                }
                course = st.selectbox("Program Studi", options=list(course_mapping.keys()), index=6)
                application_mode = st.number_input("Mode Pendaftaran (Kode)", min_value=0, value=1)
                application_order = st.number_input("Urutan Pilihan Jurusan", min_value=0, max_value=9, value=1)
                admission_grade = st.number_input("Nilai Masuk", min_value=0.0, max_value=200.0, value=125.0)

            with st.expander("📈 Data Perkuliahan (Semester 1 & 2)"):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Semester 1**")
                    curricular_units_1st_sem_enrolled = c1.number_input("SKS Diambil", key="s1_enrolled", min_value=0, value=6)
                    curricular_units_1st_sem_approved = c1.number_input("SKS Lulus", key="s1_approved", min_value=0, value=6)
                    curricular_units_1st_sem_grade = c1.number_input("Rata-rata Nilai", key="s1_grade", min_value=0.0, max_value=20.0, value=14.0)
                    curricular_units_1st_sem_credited = c1.number_input("SKS Disetarakan", key="s1_credited", min_value=0, value=0)
                    curricular_units_1st_sem_without_evaluations = c1.number_input("SKS Tanpa Evaluasi", key="s1_no_eval", min_value=0, value=0)
                with c2:
                    st.markdown("**Semester 2**")
                    curricular_units_2nd_sem_enrolled = c2.number_input("SKS Diambil", key="s2_enrolled", min_value=0, value=6)
                    curricular_units_2nd_sem_approved = c2.number_input("SKS Lulus", key="s2_approved", min_value=0, value=6)
                    curricular_units_2nd_sem_grade = c2.number_input("Rata-rata Nilai", key="s2_grade", min_value=0.0, max_value=20.0, value=13.5)
                    curricular_units_2nd_sem_credited = c2.number_input("SKS Disetarakan", key="s2_credited", min_value=0, value=0)
                    curricular_units_2nd_sem_without_evaluations = c2.number_input("SKS Tanpa Evaluasi", key="s2_no_eval", min_value=0, value=0)


        st.markdown("---")
        st.header("Status Finansial & Lainnya")
        fin_col1, fin_col2, fin_col3 = st.columns(3)
        boolean_mapping = {"Tidak": 0, "Ya": 1}
        with fin_col1:
            debtor = st.selectbox("Memiliki Tunggakan?", options=list(boolean_mapping.keys()))
            scholarship_holder = st.selectbox("Penerima Beasiswa?", options=list(boolean_mapping.keys()))
        with fin_col2:
            tuition_fees_up_to_date = st.selectbox("Biaya Kuliah Lancar?", options=list(boolean_mapping.keys()), index=1)
            displaced = st.selectbox("Mahasiswa Pindahan?", options=list(boolean_mapping.keys()))
        with fin_col3:
            educational_special_needs = st.selectbox("Kebutuhan Pendidikan Khusus?", options=list(boolean_mapping.keys()))
            international = st.selectbox("Mahasiswa Internasional?", options=list(boolean_mapping.keys()))
        
        st.markdown("---")
        st.header("Indikator Ekonomi Makro")
        eco_col1, eco_col2, eco_col3 = st.columns(3)
        with eco_col1:
            unemployment_rate = st.number_input("Tingkat Pengangguran (%)", value=12.4)
        with eco_col2:
            inflation_rate = st.number_input("Tingkat Inflasi (%)", value=1.4)
        with eco_col3:
            gdp = st.number_input("GDP", value=1.79)
        
        st.markdown("<br>", unsafe_allow_html=True)
        # Tombol submit di dalam form
        submitted = st.form_submit_button("🚀 Analisis dan Prediksi Sekarang")

    if submitted:
        try:
            # Mengumpulkan semua input ke dalam dictionary
            input_dict = {
                'Marital_Status': marital_status_mapping[marital_status], 'Application_mode': application_mode,
                'Application_order': application_order, 'Course': course_mapping[course],
                'Daytime_evening_attendance': daytime_evening_attendance_mapping[daytime_evening_attendance],
                'Previous_qualification': previous_qualification_mapping[previous_qualification],
                'Previous_qualification_grade': previous_qualification_grade, 'Nacionality': 1, # Asumsi Kewarganegaraan utama
                'Mother_occupation': occupation_mapping[mothers_occupation], 'Father_occupation': occupation_mapping[fathers_occupation],
                'Admission_grade': admission_grade, 'Displaced': boolean_mapping[displaced],
                'Educational_special_needs': boolean_mapping[educational_special_needs],
                'Debtor': boolean_mapping[debtor], 'Tuition_fees_up_to_date': boolean_mapping[tuition_fees_up_to_date],
                'Gender': gender_mapping[gender], 'Scholarship_holder': boolean_mapping[scholarship_holder],
                'Age_at_enrollment': age_at_enrollment, 'International': boolean_mapping[international],
                'Curricular_units_1st_sem_credited': curricular_units_1st_sem_credited,
                'Curricular_units_1st_sem_enrolled': curricular_units_1st_sem_enrolled,
                'Curricular_units_1st_sem_approved': curricular_units_1st_sem_approved,
                'Curricular_units_1st_sem_grade': curricular_units_1st_sem_grade,
                'Curricular_units_1st_sem_without_evaluations': curricular_units_1st_sem_without_evaluations,
                'Curricular_units_2nd_sem_credited': curricular_units_2nd_sem_credited,
                'Curricular_units_2nd_sem_enrolled': curricular_units_2nd_sem_enrolled,
                'Curricular_units_2nd_sem_approved': curricular_units_2nd_sem_approved,
                'Curricular_units_2nd_sem_grade': curricular_units_2nd_sem_grade,
                'Curricular_units_2nd_sem_without_evaluations': curricular_units_2nd_sem_without_evaluations,
                'Unemployment_rate': unemployment_rate, 'Inflation_rate': inflation_rate, 'GDP': gdp
            }
            input_data = pd.DataFrame([input_dict])

            # --- Feature Engineering (Sama persis dengan saat training) ---
            epsilon = 1e-5
            input_data['academic_performance'] = (input_data['Curricular_units_1st_sem_grade'] + input_data['Curricular_units_2nd_sem_grade']) / 2
            input_data['success_ratio'] = (input_data['Curricular_units_1st_sem_approved'] + input_data['Curricular_units_2nd_sem_approved']) / \
                                          (input_data['Curricular_units_1st_sem_enrolled'] + input_data['Curricular_units_2nd_sem_enrolled'] + epsilon)
            input_data['student_age'] = input_data['Age_at_enrollment']
            input_data['has_debt'] = input_data['Debtor']
            input_data['has_scholarship'] = input_data['Scholarship_holder']
            input_data['fees_updated'] = input_data['Tuition_fees_up_to_date']
            
            for col in scaler.feature_names_in_:
                if col not in input_data.columns:
                    input_data[col] = 0
            
            input_data = input_data[scaler.feature_names_in_]
            
            input_data_scaled = scaler.transform(input_data)

            prediction = model.predict(input_data_scaled)
            probability_dropout = model.predict_proba(input_data_scaled)[0][1]

            # --- TAMPILAN HASIL PREDIKSI YANG ELEGAN ---
            st.markdown("---")
            st.header("📊 Hasil Analisis Prediktif")
            
            col_res1, col_res2 = st.columns([1, 1.2], gap="large")
            
            with col_res1:
                if prediction[0] == 1:
                    st.markdown(f"""
                        <div class='prediction-box high-risk'>
                            <h3>⚠️ Status: BERISIKO TINGGI DROPOUT</h3>
                            <p>Mahasiswa ini menunjukkan sinyal kuat untuk tidak melanjutkan studi. Perlu adanya intervensi dan dukungan segera.</p>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div class='prediction-box low-risk'>
                            <h3>✅ Status: CENDERUNG MELANJUTKAN STUDI</h3>
                            <p>Mahasiswa ini diprediksi akan tetap melanjutkan perkuliahannya. Pertahankan performa!</p>
                        </div>
                    """, unsafe_allow_html=True)

            with col_res2:
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = probability_dropout * 100,
                    title = {'text': "Tingkat Risiko Dropout", 'font': {'size': 24, 'color': '#FAFAFA'}},
                    number = {'suffix': "%", 'font': {'size': 36}},
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    gauge = {
                        'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#FAFAFA"},
                        'bar': {'color': "#EF5350" if prediction[0] == 1 else "#66BB6A"},
                        'bgcolor': "#262730",
                        'borderwidth': 2,
                        'bordercolor': "#41444f",
                        'steps': [
                            {'range': [0, 30], 'color': 'rgba(102, 187, 106, 0.5)'},
                            {'range': [30, 60], 'color': 'rgba(255, 238, 88, 0.5)'},
                            {'range': [60, 100], 'color': 'rgba(239, 83, 80, 0.5)'}]
                    }
                ))
                fig.update_layout(paper_bgcolor = "rgba(0,0,0,0)", font = {'color': "#FAFAFA", 'family': "Source Sans Pro"})
                st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error("❌ Terjadi kesalahan dalam pemrosesan data.")
            st.error(f"Detail error: {str(e)}")