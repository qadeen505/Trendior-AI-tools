import streamlit as st
import google.generativeai as genai
import asyncio
import edge_tts
import tempfile
import textwrap
import re
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips


# =========================
# Compatibility Fix
# Fix for Pillow 10+ with MoviePy 1.0.3
# =========================
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS


# =========================
# Page Settings
# =========================
st.set_page_config(
    page_title="Trendior AI Tools",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 Trendior AI Tools: English Video Maker")
st.write("Generate an English script, realistic AI voice, and a simple animated vertical video.")


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
        "English Voice:",
        [
            "en-US-JennyNeural",
            "en-US-GuyNeural",
            "en-US-AriaNeural",
            "en-US-DavisNeural",
            "en-GB-RyanNeural",
            "en-GB-SoniaNeural"
        ]
    )

    video_length = st.selectbox(
        "Video Length:",
        [
            "Short 45-60 seconds",
            "Medium 90 seconds",
            "Long 2 minutes"
        ]
    )


# =========================
# Main Visible Inputs
# =========================
st.markdown("### ✍️ Video Topic / Prompt")

topic = st.text_area(
    "Write your video idea here:",
    height=160,
    placeholder="Example: Create a short video about how AI tools can help creators save time, write better content, and automate repetitive marketing tasks."
)

platform = st.selectbox(
    "Platform:",
    [
        "TikTok",
        "Instagram Reels",
        "YouTube Shorts"
    ]
)

generate_button = st.button("🚀 Generate Full Video")


# =========================
# Voice Over Function
# =========================
async def generate_voice_over(text, voice, filename):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filename)


# =========================
# Helper Functions
# =========================
def load_font(size, bold=False):
    try:
        if bold:
            return ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                size
            )
        return ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            size
        )
    except Exception:
        return ImageFont.load_default()


def clean_script_text(text):
    text = re.sub(r"\[.*?\]", "", text)
    text = re.sub(r"\(.*?\)", "", text)
    text = text.replace("*", "")
    text = text.replace("#", "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def split_script_into_scenes(script, max_chars=230):
    sentences = re.split(r"(?<=[.!?])\s+", script)
    scenes = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) <= max_chars:
            current += " " + sentence
        else:
            if current.strip():
                scenes.append(current.strip())
            current = sentence

    if current.strip():
        scenes.append(current.strip())

    return scenes[:8]


