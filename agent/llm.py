from typing import Optional
import os
import sys
import re
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableBranch
from pydantic import BaseModel, Field
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from web.api import MyTravels
from tests import print_table

# Load environment variables
load_dotenv()

class UserIntent(BaseModel):
    task: str = Field(..., description="User intent (bookticket, checkprice, checkavailability, other)")

class TicketDetails(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    from_: Optional[str] = None
    to: Optional[str] = None
    date: Optional[str] = None
    reply: Optional[str] = None

class TicketAI:
    def __init__(self):
        self.client = InferenceClient(token=os.getenv("HUGGINGFACEHUB_API_TOKEN"))
        self.model = "google/gemma-7b-it"
        self.intent_parser = PydanticOutputParser(pydantic_object=UserIntent)
        self.details_parser = PydanticOutputParser(pydantic_object=TicketDetails)
        self.ticket_data = {key: None for key in ["name", "phone", "from", "to", "date"]}
        
        # Define prompts
        self.intent_prompt = """
        Determine the user's intent. Choose one of the following tasks:
        - book_ticket
        - check_price
        - check_availability
        - other

        User Input: {user_input}
        {format_instruction}
        """
        
        self.details_prompt = """
        Extract ticket details: name, phone, from, to, and date.
        If any details are missing, return a 'reply' field asking for them.
        
        User Input: {user_input}
        {format_instruction}
        """
        
        self.fallback_prompt = """
        {user_input}
        Best train routes, travel tips, station amenities—discuss anything train-related!
        Be creative and funny in 2 lines.
        """
        
        self.price_prompt = """
        Retrieve ticket price information for the given journey.
        
        User Input: {user_input}
        """
        
        self.availability_prompt = """
        Check ticket availability for the given journey.
        
        User Input: {user_input}
        """

    def query_model(self, prompt):
        response = self.client.chat_completion(model=self.model, messages=[{"role": "user", "content": prompt}])
        return response.choices[0]["message"]["content"]

    def detect_intent(self, user_input):
        prompt = self.intent_prompt.format(user_input=user_input, format_instruction=self.intent_parser.get_format_instructions())
        try:
            return re.sub(r'[^a-z]', '', self.intent_parser.parse(self.query_model(prompt)).task.lower())
        except:
            return "other"

    def handle_booking(self,task):
        prompt = self.details_prompt.format(user_input=self.user_input, format_instruction=self.details_parser.get_format_instructions())
        try:
            details = self.details_parser.parse(self.query_model(prompt))
            self.ticket_data.update({k: v for k, v in details.dict().items() if v})
            if all(self.ticket_data.values()):
                self.book_ticket()
            else:
                print(f"Missing details: {details.reply}")
                self.call_agent(input("Provide missing details: "))
        except:
            self.call_agent(input("How can I help you further? "))

    def book_ticket(self):
        MyTravels().book_ticket(**self.ticket_data)
        print_table()
        print("Booking confirmed! Ticket details saved.")

    def check_price(self,task):
        prompt = self.price_prompt.format(user_input=self.user_input)
        print("Ticket price info:", self.query_model(prompt))

    def check_availability(self,task):
        prompt = self.availability_prompt.format(user_input=self.user_input)
        print("Ticket availability info:", self.query_model(prompt))

    def fallback(self,task):
        prompt = self.fallback_prompt.format(user_input=self.user_input)
        print(self.query_model(prompt))
        self.call_agent(input("How else can I assist? "))

    def call_agent(self, user_input):
        self.user_input = user_input
        task = self.detect_intent(user_input)
        print(task)
        RunnableBranch(
            (lambda x: x == "bookticket", self.handle_booking),
            (lambda x: x == "checkprice", self.check_price),
            (lambda x: x == "checkavailability", self.check_availability),
            self.fallback,
        ).invoke(task)

if __name__ == "__main__":
    TicketAI().call_agent(input("How can I help you today? "))
