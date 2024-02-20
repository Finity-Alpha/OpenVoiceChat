from st_audiorec import st_audiorec
import streamlit as st


wav_audio_data = st_audiorec()

if wav_audio_data is not None:
    st.audio(wav_audio_data, format='audio/wav')