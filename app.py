import streamlit as st
import google.generativeai as genai
import asyncio
import edge_tts
import os
import tempfile
from moviepy.editor import TextClip, ColorClip, CompositeVideoClip, AudioFileClip

# 1. إعدادات الصفحة والسمة الهوية التجارية
st.set_page_config(page_title="Trendior AI Tools", page_icon="🎬", layout="wide")

# تصميم الواجهة بلمسة احترافية
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #007bff; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Trendior AI Tools: Video Maker")
st.info("مرحباً قمر الدين! ابدأ بصناعة محتواك التسويقي الآن.")

# 2. إعدادات الـ API (المحرك)
with st.sidebar:
    st.header("⚙️ الإعدادات")
    gemini_key = st.text_input("Gemini API Key", type="password")
    voice_option = st.selectbox("اختر المعلق الصوتي (العربي):", ["ar-EG-SalmaNeural", "ar-SA-ZariyahNeural"])
    
# 3. مدخلات المحتوى
platform = st.selectbox("منصة النشر المستهدفة:", ["YouTube Shorts", "TikTok", "Instagram Reels"])
topic = st.text_area("عن ماذا يتحدث الفيديو؟ (اكتب فكرتك هنا)", placeholder="مثال: أهم 3 أدوات ذكاء اصطناعي لعام 2026")

# 4. الوظائف البرمجية الأساسية
async def generate_audio(text, voice, output_path):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

def create_video(script_text, audio_path):
    # إنشاء خلفية بسيطة للفيديو (Vertical)
    bg = ColorClip(size=(720, 1280), color=(10, 10, 10), duration=10)
    audio = AudioFileClip(audio_path)
    
    # إضافة النص (مبسط لتجنب أخطاء الخطوط في السيرفر)
    txt_clip = TextClip("Trendior AI Tools\n\n" + script_text[:30] + "...", fontsize=50, color='white', size=(600, 1000))
    txt_clip = txt_clip.set_position('center').set_duration(audio.duration)
    
    final_video = CompositeVideoClip([bg, txt_clip])
    final_video = final_video.set_audio(audio).set_duration(audio.duration)
    
    output_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    final_video.write_videofile(output_video.name, fps=24, codec="libx264")
    return output_video.name

# 5. زر التشغيل والمنطق
if st.button("توليد الفيديو"):
    if not gemini_key:
        st.error("الرجاء إدخال مفتاح Gemini API Key أولاً!")
    elif not topic:
        st.warning("الرجاء كتابة موضوع للفيديو.")
    else:
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-pro')
            
            with st.spinner("🧠 جاري كتابة السيناريو..."):
                response = model.generate_content(f"اكتب سيناريو فيديو قصير لـ {platform} عن: {topic}. اجعل النص جذاباً وتسويقياً.")
                script = response.text
                st.write("### السيناريو المقترح:")
                st.write(script)

            with st.spinner("🎙️ جاري توليد الصوت..."):
                audio_file = "temp_audio.mp3"
                asyncio.run(generate_audio(script, voice_option, audio_file))

            with st.spinner("🎬 جاري مونتاج الفيديو..."):
                # ملاحظة: المونتاج الكامل يتطلب معالجة صور، هنا نقوم بإنتاج النسخة الأولية
                video_path = create_video(script, audio_file)
                st.video(video_path)
                
                with open(video_path, "rb") as file:
                    st.download_button("تحميل الفيديو النهائي", data=file, file_name="Trendior_Video.mp4", mime="video/mp4")
            
            st.success("تم إنتاج الفيديو بنجاح!")
            
        except Exception as e:
            st.error(f"حدث خطأ: {e}")
