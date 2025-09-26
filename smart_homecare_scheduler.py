# Smart Homecare Scheduler - All Rights Reserved © Dr. Yousra Abdelatti

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- Page config ---
st.set_page_config(
    page_title="Smart Homecare Scheduler",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
    .stButton>button {background-color:#ff69b4;color:white;height:3em;width:100%;}
    .stTextInput>div>input {border-radius:10px; border:2px solid #ff69b4;}
    .stDataFrame {border:2px solid #ff69b4; border-radius:10px;}
    </style>
    """, unsafe_allow_html=True
)

st.title("💖 Smart Homecare Scheduler")

# --- Session storage ---
if "patients" not in st.session_state:
    st.session_state.patients = pd.DataFrame(columns=["Patient ID", "Name", "Diagnosis"])

if "doctors" not in st.session_state:
    st.session_state.doctors = pd.DataFrame(columns=["Doctor ID", "Name", "Role"])

if "schedule" not in st.session_state:
    st.session_state.schedule = pd.DataFrame(columns=[
        "Visit ID", "Date", "Patient Name", "Doctor Name", "Role", "Start Time", "End Time"
    ])

# --- Sidebar: Add Patients ---
st.sidebar.header("💗 Add / Edit Patients")
with st.sidebar.form("patient_form"):
    patient_name = st.text_input("Patient Name")
    patient_id = st.text_input("Patient ID")
    diagnosis = st.text_input("Diagnosis")
    if st.form_submit_button("Add Patient"):
        st.session_state.patients = pd.concat([
            st.session_state.patients,
            pd.DataFrame([{"Patient ID": patient_id,"Name": patient_name,"Diagnosis": diagnosis}])
        ], ignore_index=True)
        st.success(f"Patient {patient_name} added!")

# --- Sidebar: Add Doctors ---
st.sidebar.header("💉 Add / Edit Doctors")
with st.sidebar.form("doctor_form"):
    doctor_name = st.text_input("Doctor Name")
    doctor_id = st.text_input("Doctor ID")
    role = st.selectbox("Role", ["GP", "Specialist", "Nurse"])
    if st.form_submit_button("Add Doctor"):
        st.session_state.doctors = pd.concat([
            st.session_state.doctors,
            pd.DataFrame([{"Doctor ID": doctor_id,"Name": doctor_name,"Role": role}])
        ], ignore_index=True)
        st.success(f"Doctor {doctor_name} added!")

# --- View Tables ---
st.header("👨‍⚕️ Doctors")
st.dataframe(st.session_state.doctors)

st.header("🧑‍⚕️ Patients")
st.dataframe(st.session_state.patients)

# --- Generate Schedule ---
st.header("📅 Generate Weekly Schedule")
mode = st.radio("Mode", ["Automatic", "Manual"], horizontal=True)
start_date = st.date_input("Start Date", datetime.today())
visit_duration = st.number_input("Visit Duration (minutes)", 15, 240, 60, 15)

if st.button("Generate Schedule"):
    schedule_rows = []
    if st.session_state.patients.empty or st.session_state.doctors.empty:
        st.warning("Add at least one doctor and one patient first!")
    else:
        visit_id_counter = 1
        for i, patient in st.session_state.patients.iterrows():
            if mode == "Automatic":
                doctor = st.session_state.doctors.sample(1).iloc[0]
                visit_date = start_date + timedelta(days=(i % 7))
                start_time = datetime.strptime("09:00", "%H:%M") + timedelta(minutes=(i * visit_duration))
                end_time = start_time + timedelta(minutes=visit_duration)
                schedule_rows.append({
                    "Visit ID": f"V{visit_id_counter:04d}",
                    "Date": visit_date.strftime("%Y-%m-%d"),
                    "Patient Name": patient["Name"],
                    "Doctor Name": doctor["Name"],
                    "Role": doctor["Role"],
                    "Start Time": start_time.strftime("%H:%M"),
                    "End Time": end_time.strftime("%H:%M")
                })
                visit_id_counter += 1
            else:
                st.info(f"Manual mode: assign patient {patient['Name']} later.")

        if schedule_rows:
            st.session_state.schedule = pd.DataFrame(schedule_rows)
            st.success("Schedule generated!")

# --- View Schedule ---
st.header("🗓️ Current Schedule")
st.dataframe(st.session_state.schedule)

# --- Save CSV ---
st.header("💾 Export Data")
if st.button("Save Patients CSV"):
    st.session_state.patients.to_csv("patients.csv", index=False)
    st.success("Patients saved to patients.csv")
if st.button("Save Schedule CSV"):
    st.session_state.schedule.to_csv("schedule.csv", index=False)
    st.success("Schedule saved to schedule.csv")
