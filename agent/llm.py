from typing import Optional
import os
import sys
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableBranch
from pydantic import BaseModel, Field
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from web.api import MyTravels
from tests import print_table
from  agent.output_formats import TicketDetails, Intent
from agent.prompts import (
    intent_prompt,details_prompt,fallback_prompt
)
# Load environment variables
load_dotenv()


class TicketAI:
    def __init__(self):
        
        self.hf_api_key = os.getenv("HUGGINGFACEHUB_API_TOKEN")
        self.client = InferenceClient(token=self.hf_api_key)
        self.user_input = None
        self.intent_parser = PydanticOutputParser(pydantic_object=Intent)
        self.details_parser = PydanticOutputParser(pydantic_object=TicketDetails)

       
        self.intent_prompt= intent_prompt
        self.details_prompt= details_prompt
        self.fallback_prompt= fallback_prompt
        
        
        self.ticket_data = { "name": None, "phone": None, "from": None, "to": None, "date": None }

    def update_ticket(self, name, phone, from_, to, date):
        if name: self.ticket_data["name"] = name
        if phone: self.ticket_data["phone"] = phone
        if from_: self.ticket_data["from"] = from_
        if to: self.ticket_data["to"] = to
        if date: self.ticket_data["date"] = date
        return all(self.ticket_data.values())

    def detect_intent(self, user_input):
        formatted_prompt = self.intent_prompt.format(
            user_input=user_input, format_instruction=self.intent_parser.get_format_instructions()
        )
        response = self.client.chat_completion(
            model="mistralai/Mistral-7B-Instruct-v0.1", messages=[{"role": "user", "content": formatted_prompt}]
        )
        
        raw_text = response.choices[0]["message"]["content"]
        cleaned_text = raw_text.replace("\\_", "_").strip()

        return self.intent_parser.parse(cleaned_text)
        # return self.intent_parser.parse(response.choices[0]["message"]["content"])

    def handle_booking(self, *_):
        print("Booking ticket...")
        formatted_prompt = self.details_prompt.format(
            user_input=self.user_input, format_instruction=self.details_parser.get_format_instructions()
        )
        response = self.client.chat_completion(
            model="mistralai/Mistral-7B-Instruct-v0.1", messages=[{"role": "user", "content": formatted_prompt}]
        )
        try:
            details = self.details_parser.parse(response.choices[0]["message"]["content"])
            complete = self.update_ticket(details.name, details.phone, details.from_, details.to, details.date)

            print("Extracted Ticket Details:", self.ticket_data)
            if complete:
                a=self.book_ticket()
                return f"{a['message']} Ticket ID: {a['ticket_id']}"
            elif details.reply:
                print(f"Missing Details: {details.reply}")
                self.call_agent(input("Please provide the missing details: "))
            else:
                print("Incomplete details. Please provide all required information.")
                self.call_agent(input("Please provide the missing details: "))
                
                
        except Exception as e:
            print(f"Error processing booking: {e}")


    def book_ticket(self):
        travel_agent = MyTravels()
        a=travel_agent.book_ticket(
            name=self.ticket_data["name"], phone=self.ticket_data["phone"],
            source=self.ticket_data["from"], destination=self.ticket_data["to"], date=self.ticket_data["date"]
        )
        # print_table()
        print("Booking confirmed! Ticket details saved.")
        return a

    def check_price(self, *_):
        print("Checking ticket prices... (Functionality not yet implemented)")
        return "Checking ticket prices... (Functionality not yet implemented)"

    def check_availability(self, *_):
        print("Checking ticket availability... (Functionality not yet implemented)")
        return "Checking ticket availability... (Functionality not yet implemented)"

    def fallback(self, *_):
        print("Fallback to general conversation...")
        formatted_prompt = self.fallback_prompt.format(user_input=self.user_input)
        response = self.client.chat_completion(
            model="mistralai/Mistral-7B-Instruct-v0.1", messages=[{"role": "user", "content": formatted_prompt}]
        )
        try:
            print(response.choices[0]["message"]["content"])
            return response.choices[0]["message"]["content"]
        except Exception as e:
            print(f"Error parsing fallback response: {e}")
            
        return "How else can I assist you with your train travel?"


    def call_agent(self, user_input):
        self.user_input = user_input
        intent = self.detect_intent(user_input)
        print(f"Detected intent: {intent}")

        # Branch execution based on boolean flags
        branch = RunnableBranch(
            (lambda _: intent.book_ticket, self.handle_booking),
            (lambda _: intent.check_price, self.check_price),
            (lambda _: intent.check_availability, self.check_availability),
            self.fallback,
        )
        output= branch.invoke(None)
        return output

if __name__ == "__main__":
    agent = TicketAI()
    user_input = input("How can I help you today? ")
    agent.call_agent(user_input)


