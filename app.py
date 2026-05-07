import streamlit as st
import google.generativeai as genai
import asyncio
import edge_tts
import os
import tempfile
from moviepy.editor import ColorClip, TextClip, CompositeVideoClip, AudioFileClip

# Settings
st.set_page_config(page_title="Trendior AI Tools", page_icon="🎬", layout="wide")

st.title("🎬 Trendior AI Tools: Full Edition")

with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Gemini API Key", type="password")
    voice_type = st.selectbox("Voice:", ["ar-SA-ZariyahNeural", "ar-EG-SalmaNeural"])

async def generate_voice_over(text, voice, filename):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filename)

def build_video(script, audio_file):
    duration = AudioFileClip(audio_file).duration
    bg = ColorClip(size=(720, 1280), color=(20, 20, 20)).set_duration(duration)
    audio = AudioFileClip(audio_file)
    txt = TextClip("Trendior AI Tools\n\n" + script[:30] + "...", fontsize=40, color='white', size=(620, None), method='caption')
    txt = txt.set_position('center').set_duration(duration)
    final = CompositeVideoClip([bg, txt]).set_audio(audio)
    output = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    final.write_videofile(output.name, fps=24, codec="libx264", audio_codec="aac")
    return output.name

topic = st.text_area("وصف الفيديو:")
platform = st.selectbox("المنصة:", ["TikTok", "Reels", "Shorts"])
    
if st.button("🚀 إنتاج الفيديو الكامل"):
    if not api_key:
        st.error("أدخل مفتاح الـ API أولاً")
    else:
        try:
            genai.configure(api_key=api_key)
            # تم تحديث النموذج هنا ليصبح متوافقاً
            model = genai.GenerativeModel('models/gemini-pro')
            
            with st.spinner("Writing Script..."):
                res = model.generate_content(f"اكتب سيناريو جذاب لـ {platform} عن {topic}")
                full_script = res.text
                st.write(full_script)

            with st.spinner("Recording Voice..."):
                audio_temp = "temp_voice.mp3"
                asyncio.run(generate_voice_over(full_script, voice_type, audio_temp))
                st.audio(audio_temp)

            with st.spinner("Creating Video..."):
                video_path = build_video(full_script, audio_temp)
                st.video(video_path)
                with open(video_path, "rb") as f:
                    st.download_button("Download Video", f, "trendior.mp4")

        except Exception as e:
            st.error(f"Error: {str(e)}")
