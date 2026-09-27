import streamlit as st
import subprocess

st.title("Minimal Git Test")
if st.button("Run Git"):
    result = subprocess.run(["git", "status"], capture_output=True, text=True)
    st.write(result.stdout)