def create_scene_image(scene_text, scene_number, total_scenes, platform):
    width, height = 720, 1280

    img = Image.new("RGB", (width, height), color=(10, 14, 25))
    draw = ImageDraw.Draw(img)

    title_font = load_font(46, bold=True)
    scene_font = load_font(34, bold=True)
    body_font = load_font(34, bold=False)
    small_font = load_font(25, bold=True)
    footer_font = load_font(27, bold=True)

    # Background gradient
    for y in range(height):
        r = int(10 + y * 0.015)
        g = int(14 + y * 0.02)
        b = int(25 + y * 0.04)
        draw.line((0, y, width, y), fill=(r, g, min(b, 70)))

    # Decorative circles
    circle_positions = [
        (-120, 100, 260, 480),
        (500, 60, 880, 440),
        (-80, 850, 280, 1210),
        (470, 900, 850, 1280)
    ]

    circle_colors = [
        (35, 92, 160),
        (80, 40, 150),
        (25, 130, 120),
        (120, 70, 30)
    ]

    for pos, color in zip(circle_positions, circle_colors):
        draw.ellipse(pos, outline=color, width=6)

    draw.text(
        (width // 2, 92),
        "TRENDIOR AI TOOLS",
        font=title_font,
        fill=(255, 255, 255),
        anchor="mm"
    )

    draw.text(
        (width // 2, 145),
        f"{platform} • AI Tools • Smart Workflows",
        font=small_font,
        fill=(160, 200, 255),
        anchor="mm"
    )

    # Progress bar
    bar_x = 90
    bar_y = 200
    bar_w = 540
    bar_h = 12
    progress = int(bar_w * (scene_number / total_scenes))

    draw.rounded_rectangle(
        (bar_x, bar_y, bar_x + bar_w, bar_y + bar_h),
        radius=8,
        fill=(55, 60, 75)
    )

    draw.rounded_rectangle(
        (bar_x, bar_y, bar_x + progress, bar_y + bar_h),
        radius=8,
        fill=(90, 180, 255)
    )

    draw.text(
        (width // 2, 285),
        f"SCENE {scene_number}",
        font=scene_font,
        fill=(180, 220, 255),
        anchor="mm"
    )

    # Text box
    box_x1, box_y1 = 70, 350
    box_x2, box_y2 = 650, 900

    draw.rounded_rectangle(
        (box_x1, box_y1, box_x2, box_y2),
        radius=30,
        fill=(18, 24, 38),
        outline=(80, 130, 190),
        width=3
    )

    wrapped = textwrap.fill(scene_text, width=28)
    lines = wrapped.split("\n")

    y = 430
    for line in lines[:9]:
        draw.text(
            (width // 2, y),
            line,
            font=body_font,
            fill=(245, 245, 245),
            anchor="mm"
        )
        y += 55

    # CTA button
    draw.rounded_rectangle(
        (90, 1010, 630, 1105),
        radius=24,
        fill=(90, 180, 255)
    )

    draw.text(
        (width // 2, 1058),
        "Follow for practical AI tools",
        font=footer_font,
        fill=(5, 10, 20),
        anchor="mm"
    )

    draw.text(
        (width // 2, 1180),
        "Create smarter. Automate faster. Grow better.",
        font=small_font,
        fill=(220, 225, 235),
        anchor="mm"
    )

    temp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    img_path = temp_img.name
    temp_img.close()

    img.save(img_path)
    return img_path


def build_video(script, audio_file, platform):
    audio = AudioFileClip(audio_file)
    duration = audio.duration

    scenes = split_script_into_scenes(script)

    if not scenes:
        scenes = [script[:250]]

    total_scenes = len(scenes)
    scene_duration = max(4, duration / total_scenes)

    clips = []

    for i, scene in enumerate(scenes, start=1):
        img_path = create_scene_image(scene, i, total_scenes, platform)

        clip = ImageClip(img_path).set_duration(scene_duration)

        # Simple slow zoom
        clip = clip.resize(lambda t: 1 + 0.015 * t)

        if i != 1:
            clip = clip.crossfadein(0.4)

        clips.append(clip)

    video = concatenate_videoclips(clips, method="compose", padding=-0.4)
    video = video.set_audio(audio)

    output = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    output_path = output.name
    output.close()

    video.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )

    audio.close()
    video.close()

    return output_path


# =========================
# Generate Video
# =========================
if generate_button:

    if not api_key:
        st.error("Please enter your Gemini API Key first.")

    elif not topic.strip():
        st.error("Please write the video topic first.")

    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name)

            length_instruction = {
                "Short 45-60 seconds": "Write around 120 to 150 words.",
                "Medium 90 seconds": "Write around 190 to 230 words.",
                "Long 2 minutes": "Write around 260 to 320 words."
            }[video_length]

            prompt = f"""
Write a natural English voiceover script for TRENDIOR AI TOOLS.

Platform: {platform}
Topic: {topic}

Requirements:
- Write in English only.
- {length_instruction}
- Make it sound human, confident, and conversational.
- Start with a strong hook in the first sentence.
- Do not sound robotic.
- Do not use Arabic.
- Do not add scene labels.
- Do not add markdown.
- Do not add camera directions.
- Focus on creators, marketers, affiliate marketers, and online business owners.
- Explain the idea clearly and practically.
- End with a soft CTA: Follow TRENDIOR AI TOOLS for curated AI tools and smart workflows.
"""

            with st.spinner("Writing English Script..."):
                res = model.generate_content(prompt)
                full_script = clean_script_text(res.text)

                st.subheader("📜 Generated English Script")
                st.write(full_script)

            with st.spinner("Generating English Voice..."):
                audio_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                audio_path = audio_temp.name
                audio_temp.close()

                asyncio.run(generate_voice_over(full_script, voice_type, audio_path))

                st.subheader("🔊 Generated Voice")
                st.audio(audio_path)

            with st.spinner("Creating Animated Video..."):
                video_path = build_video(full_script, audio_path, platform)

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
                    "Gemini API quota is not available for this model. "
                    "Try another model from the sidebar or use another API key from a new Google AI Studio project."
                )
                st.code(error_message)

            elif "API key" in error_message or "permission" in error_message.lower():
                st.error(
                    "There is a problem with the API key. Make sure it is correct and created from Google AI Studio."
                )
                st.code(error_message)

            else:
                st.error("An error occurred while generating the video.")
                st.code(error_message)
