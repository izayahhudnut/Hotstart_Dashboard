from typing import Any, Dict, List, Type
import instructor
from anthropic import Anthropic
from config.setting import get_settings
from openai import OpenAI
from pydantic import BaseModel, Field
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from linkedin_api import Linkedin
import re


def scrape_website(url: str) -> str:
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script and style elements
        for script in soup(['script', 'style']):
            script.decompose()

        # Get text and clean it
        text = ' '.join(soup.stripped_strings)
        return text[:2000]
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return ""


class LLMFactory:
    def __init__(self, provider: str):
        self.provider = provider
        self.settings = getattr(get_settings(), provider)
        self.client = self._initialize_client()

    def _initialize_client(self) -> Any:
        client_initializers = {
            "openai": lambda s: instructor.from_openai(OpenAI(api_key=s.api_key)),
            "anthropic": lambda s: instructor.from_anthropic(
                Anthropic(api_key=s.api_key)
            ),
            "llama": lambda s: instructor.from_openai(
                OpenAI(base_url=s.base_url, api_key=s.api_key),
                mode=instructor.Mode.JSON,
            ),
        }

        initializer = client_initializers.get(self.provider)
        if initializer:
            return initializer(self.settings)
        raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def create_completion(
        self, response_model: Type[BaseModel], messages: List[Dict[str, str]], **kwargs
    ) -> Any:
        completion_params = {
            "model": kwargs.get("model", self.settings.default_model),
            "temperature": kwargs.get("temperature", self.settings.temperature),
            "max_retries": kwargs.get("max_retries", self.settings.max_retries),
            "max_tokens": kwargs.get("max_tokens", self.settings.max_tokens),
            "response_model": response_model,
            "messages": messages,
        }
        return self.client.chat.completions.create(**completion_params)


class LeadList(BaseModel):
    """This is a list of warm leads for my business. We want to sell companies on a product and we want to rank them 1-5 on how likely they are to buy the product"""
    reasoning: str = Field(description="A short title of the curated newsletter")
    score: int = Field(description="A score from 1-5 ranking how likely the company is to buy the product", ge=0, le=5)
    data_message: str = Field(description="A message focusing on data-driven benefits, such as how our product can help the client make money")
    sentiment_message: str = Field(description="A message highlighting success stories with similar companies")
    connection_message: str = Field(description="A message attempting to establish a personal connection between the user and the potential client")


def extract_linkedin_username(url):
    # Regular expression to match LinkedIn URLs and extract the username
    pattern = r'linkedin\.com/in/([^/]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None


