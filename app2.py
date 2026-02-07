import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re

# -----------------------------
# 🔑 YOUTUBE API KEY
# -----------------------------
API_KEY = "AIzaSyCkSZ_bxy5tsond0PZM7dw31A_9q5fZuGk"
youtube = build("youtube", "v3", developerKey=API_KEY)

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="YouTube Live Analytics",
    page_icon="🔥",
    layout="wide"
)

# -----------------------------
# CUSTOM CSS (Premium UI)
# -----------------------------
st.markdown("""
<style>
.main {
    background-color: #0E1117;
}
h1 {
    text-align: center;
    color: #FF4B4B;
}
.metric-card {
    background-color: #1c1f26;
    padding: 20px;
    border-radius: 15px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🔥 YouTube Live Analytics Dashboard</h1>", unsafe_allow_html=True)

st.write("Paste any YouTube Channel URL below 👇")

# -----------------------------
# INPUT CHANNEL URL
# -----------------------------
channel_url = st.text_input("Enter Channel URL")

def extract_channel_id(url):
    if "channel/" in url:
        return url.split("channel/")[1]
    return None

if channel_url:

    try:
        channel_id = extract_channel_id(channel_url)

        if not channel_id:
            st.error("Please enter a valid channel URL (must contain /channel/)")
            st.stop()

        # -----------------------------
        # FETCH CHANNEL DETAILS
        # -----------------------------
        channel_data = youtube.channels().list(
            part="snippet,statistics",
            id=channel_id
        ).execute()["items"][0]

        channel_name = channel_data["snippet"]["title"]
        subscribers = int(channel_data["statistics"].get("subscriberCount", 0))
        total_views = int(channel_data["statistics"].get("viewCount", 0))
        total_videos = int(channel_data["statistics"].get("videoCount", 0))

        st.success(f"Channel Found: {channel_name} ✅")

        # -----------------------------
        # KPI SECTION
        # -----------------------------
        st.markdown("## 📊 Channel Overview")
        col1, col2, col3 = st.columns(3)

        col1.metric("👥 Subscribers", f"{subscribers:,}")
        col2.metric("👀 Total Views", f"{total_views:,}")
        col3.metric("🎥 Total Videos", f"{total_videos:,}")

        # -----------------------------
        # FETCH TOP 10 VIDEOS
        # -----------------------------
        video_search = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            order="viewCount",
            type="video",
            maxResults=10
        ).execute()

        video_ids = [item["id"]["videoId"] for item in video_search["items"]]

        videos = youtube.videos().list(
            part="snippet,statistics",
            id=",".join(video_ids)
        ).execute()["items"]

        rows = []
        for video in videos:
            rows.append({
                "Title": video["snippet"]["title"],
                "Views": int(video["statistics"].get("viewCount", 0)),
                "Likes": int(video["statistics"].get("likeCount", 0)),
                "Comments": int(video["statistics"].get("commentCount", 0))
            })

        df = pd.DataFrame(rows)
        df = df.sort_values("Views", ascending=True)

        # -----------------------------
        # CHART SECTION
        # -----------------------------
        st.markdown("## 🔥 Top 10 Most Viewed Videos")

        col_left, col_right = st.columns([1.2, 1])

        with col_left:
            plt.figure(figsize=(8,5))
            plt.barh(df["Title"], df["Views"])
            plt.xlabel("Views")
            plt.tight_layout()
            st.pyplot(plt)
            plt.clf()

        with col_right:
            plt.figure(figsize=(6,4))
            plt.bar(df["Title"], df["Likes"])
            plt.xticks(rotation=90)
            plt.ylabel("Likes")
            plt.tight_layout()
            st.pyplot(plt)
            plt.clf()

        # -----------------------------
        # TABLE
        # -----------------------------
        st.markdown("## 📄 Video Details")
        st.dataframe(df.sort_values("Views", ascending=False), use_container_width=True)

    except HttpError as e:
        st.error(f"API Error: {e}")
