# Model Choice Demo

## What's in this folder?
This folder contains a basic chatbot example where you can choose **which LLM you interact with**.

- `chat_with_model_choice.py`: A basic chat app using OpenRouter. The "_Available models_" list blends OpenRouter's pricing with an LM Arena quality score (see below) to show an estimated "LM Arena Score" and "Value Estimate" (cost, scaled by quality) per model.

- `lmarena_download.py`: Downloads an LM Arena leaderboard snapshot (`overall` category) from the official [lmarena-ai/leaderboard-dataset](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset) on Hugging Face, and saves it as `lmarena_<subset>_<date>.csv`. Run it whenever you want to refresh the scores:
  ```bash
  python3 lmarena_download.py --subset text_style_control   # default
  python3 lmarena_download.py --subset webdev
  python3 lmarena_download.py --subset agent
  ```
  `chat_with_model_choice.py` picks up whichever CSV matches its `LMARENA_SUBSET` constant (loads the most recent dated file for that subset). Only one subset is used at a time — they're on different scales and aren't blended.

## Configuration

To install the necessary libraries, use `pip install -r requirements.txt`

Please create an `.env` file with the same structure as the provided `.env.example` file, and enter your personal **API key** therein.

Before first use (or whenever you want fresher scores), run `lmarena_download.py` to (re)generate the CSV for the subset configured in `chat_with_model_choice.py` (`LMARENA_SUBSET`, default `text_style_control`). Models OpenRouter doesn't have pricing for are skipped automatically (they never enter the OpenRouter-driven model list); OpenRouter models with no matching LM Arena score just show "N/A" for score/value.

## Use

1.  Run the `chat_with_model_choice.py` script from the terminal (or your IDE). This will start a Gradio interface.
2.  To switch to another LLM provider, click any of the rows in the "_Available models_" list. You can sort the list by name, price, context length, LM Arena score, or value estimate.

_For more info regarding how Gradio works, please refer to the general README in this repository._

## Screenshots

`chat_with_model_choice.py`

![model_choice_1.png](../../assets/screenshots/model_choice_1.png)
