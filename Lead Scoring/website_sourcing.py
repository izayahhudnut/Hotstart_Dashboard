import pandas as pd
import requests
from bs4 import BeautifulSoup
from time import sleep
from typing import Any, Dict, List, Type
from pydantic import BaseModel, Field
from config.setting import get_settings
import instructor
from anthropic import Anthropic
from openai import OpenAI

# Function to scrape website content
def scrape_website(url: str) -> str:
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script and style elements
        for script in soup(['script', 'style']):
            script.decompose()

        # Extract and clean text
        text = ' '.join(soup.stripped_strings)
        return text[:2000]
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""

# LLM Factory for handling multiple LLM providers
class LLMFactory:
    def __init__(self, provider: str):
        self.provider = provider
        self.settings = getattr(get_settings(), provider)
        self.client = self._initialize_client()

    def _initialize_client(self) -> Any:
        client_initializers = {
            "openai": lambda s: instructor.from_openai(OpenAI(api_key=s.api_key)),
            "anthropic": lambda s: instructor.from_anthropic(Anthropic(api_key=s.api_key)),
        }

        initializer = client_initializers.get(self.provider)
        if initializer:
            return initializer(self.settings)
        raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def create_completion(self, response_model: Type[BaseModel], messages: List[Dict[str, str]], **kwargs) -> Any:
        completion_params = {
            "model": kwargs.get("model", self.settings.default_model),
            "temperature": kwargs.get("temperature", self.settings.temperature),
            "max_retries": kwargs.get("max_retries", self.settings.max_retries),
            "max_tokens": kwargs.get("max_tokens", self.settings.max_tokens),
            "response_model": response_model,
            "messages": messages,
        }
        return self.client.chat.completions.create(**completion_params)

# Response Model
class VCClassification(BaseModel):
    decision: str = Field(description="Yes or No indicating if this is a traditional VC firm.")
    reasoning: str = Field(description="Reasoning behind the decision.")

# Process a single lead
def process_lead(first_name: str, last_name: str, website: str, llm: LLMFactory) -> Dict:
    website_content = scrape_website(website)

    if not website_content:
        return {
            "name": f"{first_name} {last_name}",
            "decision": "No",
            "reasoning": "Website content could not be retrieved."
        }

    messages = [
        {
            "role": "system",
            "content": """
You are an AI trained to classify investment firms. Based on the provided website content, decide if the firm is a traditional VC firm or more of an LP/general investor. A traditional VC firm primarily invests in startups.

Output:
- Decision: Yes or No
- Reasoning: Explain the decision concisely.
"""
        },
        {
            "role": "user",
            "content": f"Website Content: {website_content}"
        }
    ]

    try:
        completion = llm.create_completion(response_model=VCClassification, messages=messages)
        return {
            "name": f"{first_name} {last_name}",
            "decision": completion.decision,
            "reasoning": completion.reasoning
        }
    except Exception as e:
        print(f"Error processing {first_name}: {e}")
        return {
            "name": f"{first_name} {last_name}",
            "decision": "Error",
            "reasoning": str(e)
        }

# Map and normalize columns
def map_columns(df: pd.DataFrame, required_columns: List[str]) -> pd.DataFrame:
    column_mapping = {col.lower().replace(' ', ''): col for col in df.columns}
    mapped_df = {}

    for required_col in required_columns:
        lowercase_col = required_col.lower().replace(' ', '')
        if lowercase_col in column_mapping:
            mapped_df[required_col] = df[column_mapping[lowercase_col]]
        else:
            raise ValueError(f"Missing required column: {required_col}")

    return pd.DataFrame(mapped_df)

# Process leads from a CSV file
def process_leads_from_csv(csv_path: str) -> None:
    df = pd.read_csv(csv_path)
    required_columns = ['First Name', 'Last Name', 'Website']
    df = map_columns(df, required_columns)

    llm = LLMFactory("openai")
    results = []

    for index, row in df.iterrows():
        print(f"Processing {row['First Name']} {row['Last Name']}...")
        result = process_lead(
            first_name=row['First Name'],
            last_name=row['Last Name'],
            website=row['Website'],
            llm=llm
        )
        results.append(result)
        sleep(1)  # Avoid rate limiting

    results_df = pd.DataFrame(results)
    results_df.to_csv('classified_leads.csv', index=False)
    print("Processing complete. Results saved to 'classified_leads.csv'.")

# Example usage
if __name__ == "__main__":
    process_leads_from_csv("leads.csv")
