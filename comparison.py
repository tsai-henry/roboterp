import streamlit as st
import os
import random
from PIL import Image
import pandas as pd
from datetime import datetime

# === Configuration ===
BASE_FOLDER   = "/home/henrytsai/dhruv/baseline_images_correct_description"
FINETUNED_FOLDER = "/home/henrytsai/dhruv/finetuned_images_correct_description"
VOTE_LOG      = "/home/henrytsai/dhruv/votes_baseline_vs_finetuned.csv"

# -----------------------------------------------------------
#                Helper utilities
# -----------------------------------------------------------
def list_image_ids(folder):
    """Return basenames (no extension) that have both .jpg and .txt."""
    return [
        os.path.splitext(f)[0]
        for f in os.listdir(folder)
        if f.lower().endswith(".jpg")
        and os.path.exists(os.path.join(folder, f"{os.path.splitext(f)[0]}.txt"))
    ]


def load_captions(image_id):
    """Return (baseline_caption, finetuned_caption)."""
    with open(os.path.join(BASE_FOLDER,     f"{image_id}.txt")) as f:
        baseline  = f.read().strip()
    with open(os.path.join(FINETUNED_FOLDER, f"{image_id}.txt")) as f:
        finetuned = f.read().strip()
    return baseline, finetuned


def get_random_sample(common_ids):
    """
    Pick a random image id and shuffle which caption (baseline / finetuned)
    goes on the left vs right.  Returns a dict of the form:

    {
        "image_id": str,
        "left":  {"source": "Baseline" | "Finetuned", "text": str},
        "right": {"source": "Baseline" | "Finetuned", "text": str},
    }
    """
    image_id = random.choice(common_ids)
    baseline_txt, finetuned_txt = load_captions(image_id)

    # Build list of caption dicts and shuffle in‑place once
    entries = [
        {"source": "Baseline",  "text": baseline_txt},
        {"source": "Finetuned", "text": finetuned_txt},
    ]
    random.shuffle(entries)

    return {"image_id": image_id, "left": entries[0], "right": entries[1]}

# -----------------------------------------------------------
#                Data preparation
# -----------------------------------------------------------
base_ids      = set(list_image_ids(BASE_FOLDER))
finetuned_ids = set(list_image_ids(FINETUNED_FOLDER))
common_ids    = sorted(base_ids & finetuned_ids)

if not common_ids:
    st.error("Could not find any matching image +.txt pairs in both folders.")
    st.stop()

# Load existing votes (counter only, ignore read errors)
try:
    vote_df = pd.read_csv(VOTE_LOG) if os.path.exists(VOTE_LOG) else pd.DataFrame()
except Exception:
    vote_df = pd.DataFrame()
vote_count = len(vote_df)

# -----------------------------------------------------------
#                App UI
# -----------------------------------------------------------
st.title("VLM Caption Comparison Tool (Blind)")
st.markdown(f"Total Votes Submitted: **{vote_count}**")

username = st.text_input("Enter your name:")

# ---- Persist / initialise current sample in session_state ----
if "sample" not in st.session_state:
    st.session_state.sample = get_random_sample(common_ids)

sample   = st.session_state.sample
image_id = sample["image_id"]

# ---- Display image + captions ----
img_path = os.path.join(BASE_FOLDER, f"{image_id}.jpg")   # same image in both dirs
st.image(Image.open(img_path), use_container_width=True, clamp=True)
st.markdown("### Compare the two captions for this image:")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Left Caption:**")
    st.write(sample["left"]["text"])

with col2:
    st.markdown("**Right Caption:**")
    st.write(sample["right"]["text"])

# ---- Voting UI ----
st.markdown("### Which caption is better?")
vote = st.radio(
    "Select one:",
    ["Left", "Right", "Can't Tell"],
    index=None,
    key="vote_radio"
)

# -----------------------------------------------------------
#                Handle vote submission
# -----------------------------------------------------------
if st.button("Submit Vote"):
    if vote is not None and username.strip():
        # Map vote back to hidden source for logging
        voted_source = (
            sample["left" ]["source"] if vote == "Left"
            else sample["right"]["source"] if vote == "Right"
            else "Can't Tell"
        )

        vote_data = {
            "timestamp": datetime.now().isoformat(),
            "user":      username.strip(),
            "image_id":  image_id,
            "left_caption_source":  sample["left" ]["source"],
            "right_caption_source": sample["right"]["source"],
            "left_caption_text":    sample["left" ]["text"],
            "right_caption_text":   sample["right"]["text"],
            "vote": voted_source,
        }

        # Append to CSV (create if needed)
        vote_df = pd.concat([vote_df, pd.DataFrame([vote_data])], ignore_index=True)
        vote_df.to_csv(VOTE_LOG, index=False)

        # Draw next random sample and refresh
        st.session_state.sample = get_random_sample(common_ids)
        st.success("Vote submitted!")
        st.rerun()
    else:
        st.warning("Please enter your name *and* select an option before submitting.")
