import streamlit as st
import google.generativeai as genai
import asyncio
import edge_tts
import tempfile
import textwrap
from moviepy.editor import ImageClip, CompositeVideoClip, AudioFileClip
from PIL import Image, ImageDraw, ImageFont


# =========================
# Page Settings
# =========================
st.set_page_config(
    page_title="Trendior AI Tools",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 Trendior AI Tools: Full Edition")
st.write("أداة بسيطة لإنشاء سكربت + تعليق صوتي + فيديو قصير لمشروع TRENDIOR AI TOOLS.")


# =========================
# Sidebar Settings
# =========================
with st.sidebar:
    st.header("⚙️ Settings")

    api_key = st.text_input("Gemini API Key", type="password")

    model_name = st.selectbox(
        "Gemini Model:",
        [
            "gemini-1.5-flash",
            "gemini-2.0-flash",
            "gemini-2.5-flash"
        ]
    )

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
# PIL Version - No ImageMagick Needed
# =========================
def build_video(script, audio_file):
    audio = AudioFileClip(audio_file)
    duration = audio.duration

    width, height = 720, 1280

    # Create video background as an image
    img = Image.new("RGB", (width, height), color=(16, 18, 24))
    draw = ImageDraw.Draw(img)

    # Load fonts
    try:
        font_title = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            46
        )
        font_text = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            32
        )
        font_footer = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            28
        )
    except Exception:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()
        font_footer = ImageFont.load_default()

    # Title
    title = "TRENDIOR AI TOOLS"
    draw.text(
        (width // 2, 120),
        title,
        font=font_title,
        fill=(255, 255, 255),
        anchor="mm"
    )

    # Decorative line
    draw.line(
        (100, 175, 620, 175),
        fill=(120, 180, 255),
        width=4
    )

    # Script text
    clean_script = script.replace("\n", " ")
    short_script = clean_script[:850]

    wrapped_text = textwrap.fill(short_script, width=34)

    y = 250
    for line in wrapped_text.split("\n"):
        draw.text(
            (width // 2, y),
            line,
            font=font_text,
            fill=(235, 235, 235),
            anchor="mm"
        )
        y += 50

        if y > 1040:
            break

    # Footer
    footer = "Follow for curated AI tools"
    draw.text(
        (width // 2, 1160),
        footer,
        font=font_footer,
        fill=(255, 255, 255),
        anchor="mm"
    )

    # Save temporary image
    image_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    image_path = image_temp.name
    image_temp.close()
    img.save(image_path)

    # Convert image to video and add audio
    bg_clip = ImageClip(image_path).set_duration(duration)
    final = CompositeVideoClip([bg_clip]).set_audio(audio)

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
    bg_clip.close()
    final.close()

    return output_path


# =========================
# Main Inputs
# =========================
topic = st.text_area(
    "وصف الفيديو:",
    placeholder="مثال: اعمل لي فيديو قصير عن أداة ذكاء اصطناعي تساعد المسوقين وصناع المحتوى على توفير الوقت وزيادة الإنتاجية."
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
        st.error("أدخل مفتاح Gemini API أولاً.")

    elif not topic.strip():
        st.error("اكتب وصف الفيديو أولاً.")

    else:
        try:
            genai.configure(api_key=api_key)

            model = genai.GenerativeModel(model_name)

            prompt = f"""
اكتب سيناريو فيديو احترافي لمشروع TRENDIOR AI TOOLS.

المطلوب:
- المنصة: {platform}
- موضوع الفيديو: {topic}

الشروط:
- اجعل الأسلوب تسويقيًا، واضحًا، مقنعًا، واحترافيًا.
- ابدأ بخطاف قوي في أول 5 ثواني.
- لا تستخدم مقدمة طويلة.
- لا تقلد أي منشئ محتوى.
- لا تستخدم عبارات مبالغ فيها أو وعود غير واقعية.
- اشرح الفكرة بطريقة بسيطة.
- اربط الفكرة بفائدة عملية لصناع المحتوى، المسوقين، أصحاب المشاريع الرقمية، والمهتمين بأدوات الذكاء الاصطناعي.
- اجعل النص مناسبًا للتعليق الصوتي.
- اختم بدعوة للمتابعة وزيارة TRENDIOR AI TOOLS.
- اكتب النص النهائي فقط بدون عناوين تقنية وبدون ملاحظات إخراجية.
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

                st.subheader("🔊 Generated Voice")
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
            error_message = str(e)

            if "429" in error_message or "quota" in error_message.lower():
                st.error(
                    "حدث خطأ بسبب نفاد أو عدم توفر حصة Gemini API لهذا الموديل. "
                    "جرّب تغيير الموديل من القائمة الجانبية إلى gemini-1.5-flash أو استخدم API Key من مشروع Google AI Studio آخر."
                )
                st.code(error_message)

            elif "API key" in error_message or "permission" in error_message.lower():
                st.error(
                    "يبدو أن هناك مشكلة في مفتاح API. تأكد أن المفتاح صحيح ومأخوذ من Google AI Studio."
                )
                st.code(error_message)

            else:
                st.error("حدث خطأ أثناء تنفيذ العملية.")
                st.code(error_message)
