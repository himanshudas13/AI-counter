from typing import Optional
import os
import sys
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from web.api import MyTravels
from tests import print_table

# Load environment variables
load_dotenv()

# Define a structured dictionary type for ticket details
class TicketDetails(BaseModel):
    name: Optional[str] = Field(None, description="Name of the person")
    phone: Optional[str] = Field(None, description="Mobile number of the person")
    from_: Optional[str] = Field(None, description="Name of a city")  # "from" is a keyword in Python, so use "from_" instead
    to: Optional[str] = Field(None, description="Name of a city")
    date: Optional[str] = Field(None, description="A date on the calendar")
    reply: Optional[str] = Field(None, description="If any details are missing, return a message asking for the missing fields.")

class TicketAI:
    def __init__(self):
        self.hf_api_key = os.getenv("HUGGINGFACEHUB_API_TOKEN")
        self.client = InferenceClient(token=self.hf_api_key)
        self.chat_history = []  # Store chat history
        self.parser = PydanticOutputParser(pydantic_object=TicketDetails)

        # Adjusted prompt for structured output
        # self.prompt_template = (
        #     "Extract the following details from the input and return a strictly valid JSON object:\n"
        #     "name, phone, from (source), to (destination), and date.\n\n"
        #     "If any details are missing, return a field called 'reply' with a message listing the missing details.\n"
        #     "Use the exact format as defined:\n"
        #     "{format_instruction}\n\n"
        #     "Chat History:\n{chat_history}\n\n"
        #     "Latest Input:\n{user_input}\n\n"
        # ) 
        
        self.prompt_template = (
            "Extract the following details from the input and return \n"
            "name, phone, from (source), to (destination), and date.\n\n"
            "If any details are missing, return a field called 'reply' with a message listing the missing details.\n"
            "Use the exact format as defined:\n"
            "{format_instruction}\n\n"
            "Chat History:\n{chat_history}\n\n"
            "Latest Input:\n{user_input}\n\n"
        ) 

    def call_agent(self, user_input):
        extracted_data = {}

        while True:
            self.chat_history.append(f"User: {user_input}")
            chat_history_str = "\n".join(self.chat_history)

            formatted_prompt = self.prompt_template.format(
                format_instruction=self.parser.get_format_instructions(),
                chat_history=chat_history_str,
                user_input=user_input
            )

            response = self.client.chat_completion(
                model="mistralai/Mistral-7B-Instruct-v0.1",
                messages=[{"role": "user", "content": formatted_prompt}]
            )

            # Extract and parse response using LangChain's Pydantic parser
            try:
                ai_response = response.choices[0]["message"]["content"]
                parsed_data = self.parser.parse(ai_response)  # **Correct way to parse output**
            except Exception as e:
                print(f"Invalid output: {response}\nError: {e}")
                continue

            
            self.chat_history.append(f"AI: {parsed_data.model_dump_json()}")
            extracted_data.update(parsed_data.model_dump())

           
            # Ensure all required fields are present before proceeding
            missing_fields = [key for key in ["name", "phone", "from_", "to", "date"] if not extracted_data.get(key)]

            if missing_fields:
                extracted_data["reply"] = f"Provide the following missing details: {', '.join(missing_fields)}"
                print("AI:")
                print(extracted_data["reply"])
                user_input = input("Enter missing details: ").strip()
                continue


            # Ensure all required fields are present before booking
            if all(extracted_data.get(key) for key in ["name", "phone", "from_", "to", "date"]):
                print("\nLet me book a ticket for you...")
                self.buy_ticket(extracted_data, show_table=True)
                break  

    def buy_ticket(self, details, show_table=False):
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
