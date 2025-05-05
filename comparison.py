import streamlit as st
import os
import random
from PIL import Image
import pandas as pd
from datetime import datetime

# === Configuration ===
BASE_FOLDER = "/home/henrytsai/ishan/sae_trials/collage/100_episodes"
FINETUNED_FOLDER = "/home/henrytsai/ishan/sae_trials/collage/100_episodes_finetuned"
VOTE_LOG = "/home/henrytsai/henry/feature_votes.csv"

# === Load image names ===
base_images = sorted(os.listdir(BASE_FOLDER))
finetuned_images = sorted(os.listdir(FINETUNED_FOLDER))

if not base_images or not finetuned_images:
    st.error("Both image folders must contain at least one image.")
    st.stop()

# === Load vote count ===
vote_count = 0
if os.path.exists(VOTE_LOG):
    try:
        vote_df = pd.read_csv(VOTE_LOG)
        vote_count = len(vote_df)
    except Exception:
        vote_df = pd.DataFrame()
        vote_count = 0
else:
    vote_df = pd.DataFrame()

# === Header ===
st.title("VLM Image Comparison Tool")
st.markdown(f"Total Votes Submitted: **{vote_count}**")

# === User name input ===
username = st.text_input("Enter your name:")

# === Random image selection ===
base_image = random.choice(base_images)
finetuned_image = random.choice(finetuned_images)
base_path = os.path.join(BASE_FOLDER, base_image)
finetuned_path = os.path.join(FINETUNED_FOLDER, finetuned_image)

# === Randomize display order ===
images = [("Base", base_image, base_path), ("Finetuned", finetuned_image, finetuned_path)]
random.shuffle(images)

# === Display side-by-side ===
st.markdown("Compare the images and vote for the better one.")

col1, col2 = st.columns([1, 1])

with col1:
    st.image(Image.open(images[0][2]), use_container_width=True, clamp=True)

with col2:
    st.image(Image.open(images[1][2]), use_container_width=True, clamp=True)

# === Voting form ===
st.markdown("### Which image is better?")
vote = st.radio("Select one:", ["Left", "Right", "Can't Tell"], index=None, key="vote_radio")

if st.button("Submit Vote"):
    if vote is not None and username.strip():
        # Map vote back to base or finetuned
        if vote == "Left":
            voted_label = images[0][0]
        elif vote == "Right":
            voted_label = images[1][0]
        else:
            voted_label = "Can't Tell"

        vote_data = {
            "timestamp": datetime.now().isoformat(),
            "user": username.strip(),
            "base_image": base_image,
            "finetuned_image": finetuned_image,
            "left_image": images[0][0],
            "right_image": images[1][0],
            "vote": voted_label
        }

        # Append to CSV
        vote_df = pd.concat([vote_df, pd.DataFrame([vote_data])], ignore_index=True)
        vote_df.to_csv(VOTE_LOG, index=False)

        st.success("Vote submitted!")
        st.rerun()
    else:
        st.warning("Please enter your name and select an option before submitting.")
