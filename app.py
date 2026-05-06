import streamlit as st
import google.generativeai as genai
import asyncio
import edge_tts
import os
import tempfile
from moviepy.editor import ColorClip, TextClip, CompositeVideoClip, AudioFileClip

# 1. إعدادات الصفحة الأساسية
st.set_page_config(page_title="Trendior AI Tools", page_icon="video", layout="wide")

st.title("Trendior AI Video Maker")
st.markdown("---")

# 2. إعدادات الشريط الجانبي
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    voice_choice = st.selectbox("Choose Voice:", ["ar-EG-SalmaNeural", "ar-SA-ZariyahNeural"])

# 3. الوظائف البرمجية (توليد الصوت)
async def generate_audio(text, voice, path):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(path)

# 4. الواجهة الرئيسية
topic = st.text_area("What is the video topic?", placeholder="Example: Top 3 AI tools for marketing")
platform = st.selectbox("Target Platform:", ["YouTube Shorts", "TikTok", "Instagram Reels"])

if st.button("Generate Video"):
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar.")
    elif not topic:
        st.warning("Please enter a topic for the video.")
    else:
        try:
            # إعداد محرك Gemini
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            with st.spinner("Writing Script..."):
                prompt = f"Write a short, engaging marketing script for {platform} about: {topic}. Language: Arabic."
                response = model.generate_content(prompt)
                script = response.text
                st.subheader("Generated Script:")
                st.write(script)

            with st.spinner("Generating Voice..."):
                audio_path = "output_audio.mp3"
                asyncio.run(generate_audio(script, voice_choice, audio_path))
                st.audio(audio_path)

            # ملاحظة: تم إيقاف المونتاج المتقدم مؤقتاً لضمان عمل الواجهة أولاً
            st.success("The script and audio are ready! We will enable full video rendering once the interface is stable.")
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# نهاية الكود البرمجي النظيف
