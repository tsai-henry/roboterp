import streamlit as st
import os
import random
from PIL import Image
import pandas as pd
from datetime import datetime

# === Configuration ===
BASE_FOLDER = "/home/henrytsai/dhruv/baseline_images_correct_description"
FINETUNED_FOLDER = "/home/henrytsai/dhruv/finetuned_images_correct_description"
VOTE_LOG = "/home/henrytsai/dhruv/votes_baseline_vs_finetuned.csv"

# -----------------------------------------------------------
#                Helper utilities
# -----------------------------------------------------------
def list_image_ids(folder):
    """Return image basenames (no extension) that have both .jpg and .txt."""
    ids = []
    for fname in os.listdir(folder):
        if fname.lower().endswith(".jpg"):
            stem = os.path.splitext(fname)[0]
            if os.path.exists(os.path.join(folder, f"{stem}.txt")):
                ids.append(stem)
    return ids


def load_captions(image_id):
    """Return (baseline_caption, finetuned_caption) for a given image_id."""
    with open(os.path.join(BASE_FOLDER, f"{image_id}.txt")) as f:
        baseline = f.read().strip()
    with open(os.path.join(FINETUNED_FOLDER, f"{image_id}.txt")) as f:
        finetuned = f.read().strip()
    return baseline, finetuned


def get_random_sample(common_ids):
    """Sample an image_id plus shuffled caption order and return a dict."""
    image_id = random.choice(common_ids)
    baseline, finetuned = load_captions(image_id)

    # Prepare caption tuples (label, text) and shuffle once
    captions = [("Baseline", baseline), ("Finetuned", finetuned)]
    random.shuffle(captions)

    return {
        "image_id": image_id,
        "captions": captions,  # already shuffled; captions[0] is left
    }


# -----------------------------------------------------------
#                Data preparation
# -----------------------------------------------------------
base_ids = set(list_image_ids(BASE_FOLDER))
finetuned_ids = set(list_image_ids(FINETUNED_FOLDER))
common_ids = sorted(base_ids & finetuned_ids)

if not common_ids:
    st.error("Could not find any matching image +.txt pairs in both folders.")
    st.stop()

# Load existing votes (for counter only)
try:
    vote_df = pd.read_csv(VOTE_LOG) if os.path.exists(VOTE_LOG) else pd.DataFrame()
except Exception:
    vote_df = pd.DataFrame()
vote_count = len(vote_df)

# -----------------------------------------------------------
#                App UI
# -----------------------------------------------------------
st.title("VLM Caption Comparison Tool")
st.markdown(f"Total Votes Submitted: **{vote_count}**")

username = st.text_input("Enter your name:")

# ---- Persist / initialise current sample in session_state ----
if "sample" not in st.session_state:
    st.session_state.sample = get_random_sample(common_ids)

sample = st.session_state.sample
image_id = sample["image_id"]
captions = sample["captions"]          # [ (label,text), (label,text) ]

# ---- Display image + captions ----
img_path = os.path.join(BASE_FOLDER, f"{image_id}.jpg")  # image is the same in both dirs
st.image(Image.open(img_path), use_container_width=True, clamp=True)
st.markdown("### Compare the captions generated for this image:")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown(f"**Left Caption ({captions[0][0]}):**")
    st.write(captions[0][1])

with col2:
    st.markdown(f"**Right Caption ({captions[1][0]}):**")
    st.write(captions[1][1])

# ---- Voting UI ----
st.markdown("### Which caption is better?")
vote = st.radio("Select one:", ["Left", "Right", "Can't Tell"], index=None, key="vote_radio")

# -----------------------------------------------------------
#                Handle vote submission
# -----------------------------------------------------------
if st.button("Submit Vote"):
    if vote is not None and username.strip():
        # Determine which system the user picked
        voted_label = (
            captions[0][0] if vote == "Left"
            else captions[1][0] if vote == "Right"
            else "Can't Tell"
        )

        vote_data = {
            "timestamp": datetime.now().isoformat(),
            "user": username.strip(),
            "image_id": image_id,
            "left_caption_source": captions[0][0],
            "right_caption_source": captions[1][0],
            "left_caption_text": captions[0][1],
            "right_caption_text": captions[1][1],
            "vote": voted_label,
        }

        # Append to CSV (create if first time)
        vote_df = pd.concat([vote_df, pd.DataFrame([vote_data])], ignore_index=True)
        vote_df.to_csv(VOTE_LOG, index=False)

        # Prepare next sample and refresh UI
        st.session_state.sample = get_random_sample(common_ids)
        st.success("Vote submitted!")
        st.rerun()
    else:
        st.warning("Please enter your name and select an option before submitting.")
