import pandas as pd
import streamlit as st
import joblib
import numpy as np

file = "avg_setlist_model2.joblib"

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
# Run with `streamlit run avg_setlist.py`
st.header("Song Setlist Position Predictor (Model 2)")
st.write("Enter song information below:")

col1, col2 = st.columns(2)

with col1:
    length_seconds = st.number_input("Length (sec)", min_value=1, value=60)

with col2:
    rating = st.number_input("Rating", value=0)
    

features = np.array([[length_seconds, rating]])

if st.button("Predict🎵"):
    prediction = model.predict(features)
    #confidence = model.predict_proba(features)

    st.divider()

    st.write(f"Model's estimated average order: {prediction[0]}")
    #st.write(f"Confidence: {confidence}")