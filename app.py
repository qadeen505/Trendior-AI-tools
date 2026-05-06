import streamlit as st
import google.generativeai as genai
import asyncio
import edge_tts
import os
import tempfile
from moviepy.editor import ColorClip, TextClip, CompositeVideoClip, AudioFileClip

# 1. إعدادات الهوية البصرية لـ Trendior AI
st.set_page_config(page_title="Trendior AI Tools", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .stButton>button { background-color: #4CAF50; color: white; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 Trendior AI Tools: Full Edition")
st.write("المنصة المتكاملة لتحويل الأفكار إلى فيديوهات تسويقية")

# 2. لوحة التحكم الجانبية
with st.sidebar:
    st.header("⚙️ الإعدادات المتقدمة")
    api_key = st.text_input("Gemini API Key", type="password")
    voice_type = st.selectbox("المعلق الصوتي:", ["ar-SA-ZariyahNeural", "ar-EG-SalmaNeural", "ar-SA-HamedNeural"])
    video_quality = st.select_slider("جودة الفيديو:", options=["360p", "720p", "1080p"])

# 3. الوظائف البرمجية القوية
async def generate_voice_over(text, voice, filename):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filename)

def build_video(script, audio_file):
    # إعدادات الفيديو الرأسي (9:16)
    w, h = 720, 1280
    duration = AudioFileClip(audio_file).duration
    
    # خلفية احترافية
    bg = ColorClip(size=(w, h), color=(20, 20, 20)).set_duration(duration)
    audio = AudioFileClip(audio_file)
    
    # إضافة النص التسويقي في المنتصف
    txt = TextClip(script[:50] + "...", fontsize=40, color='white', size=(w-100, None), method='caption')
    txt = txt.set_position('center').set_duration(duration)
    
    final = CompositeVideoClip([bg, txt]).set_audio(audio)
    output = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    final.write_videofile(output.name, fps=24, codec="libx264", audio_codec="aac")
    return output.name

# 4. محرك التشغيل الرئيسي
col1, col2 = st.columns([1, 1])

with col1:
    topic = st.text_area("وصف الفيديو أو المنتج:", placeholder="مثال: ساعة ذكية جديدة بمواصفات خيالية...")
    platform = st.selectbox("منصة النشر:", ["TikTok", "Reels", "Shorts"])
    
if st.button("🚀 إنتاج الفيديو الكامل"):
    if not api_key:
        st.error("أدخل مفتاح الـ API أولاً")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            with st.spinner("🧠 جاري كتابة السيناريو التسويقي..."):
                prompt = f"اكتب سيناريو جذاب جداً لـ {platform} عن {topic}. ركز على الفوائد والتحفيز."
                res = model.generate_content(prompt)
                full_script = res.text
                st.success("تم توليد السيناريو!")
                st.text_area("السيناريو:", full_script, height=150)

            with st.spinner("🎙️ جاري تسجيل التعليق الصوتي..."):
                audio_temp = "temp_voice.mp3"
                asyncio.run(generate_voice_over(full_script, voice_type, audio_temp))
                st.audio(audio_temp)

            with st.spinner("🎬 جاري معالجة الفيديو النهائي..."):
                final_video_path = build_video(full_script, audio_temp)
                st.video(final_video_path)
                
                with open(final_video_path, "rb") as f:
                    st.download_button("📥 تحميل الفيديو لرفعه على المنصات", f, "trendior_pro.mp4")

        except Exception as e:
            st.error(f"عذراً، حدث خطأ تقني: {str(e)}")
