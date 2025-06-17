# OpenRouter Multimodal Image Analysis Demo

This Streamlit application provides a chat interface that leverages the OpenRouter API to process both text and image inputs. It allows users to dynamically select from a list of image-capable models, view detailed information about each model, and interact with them in a multimodal chat environment. Models are sorted by their capabilities based on an external CSV ranking.

## Key Features

- **Multimodal Chat:** Interact with AI models using both text and image inputs.
- **Image Upload:** Easily upload images via a drag-and-drop interface.
- **Dynamic Model Selection:** Choose from a curated list of OpenRouter models that support multimodal input.
- **Capability-Based Sorting:** Models are sorted by their performance scores from an external ranking, helping you identify the most capable options.
- **Detailed Model Information:** View comprehensive details for the selected model, including provider, pricing (per million tokens), context length, and maximum completion tokens.

## Prerequisites

Before running this demo, ensure you have the following:

- **Python:** Version 3.8 or higher is recommended.
- **OpenRouter API Key:** You will need an API key from [OpenRouter.ai](https://openrouter.ai/).
- **Model Ranking CSV:** The demo relies on a CSV file named `lmarena_vision_250616.csv` which contains ranking data for vision-enabled models. This file should be placed in the same directory as the application.

## Setup and Installation

1.  **Navigate to the Demo Directory:**
    Open your terminal or command prompt and navigate to the `demos/image_analysis` directory within this project:

    ```bash
    cd demos/image_analysis
    ```

2.  **Install Dependencies:**
    Install the required Python packages using pip:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  **Set up OpenRouter API Key:**
    Create a new file named `.env` in the `demos/image_analysis` directory (if it doesn't already exist). Add your OpenRouter API key to this file in the following format:

    ```
    OPENROUTER_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    ```

    Replace `sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` with your actual OpenRouter API key.

2.  **Place the CSV File:**
    Ensure the `lmarena_vision_250616.csv` file is located directly within the `demos/image_analysis` directory.

## Running the Demo

Once configured, you can run the Streamlit application:

```bash
streamlit run image_analysis.py
```

This command will open the Streamlit application in your default web browser.

## Usage Guide

1.  **Select a Model:** Use the dropdown menu in the sidebar to choose an AI model. The models are sorted by their capability scores.
2.  **Type a Prompt:** Enter your text query in the chat input box at the bottom.
3.  **Upload an Image:** Use the "Upload an image" file uploader to add an image to your conversation. The model will then be able to analyze both your text and the image.
4.  **View Model Details:** The sidebar will display detailed information about the currently selected model, including its pricing and capabilities.