def process_lead(First_name: str, Last_name: str, email: str, website: str, title: str, user_info: str, linkedin_url: str) -> Dict:
    # Scrape website content
    website_content = scrape_website(website)
    
    # Extract LinkedIn username
    linkedin_username = extract_linkedin_username(linkedin_url)
    if not linkedin_username:
        print(f"Invalid LinkedIn URL: {linkedin_url}")
        return {
            "name": f"{First_name} {Last_name}",
            "score": 0,
            "reasoning": "Invalid LinkedIn URL",
            "data_message": "",
            "sentiment_message": "",
            "connection_message": ""
        }
    
    # Authenticate using any LinkedIn user account credentials
    api = Linkedin('admin@dor15.com', 'L0R9>m7C%Yj8s.JRfymr')
    try:
        # GET a profile
        profile = api.get_profile(linkedin_username)
    except Exception as e:
        print(f"Error fetching LinkedIn profile: {str(e)}")
        profile = {}

    # Prepare messages for LLM
    messages = [
        {
            "role": "system",
            "content": f"""
You are a smart AI specialized in writing cold email copy. Your task is to craft personalized, compelling emails based on a list of contacts and their associated information (name, email, title, Linkedin URL, company website content). Additionally, you will incorporate details about the person sending the emails to establish a meaningful connection.

Objectives:
- Identify potential connections between the sender and recipient, prioritizing shared domains (rank these as a 5 for relevance).
- If the website content is a empty string mark this as 0 out of 5. If you give a targert a 0 it should out wieght any other factors. Only tell the user this if the score is 0.
- If the linkedin link is does not exist say in the resoning portion that we got the information from the website 
- If the title in the Recipent information that i'm giving you in the prompt is different from the title in the linkedin profile. Let me know in the reasononing and give it a 3
- Ensure the email resonates by addressing the recipient's needs or problems based on company website content.
- Double-check all details to ensure accuracy. If no email matches exist, focus on leveraging other provided information to personalize the message effectively.

Input:
- Recipient Information:
  - Name: {First_name} {Last_name}
  - Email: {email}
  - Title: {title}
  - Website: {website}
  - Website Content: {website_content}
  - LinkedIn Profile: {profile}
"""
        },
        {
            "role": "user",
            "content": f" Here is the person you are writing the content for infromation: {user_info}" 
        }
    ]

    # Generate the LeadList
    llm = LLMFactory("openai")
    try:
        completion = llm.create_completion(response_model=LeadList, messages=messages)
        return {
            "name": f"{First_name} {Last_name}",
            "score": completion.score,
            "reasoning": completion.reasoning,
            "data_message": completion.data_message,
            "sentiment_message": completion.sentiment_message,
            "connection_message": completion.connection_message
        }
    except Exception as e:
        print(f"Error processing {First_name}: {str(e)}")
        return {
            "name": f"{First_name} {Last_name}",
            "score": 0,
            "reasoning": f"Error: {str(e)}",
            "data_message": "",
            "sentiment_message": "",
            "connection_message": ""
        }


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


def process_leads_from_csv(csv_path: str, user_info: str) -> None:
    # Read CSV file
    df = pd.read_csv(csv_path)

    # Normalize and map required columns
    required_columns = ['First Name', 'Last Name', 'Email', 'Website', 'Title', 'Person Linkedin URL']
    df = map_columns(df, required_columns)

    output_path = 'lead_scores_with_details.csv'
    results = []

    # Process each lead
    for index, row in df.iterrows():
        print(f"Processing row {index + 1} of {len(df)}: {row['First Name']} {row['Last Name']}")  # Display progress
        result = process_lead(
            First_name=row['First Name'],
            Last_name=row['Last Name'],
            email=row['Email'],
            website=row['Website'],
            title=row['Title'],
            user_info=user_info,
            linkedin_url=row['Person Linkedin URL']
        )
        
        # Add results to the original row
        row['Score'] = result['score']
        row['Reasoning'] = result['reasoning']
        row['Data Message'] = result['data_message']
        row['Sentiment Message'] = result['sentiment_message']
        row['Connection Message'] = result['connection_message']
        results.append(row)

        # Save progress every 10 contacts
        if (index + 1) % 10 == 0 or (index + 1) == len(df):
            temp_results_df = pd.DataFrame(results)
            temp_results_df.to_csv(output_path, index=False)
            print(f"Progress saved to {output_path} after processing {index + 1} contacts.")

        # Add delay to avoid rate limiting
        time.sleep(1)

    print(f"\nFinal results saved to {output_path}")

    # Print summary
    print("\nTop 5 Leads:")
    final_results_df = pd.DataFrame(results).sort_values('Score', ascending=False)
    for _, row in final_results_df.head().iterrows():
        print(f"\nContact: {row['First Name']} {row['Last Name']}")
        print(f"Score: {row['Score']}/5")
        print(f"Reasoning: {row['Reasoning']}")

if __name__ == "__main__":
    # Example usage
    user_info = """My name is Izayah, I work at PRI I am trying to sell small businesses
                   on AI automations. We target STL companies.  I went to college at the university of Oklahoma Here is my CRM system. maggie.hudnut@tpg.com"""

    try:
        process_leads_from_csv('apollo-contacts-export 1.csv', user_info)
    except Exception as e:
        print(f"Error processing CSV: {str(e)}")
