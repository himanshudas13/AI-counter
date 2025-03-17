import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_huggingface import HuggingFaceEndpoint
from huggingface_hub import InferenceClient
import json
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Load environment variables
load_dotenv()
hf_api_key = os.getenv("HUGGINGFACEHUB_API_TOKEN")

# Set up Hugging Face inference
endpoint_url = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"

client = InferenceClient(token=hf_api_key)

# Define a structured prompt template
prompt = PromptTemplate.from_template(
    "Extract structured booking details from: {user_input}\n"
    "Format as JSON with keys: name, phone, from, to, date."
)

# LangChain-compatible LLM
llm = HuggingFaceEndpoint(
    endpoint_url=endpoint_url,
    huggingfacehub_api_token=hf_api_key
)

# Use RunnableSequence instead of LLMChain
llm_chain = prompt | llm

# User input
user_input = "Book a ticket for Himanshu from Bangalore to Chennai on March 18. Contact: 1234567890."

# Run inference using `.invoke()`
response = llm_chain.invoke({"user_input": user_input})

try:
    # Ensure the response is valid JSON
    extracted_data = json.loads(response)
    print("Extracted Booking Details:", extracted_data)
except json.JSONDecodeError:
    print("Error: Failed to parse LLM response. Please try again.")
from web.api import MyTravels
from tests import print_table
details=extracted_data 
if details:
        travel_agent = MyTravels()
        result = travel_agent.book_ticket(
            name=details["name"],
            phone=details["phone"],
            source=details["from"],
            destination=details["to"],
            date=details["date"]
        )
        print_table()