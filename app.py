import streamlit as st
import google.generativeai as genai
import json
import re


# =========================
# Page Settings
# =========================
st.set_page_config(
    page_title="Trendior AI Video Director",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 Trendior AI Video Director")
st.write(
    "Generate a complete 4-minute cinematic video plan with characters, ages, genders, voices, scenes, locations, image prompts, and video prompts."
)


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

    video_style = st.selectbox(
        "Video Style:",
        [
            "Cinematic Realistic Drama",
            "Luxury Product Commercial",
            "Corporate Business Story",
            "Emotional Family Story",
            "AI Tools Promotional Story",
            "Documentary Style",
            "Viral Social Media Story"
        ]
    )

    target_platform = st.selectbox(
        "Target Platform:",
        [
            "Instagram Reels",
            "TikTok",
            "YouTube Shorts",
            "YouTube Long Video"
        ]
    )

    language = st.selectbox(
        "Script Language:",
        [
            "English",
            "Arabic",
            "English with short Arabic notes"
        ]
    )


# =========================
# Main Inputs
# =========================
st.markdown("### ✍️ Video Idea / Prompt")

video_idea = st.text_area(
    "Write the video idea here:",
    height=180,
    placeholder=(
        "Example: Create a cinematic 4-minute story about a father who loses his job, "
        "then discovers AI tools that help him rebuild his income and start a smarter digital business."
    )
)

brand_name = st.text_input(
    "Brand / Project Name:",
    value="TRENDIOR AI TOOLS"
)

main_goal = st.text_area(
    "Main Goal of the Video:",
    height=100,
    placeholder="Example: Promote curated AI tools for creators, marketers, and online business owners."
)

generate_button = st.button("🚀 Generate 4-Minute Cinematic Video Plan")


# =========================
# Helper Functions
# =========================
def clean_json_response(text):
    text = text.strip()

    # Remove markdown code fences if Gemini adds them
    text = re.sub(r"^```json", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"^```", "", text).strip()
    text = re.sub(r"```$", "", text).strip()

    # Extract JSON object if extra text exists
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:
        text = text[start:end + 1]

    return text


def safe_get(data, key, default=""):
    return data.get(key, default) if isinstance(data, dict) else default


def display_character_cards(characters):
    st.markdown("## 👥 Characters")

    if not characters:
        st.info("No characters found.")
        return

    for character in characters:
        with st.container(border=True):
            st.markdown(f"### {character.get('name', 'Unnamed Character')}")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.write("**Type:**", character.get("character_type", ""))

            with col2:
                st.write("**Gender:**", character.get("gender", ""))

            with col3:
                st.write("**Age:**", character.get("age", ""))

            with col4:
                st.write("**Voice:**", character.get("recommended_voice", ""))

            st.write("**Role:**", character.get("role", ""))
            st.write("**Personality:**", character.get("personality", ""))
            st.write("**Visual Appearance:**", character.get("visual_appearance", ""))
            st.write("**Voice Direction:**", character.get("voice_direction", ""))


def display_scene_cards(scenes):
    st.markdown("## 🎞️ Cinematic Scenes")

    if not scenes:
        st.info("No scenes found.")
        return

    for scene in scenes:
        with st.container(border=True):
            st.markdown(
                f"### Scene {scene.get('scene_number', '')}: {scene.get('scene_title', '')}"
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                st.write("**Duration:**", scene.get("duration", ""))

            with col2:
                st.write("**Location:**", scene.get("location", ""))

            with col3:
                st.write("**Mood:**", scene.get("mood", ""))

            st.write("**Characters in Scene:**", ", ".join(scene.get("characters_in_scene", [])))

            st.write("**Visual Description:**")
            st.write(scene.get("visual_description", ""))

            st.write("**Camera Direction:**")
            st.write(scene.get("camera_direction", ""))

            st.write("**Dialogue / Voiceover:**")
            st.write(scene.get("dialogue_or_voiceover", ""))

            st.write("**On-Screen Text / Subtitles:**")
            st.write(scene.get("on_screen_text", ""))

            st.write("**Image Generation Prompt:**")
            st.code(scene.get("image_prompt", ""), language="text")

            st.write("**Video Generation Prompt:**")
            st.code(scene.get("video_prompt", ""), language="text")


# =========================
# Generate Plan
# =========================
if generate_button:

    if not api_key:
        st.error("Please enter your Gemini API Key first.")

    elif not video_idea.strip():
        st.error("Please write the video idea first.")

    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name)

            prompt = f"""
You are an expert cinematic video director, AI video prompt engineer, scriptwriter, casting director, and social media strategist.

Create a complete cinematic video production plan for a 4-minute video.

Brand / Project:
{brand_name}

Video Idea:
{video_idea}

Main Goal:
{main_goal}

Target Platform:
{target_platform}

Video Style:
{video_style}

Script Language:
{language}

IMPORTANT:
Return the answer ONLY as valid JSON.
Do not add markdown.
Do not add explanations outside the JSON.
Do not wrap the JSON in triple backticks.

The video must be approximately 4 minutes long.
Create around 12 to 16 scenes.
Each scene should be between 12 and 25 seconds.
The style should be realistic, cinematic, emotionally engaging, and suitable for AI video generation tools.

The plan must include:
1. Video title
2. Core message
3. Target audience
4. Story structure
5. Full character list
6. Character type for each character, such as:
   - child boy
   - child girl
   - teenage boy
   - teenage girl
   - adult man
   - adult woman
   - elderly man
   - elderly woman
7. Age and gender for each character
8. Recommended voice type for each character based on age and gender
9. Voice direction for each character
10. Visual appearance for each character
11. Scene-by-scene cinematic plan
12. Location for each scene
13. Image generation prompt for each scene
14. Video generation prompt for each scene
15. Dialogue or voiceover for each scene
16. On-screen text or subtitles for each scene
17. Music direction
18. Editing direction
19. Final CTA

Character rules:
- The video can include children, adults, elderly people, men, and women when useful for the story.
- Every character must have a clear character_type.
- Every character must have a realistic age.
- Every character must have a clear gender.
- Every character must have a voice recommendation that matches age and gender.
- Do not assign an adult voice to a child character.
- Do not assign a male voice to a female character.
- Do not assign a female voice to a male character.
- If a child appears, specify whether the child is a boy or a girl.
- If an adult appears, specify whether the adult is a man or a woman.
- If an elderly character appears, specify whether the elderly character is a man or a woman.

Voice recommendations should match the character's age and gender.

Use practical voice labels such as:
- young boy child voice
- young girl child voice
- teenage boy voice
- teenage girl voice
- warm adult male voice
- calm adult male voice
- confident middle-aged male voice
- professional adult female voice
- warm adult female voice
- calm elderly male voice
- calm elderly female voice
- emotional female narrator
- luxury commercial narrator
- energetic young male voice
- calm young female voice

For every image_prompt:
Write it as a realistic cinematic vertical 9:16 image prompt.
Include:
- character type
- character age
- gender
- appearance
- clothing
- location
- lighting
- mood
- camera angle
- cinematic realism
- high detail
- no text in image

For every video_prompt:
Write it as a realistic cinematic vertical 9:16 video prompt.
Include:
- character movement
- camera movement
- environment movement
- emotion
- lighting
- realistic motion
- cinematic quality
- no subtitles baked into the video

The visual style can include scenes like:
- modern office meeting
- father and daughter at home
- businesswoman in a corporate office
- tired entrepreneur at night
- family conversation
- workplace discussion
- cinematic close-up of a face
- emotional mirror scene
- coffee room conversation
- modern city office background
- product-style cinematic shots
- realistic social media drama scenes

Return JSON in this exact structure:

{{
  "video_title": "",
  "estimated_duration": "4 minutes",
  "brand_name": "",
  "core_message": "",
  "target_audience": "",
  "video_style": "",
  "story_structure": {{
    "hook": "",
    "conflict": "",
    "turning_point": "",
    "solution": "",
    "transformation": "",
    "call_to_action": ""
  }},
  "characters": [
    {{
      "name": "",
      "character_type": "",
      "gender": "",
      "age": "",
      "role": "",
      "personality": "",
      "visual_appearance": "",
      "recommended_voice": "",
      "voice_direction": ""
    }}
  ],
  "scenes": [
    {{
      "scene_number": 1,
      "scene_title": "",
      "duration": "",
      "location": "",
      "mood": "",
      "characters_in_scene": [],
      "visual_description": "",
      "camera_direction": "",
      "dialogue_or_voiceover": "",
      "on_screen_text": "",
      "image_prompt": "",
      "video_prompt": ""
    }}
  ],
  "music_direction": "",
  "editing_direction": "",
  "subtitle_style": "",
  "final_cta": "",
  "production_notes": ""
}}
"""

            with st.spinner("Generating cinematic video plan..."):
                response = model.generate_content(prompt)
                raw_text = response.text

                cleaned_text = clean_json_response(raw_text)

                try:
                    plan = json.loads(cleaned_text)
                except json.JSONDecodeError:
                    st.error("The model returned text that could not be parsed as JSON.")
                    st.subheader("Raw Output")
                    st.code(raw_text, language="text")
                    st.stop()

            # =========================
            # Display Results
            # =========================
            st.success("✅ 4-minute cinematic video plan generated successfully.")

            st.markdown("## 🎬 Video Overview")

            col1, col2 = st.columns(2)

            with col1:
                st.write("**Title:**", safe_get(plan, "video_title"))
                st.write("**Estimated Duration:**", safe_get(plan, "estimated_duration"))
                st.write("**Brand:**", safe_get(plan, "brand_name"))
                st.write("**Target Audience:**", safe_get(plan, "target_audience"))

            with col2:
                st.write("**Video Style:**", safe_get(plan, "video_style"))
                st.write("**Core Message:**", safe_get(plan, "core_message"))
                st.write("**Final CTA:**", safe_get(plan, "final_cta"))

            st.markdown("## 🧠 Story Structure")
            story_structure = plan.get("story_structure", {})

            if story_structure:
                for key, value in story_structure.items():
                    st.write(f"**{key.replace('_', ' ').title()}:** {value}")

            display_character_cards(plan.get("characters", []))
            display_scene_cards(plan.get("scenes", []))

            st.markdown("## 🎵 Music Direction")
            st.write(plan.get("music_direction", ""))

            st.markdown("## ✂️ Editing Direction")
            st.write(plan.get("editing_direction", ""))

            st.markdown("## 🔤 Subtitle Style")
            st.write(plan.get("subtitle_style", ""))

            st.markdown("## 📝 Production Notes")
            st.write(plan.get("production_notes", ""))

            # Download JSON
            st.download_button(
                label="⬇️ Download Video Plan as JSON",
                data=json.dumps(plan, ensure_ascii=False, indent=2),
                file_name="trendior_cinematic_video_plan.json",
                mime="application/json"
            )

            # Download TXT
            readable_text = json.dumps(plan, ensure_ascii=False, indent=2)
            st.download_button(
                label="⬇️ Download Video Plan as TXT",
                data=readable_text,
                file_name="trendior_cinematic_video_plan.txt",
                mime="text/plain"
            )

        except Exception as e:
            error_message = str(e)

            if "429" in error_message or "quota" in error_message.lower():
                st.error(
                    "Gemini API quota is not available for this model. Try another model from the sidebar or use another API key from a new Google AI Studio project."
                )
                st.code(error_message)

            elif "API key" in error_message or "permission" in error_message.lower():
                st.error(
                    "There is a problem with the API key. Make sure it is correct and created from Google AI Studio."
                )
                st.code(error_message)

            else:
                st.error("An error occurred while generating the cinematic video plan.")
                st.code(error_message)
