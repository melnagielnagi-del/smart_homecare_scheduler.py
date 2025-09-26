"""
Smart Homecare Scheduler
© All rights reserved to Dr. Yousra Abdelatti
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- Initialize Session State ---
if "patients" not in st.session_state:
    st.session_state.patients = pd.DataFrame(columns=["Name", "Diagnosis"])
if "doctors" not in st.session_state:
    st.session_state.doctors = pd.DataFrame(columns=["Name", "Role"])
if "schedule" not in st.session_state:
    st.session_state.schedule = pd.DataFrame(columns=[
        "Visit ID", "Date", "Patient Name", "Diagnosis", "Doctor Name", "Role", "Start Time", "End Time"
    ])

# --- Sidebar Menu ---
st.sidebar.title("Smart Homecare Scheduler")
menu_choice = st.sidebar.radio("Menu", [
    "Add Patient", "Add Doctor", "Generate Schedule",
    "View Schedule", "Insert Emergency"
])

# --- Add Patient ---
if menu_choice == "Add Patient":
    st.header("👤 Add Patient")
    name = st.text_input("Patient Name")
    diagnosis = st.text_input("Diagnosis")
    if st.button("Add Patient"):
        if name.strip() != "":
            st.session_state.patients = pd.concat([
                st.session_state.patients,
                pd.DataFrame([{"Name": name, "Diagnosis": diagnosis}])
            ], ignore_index=True)
            st.success(f"Patient '{name}' added.")
    st.data_editor(st.session_state.patients, num_rows="dynamic", use_container_width=True)

# --- Add Doctor ---
elif menu_choice == "Add Doctor":
    st.header("🩺 Add Doctor")
    name = st.text_input("Doctor Name")
    role = st.text_input("Role")
    if st.button("Add Doctor"):
        if name.strip() != "":
            st.session_state.doctors = pd.concat([
                st.session_state.doctors,
                pd.DataFrame([{"Name": name, "Role": role}])
            ], ignore_index=True)
            st.success(f"Doctor '{name}' added.")
    st.data_editor(st.session_state.doctors, num_rows="dynamic", use_container_width=True)

# --- Generate Schedule ---
elif menu_choice == "Generate Schedule":
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
                doctor = None
                visit_date = start_date + timedelta(days=(i % 7))
                start_time = datetime.strptime("09:00", "%H:%M") + timedelta(minutes=(i * visit_duration))
                end_time = start_time + timedelta(minutes=visit_duration)

                if mode == "Automatic":
                    doctor = st.session_state.doctors.sample(1).iloc[0]
                    schedule_rows.append({
                        "Visit ID": f"V{visit_id_counter:04d}",
                        "Date": visit_date.strftime("%Y-%m-%d"),
                        "Patient Name": patient["Name"],
                        "Diagnosis": patient["Diagnosis"],
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

# --- View / Edit Schedule ---
elif menu_choice == "View Schedule":
    st.header("🗓️ Current Schedule")
    if st.session_state.schedule.empty:
        st.info("No schedule yet. Generate it first.")
    else:
        edited_schedule = st.data_editor(
            st.session_state.schedule,
            num_rows="dynamic",
            use_container_width=True
        )
        st.session_state.schedule = edited_schedule

# --- Insert Emergency ---
elif menu_choice == "Insert Emergency":
    st.header("🚨 Insert Emergency Patient")
    name = st.text_input("Emergency Patient Name")
    diagnosis = st.text_input("Diagnosis")
    doctor = st.selectbox("Assign Doctor", st.session_state.doctors["Name"] if not st.session_state.doctors.empty else ["None"])
    time = st.time_input("Start Time", datetime.now())
    duration = st.number_input("Duration (minutes)", 15, 240, 60, 15)

    if st.button("Add Emergency"):
        if name.strip() != "":
            visit_id = f"V{len(st.session_state.schedule)+1:04d}"
            end_time = (datetime.combine(datetime.today(), time) + timedelta(minutes=duration)).time()
            st.session_state.schedule = pd.concat([
                st.session_state.schedule,
                pd.DataFrame([{
                    "Visit ID": visit_id,
                    "Date": datetime.today().strftime("%Y-%m-%d"),
                    "Patient Name": name,
                    "Diagnosis": diagnosis,
                    "Doctor Name": doctor,
                    "Role": st.session_state.doctors[st.session_state.doctors["Name"]==doctor]["Role"].values[0] if doctor!="None" else "",
                    "Start Time": time.strftime("%H:%M"),
                    "End Time": end_time.strftime("%H:%M")
                }])
            ], ignore_index=True)
            st.success(f"Emergency '{name}' added.")

# --- Footer ---
st.markdown("---")
st.markdown("© All rights reserved to Dr. Yousra Abdelatti")


