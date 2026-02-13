<h1 align="center">
RoboTerp: Interpreting Vision Language Models for Robotic Control
</h1>

<p align="center">
  <a href="./RoboTerp.pdf"><strong>Paper PDF</strong></a>
</p>

We examine how fine-tuning Vision Language Models (VLMs) on robot trajectories changes their latent representations of the real world. Specifically, we focus on **PaliGemma 2 3B** and use **Sparse Autoencoders (SAEs)** to analyze feature distributions before and after fine-tuning on the **DROID** robot manipulation dataset.

## 📂 Repository Structure

The codebase is organized into three main stages: Baseline Analysis, Fine-Tuning, and Post-Fine-Tuning Analysis.

### 1. Data Preparation & Baseline
- **`make_droid_datasets.ipynb`**: Code to process the DROID dataset (RLDS format). It handles frame sampling (single frames vs. collated grids) to create datasets for fine-tuning and SAE training. Run this before fine-tuning or training the DROID SAE.
- **`imageNet_SAE.ipynb`**: Trains a Sparse Autoencoder on the frozen PaliGemma model using ImageNet-1K. This establishes baseline interpretable features for the vision encoder.

### 2. Fine-Tuning
- **`paligemma_finetuning_single.ipynb`**: Performs fine-tuning of PaliGemma on the processed DROID dataset.
  - Supports selecting different PaliGemma variants.
  - Allows customization of image collation (e.g., single frame vs. 2x2 grids).
  - **Note:** Ensure the image grid settings match those used in `make_droid_datasets`.

### 3. Robotic SAE Analysis
- **`droid_SAE_runs.ipynb`**: Trains a second SAE on the activations of the *fine-tuned* PaliGemma model using DROID data.
  - Includes visualization tools to inspect latent features.
  - Used to compare feature sparsity and semantic meaning against the baseline.

---

##  Evaluation Tools

We provide two Streamlit applications to conduct blind, side-by-side evaluations of model performance and feature quality.

### 1. Image Comparison Tool (`sae_comparison_streamlit.py`)

This tool presents two randomly selected images — one from a base model and one from a fine-tuned model — and asks users to vote for the better one (or the one that maximally activates a specific feature).

**Key Features:**
- Randomized blind comparison.
- Vote logging with timestamps.

**Configuration:**
Update paths in the script:
```python
BASE_FOLDER = "/path/to/base/images"
FINETUNED_FOLDER = "/path/to/finetuned/images"
VOTE_LOG = "/path/to/vote_log.csv"
```
**Run:**
```bash
streamlit run sae_comparison_streamlit.py
```

### 2. Caption Comparison Tool (`finetuning_comparison_streamlit.py`)

This tool presents a single image along with two captions (from base and fine-tuned models) and asks the user to vote on which caption better describes the image. Captions are matched to the same image ID and randomized left/right.

**Key Features:**
- Side-by-side blind caption comparison.
- Randomizes left/right placement to prevent bias.
- Supports `.jpg` and `.txt` file pairs.

**Configuration:**
Update paths in the script:
```python
BASE_FOLDER = "/path/to/base/captions_and_images"
FINETUNED_FOLDER = "/path/to/finetuned/captions_and_images"
VOTE_LOG = "/path/to/vote_log.csv"
```
**Run:**
```bash
streamlit run finetuning_comparison_streamlit.py
```
