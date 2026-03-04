import pandas as pd
import streamlit as st
import joblib
import numpy as np

file = "model.joblib"

@st.cache_resource
def load_model(file):
    model = joblib.load(file)
    return model

try:
    model = load_model(file)
except FileNotFoundError:
    st.error("Error: Model File Not Found")
    st.stop()

# App UI
# Run with `streamlit run main.py`
st.header("Song Rating Predictor")
st.write("Enter song information below:")

col1 = st.columns(1)

with col1[0]:
    length_seconds = st.number_input("Length (sec)", min_value=1, value=60)
    setlist_frequency = st.number_input("Setlist Frequency", min_value=1, value=10)
    times_favorited = st.number_input("Times Favorited", value=0)
    

features = np.array([[length_seconds, setlist_frequency, times_favorited]])

if st.button("Predict🎵"):
    prediction = model.predict(features)

    st.divider()

    st.write(f"Model's estimated rating: {prediction[0]}")