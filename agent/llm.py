from typing import TypedDict, Optional
import os
import json
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEndpoint
from huggingface_hub import InferenceClient
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from web.api import MyTravels
from tests import print_table

# Load environment variables
load_dotenv()

# Define a structured dictionary type for ticket details
class TicketDetails(TypedDict, total=False):
    name: str
    phone: str
    from_: str  # "from" is a keyword in Python, so use "from_" instead
    to: str
    date: str

class TicketAI:
    def __init__(self):
        self.hf_api_key = os.getenv("HUGGINGFACEHUB_API_TOKEN")
        self.endpoint_url = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"
        self.client = InferenceClient(token=self.hf_api_key)
        
        # Adjusted prompt with chat history
        self.prompt_template = PromptTemplate.from_template(
            "Remember that do not assume any information on your own always ask for required information explicitly."
            "Do not return blank messages,request only the missing information."
            "extract structured booking details from the latest user input and conversation history.\n\n"
            "Chat History:\n{chat_history}\n\n"
            "Latest Input:\n{user_input}\n\n"
            "Respond in a structured format with keys: name, phone, from, to, date. "
            "If any details are missing, request only the missing information."
            
        )
        
        self.llm = HuggingFaceEndpoint(
            endpoint_url=self.endpoint_url,
            huggingfacehub_api_token=self.hf_api_key
        )
        
        self.llm_chain = self.prompt_template | self.llm
        self.chat_history = []  # Store chat history
        self.chat_history.clear()

    def parse_ticket_details(self, response: str) -> TicketDetails:
        """Parses LLM output and ensures it matches the TicketDetails format."""
        try:
            parsed_data = json.loads(response)
            return TicketDetails(
                name=parsed_data.get("name", ""),
                phone=parsed_data.get("phone", ""),
                from_=parsed_data.get("from", ""),
                to=parsed_data.get("to", ""),
                date=parsed_data.get("date", "")
            )
        except json.JSONDecodeError:
            print("LLM response is not valid JSON. Retrying...")
            return TicketDetails()

    def call_agent(self, user_input):
        extracted_data: TicketDetails = {}

        while True:
            self.chat_history.append(f"User: {user_input}")
            chat_history_str = "\n".join(self.chat_history)

            response = self.llm_chain.invoke({"chat_history": chat_history_str, "user_input": user_input})
            self.chat_history.append(f"AI: {json.dumps(response)}")
            parsed_data = self.parse_ticket_details(response)

            
            extracted_data.update(parsed_data)

            # Check for missing fields
            missing_fields = [key for key in ["name", "phone", "from_", "to", "date"] if not extracted_data.get(key)]

            if missing_fields:
                print("\nUpdated Booking Details:", extracted_data)
                print(f"Provide me the following information {', '.join(missing_fields)}")
                # for field in missing_fields:
                #     extracted_data[field] = input(f"Please provide {field}: ").strip()
                user_input=input(f"Please provide: ").strip()
                # print("\nUpdated Booking Details:", extracted_data)
            else:
                print("\nLet me book a ticket for you...")
                self.buy_ticket(extracted_data, show_table=True)
                break  
             

    def buy_ticket(self, details: TicketDetails, show_table=False):
        """Books the ticket once details are extracted."""
        travel_agent = MyTravels()
        result = travel_agent.book_ticket(
            name=details["name"],
            phone=details["phone"],
            source=details["from_"],  # Using "from_" since "from" is a keyword
            destination=details["to"],
            date=details["date"]
        )
        if show_table:
            print_table()
        return result


if __name__ == "__main__":
    agent = TicketAI()
    user_input = input("How can I help you today? ")
    agent.call_agent(user_input)
