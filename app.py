import streamlit as st
import google.generativeai as genai
import asyncio
import edge_tts
import os
import tempfile
from moviepy.editor import ColorClip, TextClip, CompositeVideoClip, AudioFileClip


# =========================
# Page Settings
# =========================
st.set_page_config(
    page_title="Trendior AI Tools",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 Trendior AI Tools: Full Edition")


# =========================
# Sidebar Settings
# =========================
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Gemini API Key", type="password")
    voice_type = st.selectbox(
        "Voice:",
        [
            "ar-SA-ZariyahNeural",
            "ar-EG-SalmaNeural",
            "en-US-JennyNeural",
            "en-US-GuyNeural"
        ]
    )


# =========================
# Voice Over Function
# =========================
async def generate_voice_over(text, voice, filename):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filename)


# =========================
# Video Builder Function
# =========================
def build_video(script, audio_file):
    audio = AudioFileClip(audio_file)
    duration = audio.duration

    bg = ColorClip(
        size=(720, 1280),
        color=(20, 20, 20)
    ).set_duration(duration)

    short_text = script[:700]

    txt = TextClip(
        "Trendior AI Tools\n\n" + short_text,
        fontsize=38,
        color="white",
        size=(620, 1000),
        method="caption",
        align="center"
    )

    txt = txt.set_position("center").set_duration(duration)

    final = CompositeVideoClip([bg, txt]).set_audio(audio)

    output = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    output_path = output.name
    output.close()

    final.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )

    audio.close()
    final.close()

    return output_path


# =========================
# Main Inputs
# =========================
topic = st.text_area(
    "وصف الفيديو:",
    placeholder="مثال: اعمل لي فيديو عن أفضل أدوات الذكاء الاصطناعي لصناعة المحتوى والتسويق"
)

platform = st.selectbox(
    "المنصة:",
    ["TikTok", "Reels", "Shorts", "YouTube"]
)


# =========================
# Generate Button
# =========================
if st.button("🚀 إنتاج الفيديو الكامل"):

    if not api_key:
        st.error("أدخل مفتاح الـ API أولاً")

    elif not topic.strip():
        st.error("اكتب وصف الفيديو أولاً")

    else:
        try:
            genai.configure(api_key=api_key)

            model = genai.GenerativeModel("gemini-2.0-flash")

            prompt = f"""
اكتب سيناريو فيديو احترافي لمشروع TRENDIOR AI TOOLS.

المطلوب:
- المنصة: {platform}
- موضوع الفيديو: {topic}
- اجعل الأسلوب تسويقيًا، واضحًا، مقنعًا، ومناسبًا لأدوات الذكاء الاصطناعي.
- لا تكتب مقدمة طويلة.
- ابدأ بخطاف قوي في أول 5 ثواني.
- اشرح الفكرة بطريقة بسيطة.
- اربط الفكرة بفائدة عملية للمسوقين، صناع المحتوى، وأصحاب الأعمال الرقمية.
- اختم بدعوة للمتابعة وزيارة TRENDIOR AI TOOLS.
- اكتب النص فقط بدون عناوين تقنية أو ملاحظات إخراجية.
"""

            with st.spinner("Writing Script..."):
                res = model.generate_content(prompt)
                full_script = res.text.strip()

                st.subheader("📜 Generated Script")
                st.write(full_script)

            with st.spinner("Recording Voice..."):
                audio_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                audio_path = audio_temp.name
                audio_temp.close()

                asyncio.run(generate_voice_over(full_script, voice_type, audio_path))
                st.audio(audio_path)

            with st.spinner("Creating Video..."):
                video_path = build_video(full_script, audio_path)

                st.subheader("🎥 Generated Video")
                st.video(video_path)

                with open(video_path, "rb") as f:
                    st.download_button(
                        "⬇️ Download Video",
                        f,
                        "trendior_video.mp4",
                        "video/mp4"
                    )

        except Exception as e:
            st.error(f"Error: {str(e)}")
