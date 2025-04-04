
from typing import Optional
import os
import sys
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableBranch
from pydantic import BaseModel, Field
import re
import io

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from web.api import MyTravels
from tests import print_table

class Intent(BaseModel):
    book_ticket: bool = Field(False, description="User wants to book a ticket")
    check_price: bool = Field(False, description="User wants to check ticket prices")
    check_availability: bool = Field(False, description="User wants to check seat availability")

class TicketDetails(BaseModel):
    name: Optional[str] = Field(None, description="Name of the person")
    phone: Optional[str] = Field(None, description="Mobile number of the person")
    from_: Optional[str] = Field(None, description="Name of a city")
    to: Optional[str] = Field(None, description="Name of a city")
    date: Optional[str] = Field(None, description="A date on the calendar")
    reply: Optional[str] = Field(None, description="If any of the details are missing, return a message asking for them else say thank you.")