import os
import sys
from typing import Optional, Literal

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

# Get the absolute path to the project root
sys.path.append('../../')

from demos.components.open_router_client import OpenRouterClient

class Summarizer:
    def __init__(self, api_key: str, model_name: str = 'openai/gpt-4o-mini'):
        self.client = OpenRouterClient(api_key=api_key, model_name=model_name)

    def generate_summary(
        self,
        text: str,
        summary_type: Literal["abstractive", "extractive", "query_focused"] = "abstractive",
        length: Literal["short", "medium", "detailed"] = "medium",
        query: Optional[str] = None
    ) -> Optional[str]:
        """
        Generates a summary of the given text using an LLM.

        Args:
            text: The text to summarize.
            summary_type: The type of summary to generate.
            length: The desired length of the summary.
            query: An optional query for query-focused summaries.

        Returns:
            The generated summary, or None if summarization fails.
        """
        system_prompt = self._get_system_prompt(summary_type, length, query)
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Please summarize the following text:\n\n{text}"}
        ]

        try:
            response = self.client.create_completions_stream(messages, stream=False)
            summary = response.choices[0].message.content
            return summary
        except Exception as e:
            print(f"Error generating summary: {e}")
            return None

    def _get_system_prompt(
        self,
        summary_type: Literal["abstractive", "extractive", "query_focused"],
        length: Literal["short", "medium", "detailed"],
        query: Optional[str]
    ) -> str:
        """
        Generates the system prompt for the LLM based on summary type and length.
        """
        prompt = f"You are a highly skilled summarization AI. Your task is to provide a {length} summary."

        if summary_type == "abstractive":
            prompt += " The summary should be abstractive, meaning you should rephrase and synthesize the information."
        elif summary_type == "extractive":
            prompt += " The summary should be extractive, meaning you should select key sentences directly from the text."
        elif summary_type == "query_focused" and query:
            prompt += f" The summary should be focused on answering the following query: '{query}'."
        elif summary_type == "query_focused" and not query:
            raise ValueError("Query must be provided for query_focused summary type.")

        prompt += " Ensure the summary is concise, accurate, and captures the main points."

        if length == "short":
            prompt += " Keep the summary very brief, around 1-2 sentences."
        elif length == "medium":
            prompt += " Aim for a summary of 3-5 sentences."
        elif length == "detailed":
            prompt += " Provide a comprehensive summary, covering all important aspects, around 5-10 sentences."

        return prompt

if __name__ == '__main__':
    # Example Usage (replace with your actual API key)
    # You might need to set OPENROUTER_API_KEY in your environment variables
    # or pass it directly to the Summarizer constructor.
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("OPENROUTER_API_KEY environment variable not set. Cannot run example.")
    else:
        summarizer = Summarizer(api_key=api_key)

        sample_text = """
        Quantum computing is a new type of computing that harnesses the phenomena of quantum mechanics, such as superposition and entanglement, to perform calculations. Unlike classical computers that store information as bits (0s or 1s), quantum computers use qubits, which can exist in multiple states simultaneously. This allows quantum computers to process vast amounts of information in parallel, potentially solving problems that are intractable for even the most powerful supercomputers. Applications include drug discovery, materials science, financial modeling, and breaking modern encryption. However, building stable and error-free quantum computers is a significant engineering challenge, and the technology is still in its early stages of development.
        """

        print("--- Abstractive Medium Summary ---")
        abstractive_summary = summarizer.generate_summary(sample_text, summary_type="abstractive", length="medium")
        print(abstractive_summary)

        print("\n--- Extractive Short Summary ---")
        extractive_summary = summarizer.generate_summary(sample_text, summary_type="extractive", length="short")
        print(extractive_summary)

        print("\n--- Query-Focused Detailed Summary (What are the challenges?) ---")
        query_focused_summary = summarizer.generate_summary(
            sample_text, summary_type="query_focused", length="detailed", query="What are the challenges of quantum computing?"
        )
        print(query_focused_summary)

        print("\n--- Summarization Failure Example (Invalid Query) ---")
        failed_summary = summarizer.generate_summary(
            sample_text, summary_type="query_focused", length="detailed"
        )
        print(f"Failed summary result: {failed_summary}")
