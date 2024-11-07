# Model Choice Demo
TransformAI

## What's in this folder?
This folder contains a basic chatbot example where you can choose **which LLM you interact with**.

- `chat_with_model_choice.py` a basic chat app using OpenRouter

- `or_pricing.py` a basic utility method querying the OpenRouter API for information on specific models.
  (Make edits here if you want to include or exclude specific types of models.)


## Configuration
To install the necessary libraries use `pip install -r requirements.txt`

Please create an `.env` file with the same structure as the provided `.env.example` file, 
and enter your personal **keys** and **endpoints** therein.

## Use
Run the python script from the terminal (or your IDE).

To switch to another LLM provider just click any of the rows in the "_Available models_" list.
(Sort on name / price / context length if convenient)

_For more info regarding how Gradio works, please refer to the general README in this repository._

## Screenshots

`chat_with_model_choice.py`

![model_choice_1.png](../../assets/screenshots/model_choice_1.png)
