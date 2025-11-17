import streamlit as st
from openai import OpenAI
from youtube_transcript_api import YouTubeTranscriptApi
import re

client = OpenAI(api_key="YOUR_OPENAI_API_KEY")


# -------------------------------------------------------
# Extract YouTube Video ID
# -------------------------------------------------------
def extract_video_id(url):
    pattern = r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})"
    match = re.search(pattern, url)
    return match.group(1) if match else None


# -------------------------------------------------------
# Fetch Transcript from YouTube
# -------------------------------------------------------
def fetch_youtube_transcript(url):
    video_id = extract_video_id(url)
    if not video_id:
        return None

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([item["text"] for item in transcript])
        return text
    except:
        return None


# -------------------------------------------------------
# AI Model Evaluation
# -------------------------------------------------------
def evaluate_video(title, description, transcript):
    prompt = f"""
You are an AI model that evaluates video relevance.

Input:
Title: {title}
Description: {description}
Transcript: {transcript}

Tasks:
1. Evaluate how relevant the transcript is to the title.
2. Detect and list:
   - Off-topic segments
   - Promotional segments
   - Filler segments
3. Generate:
   - Relevance Score (0–100%)
   - Short explanation for score
   - Segment analysis in bullet points

Return output in JSON with fields:
relevance_score, explanation, detected_segments.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    return response.choices[0].message["content"]


# -------------------------------------------------------
# Streamlit UI
# -------------------------------------------------------
st.title("🎥 AI Video Relevance Evaluator")

option = st.radio("Choose Input Method:", ["YouTube URL", "Upload Video File"])

transcript = ""
title = st.text_input("Video Title")
description = st.text_area("Video Description (optional)")

# -------------------- YouTube Input --------------------
if option == "YouTube URL":
    url = st.text_input("Enter YouTube Video URL")

    if st.button("Fetch Transcript"):
        transcript = fetch_youtube_transcript(url)
        if transcript:
            st.success("Transcript extracted successfully!")
            st.text_area("Transcript", transcript, height=250)
        else:
            st.error("Failed to fetch transcript!")

# -------------------- Manual Upload --------------------
else:
    uploaded_video = st.file_uploader("Upload Video", type=["mp4", "mov", "mkv"])
    user_transcript = st.text_area("Enter Transcript (optional)")

    if uploaded_video and not user_transcript:
        st.warning("Transcript extraction from uploaded videos is not enabled yet.")
    
    transcript = user_transcript


# -------------------- Run Evaluation --------------------
if st.button("Evaluate Video"):
    if not transcript:
        st.error("Transcript is required!")
    elif not title:
        st.error("Title is required!")
    else:
        with st.spinner("Analyzing video..."):
            result = evaluate_video(title, description, transcript)

        st.subheader("📊 Evaluation Result")
        st.write(result)