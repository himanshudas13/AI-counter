
import sys
import os
# Add the parent directory to sys.path so Python can find "web"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Now you can import MyTravels
from web.api import MyTravels
from dotenv import load_dotenv
from tests import print_table
import os



travel_agent = MyTravels()
    
result = travel_agent.book_ticket(
        name="Doe",
        phone="1234567890",
        source="Bangalore",
        destination="Chennai",
        date="2025-03-18"
    )

print(result)
print_table()