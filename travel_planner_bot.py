import re
from datetime import datetime
from typing import Dict, Optional
from groq import Groq

class TravelPlannerBot:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.user_info = {
            'name': None,
            'email': None,
            'destination': None,
            'source': None,
            'days': None,
            'budget': None,
            'dates': None
        }
        self.conversation_state = 'init'
        self.conversation_history = []

    def validate_email(self, email: str) -> bool:
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return bool(re.match(pattern, email))

    def get_model_response(self, prompt: str) -> str:
        try:
            system_prompt = """You are TravelGenie, an expert travel planning assistant with extensive knowledge of global destinations, travel logistics, and budget optimization. Your role is to create personalized, practical, and memorable travel experiences.

CORE RESPONSIBILITIES:
- Provide comprehensive travel planning assistance
- Create detailed, day-by-day itineraries 
- Offer budget-conscious recommendations
- Share insider tips and local insights
- Ensure all suggestions are practical and actionable

PERSONALITY & TONE:
- Enthusiastic and knowledgeable about travel
- Professional yet friendly and approachable
- Patient when gathering user information
- Encouraging and inspiring about travel experiences
- Clear and organized in communication

EXPERTISE AREAS:
- Flight booking strategies and timing
- Accommodation recommendations (hotels, hostels, Airbnb, boutique stays)
- Local transportation options and costs
- Must-see attractions and hidden gems
- Cultural experiences and local customs
- Food recommendations and dining budgets
- Safety tips and travel advisories
- Visa requirements and travel documentation
- Weather considerations and packing suggestions
- Budget optimization and money-saving tips

RESPONSE GUIDELINES:
1. Always stay focused on travel-related topics
2. If asked about non-travel topics, politely redirect: "I specialize in travel planning! Let's get back to creating your amazing trip. What would you like to know about your travel plans?"
3. Provide specific, actionable recommendations with estimated costs when possible
4. Include both popular attractions and off-the-beaten-path experiences
5. Consider different travel styles (luxury, mid-range, budget, backpacking)
6. Mention seasonal considerations and best times to visit
7. Include practical logistics like transportation between locations
8. Suggest realistic daily schedules that aren't overpacked

ITINERARY STRUCTURE:
When creating full itineraries, include:
- Executive summary of the trip
- Pre-trip checklist (documents, vaccinations, etc.)
- Day-by-day detailed schedule with timings
- Transportation details and costs
- Accommodation recommendations with price ranges
- Restaurant and food recommendations
- Cultural etiquette and local customs
- Emergency contacts and important phrases
- Budget breakdown by category
- Packing suggestions based on weather/activities

BUDGET CONSIDERATIONS:
- Always work within the specified budget
- Provide options at different price points when possible
- Include hidden costs (tips, taxes, entrance fees)
- Suggest money-saving strategies
- Recommend budget tracking methods

Remember: You are creating experiences, not just trips. Focus on what makes each destination special and how the traveler can best experience the local culture and attractions within their constraints."""
            
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="llama-3.1-8b-instant",
                temperature=0.7,
                max_tokens=2048
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def get_next_question(self) -> str:
        if self.conversation_state == 'init':
            self.conversation_state = 'name'
            return "Hello! I'm TravelGenie, your personal travel planning assistant! 🌍✈️ I'm here to help you create an amazing, personalized travel experience. To get started, what's your name?"
        
        questions = {
            'email': "Perfect! To send you your complete travel itinerary and any updates, I'll need your email address. What's your email?",
            'destination': "Exciting! Where would you like to go? You can tell me a specific city, country, or even describe the type of experience you're looking for (like 'tropical beach destination' or 'European cultural cities').",
            'source': "Great choice! From which city or airport will you be departing for this adventure?",
            'days': "How many days do you have for this trip? Please enter a number between 1-30 days. (This helps me pace your itinerary perfectly!)",
            'budget': "What's your total budget for this trip in USD? Include everything - flights, accommodation, food, activities, and shopping. Don't worry, I'll help you make every dollar count!",
            'dates': "When are you planning to travel? Please let me know the month and year (like 'March 2024' or 'Summer 2024'). This helps me suggest the best activities and prepare you for the weather!"
        }
        
        for field, value in self.user_info.items():
            if value is None:
                self.conversation_state = field
                return questions.get(field, self.get_model_response(f"Ask for {field} in a friendly, travel-focused way"))
        
        return self.generate_itinerary()

    def process_input(self, user_input: str) -> str:
        self.conversation_history.append({"role": "user", "content": user_input})

        # Process user input based on current state
        if self.conversation_state == 'name' and self.user_info['name'] is None:
            self.user_info['name'] = user_input.strip()
        elif self.conversation_state == 'email':
            if self.validate_email(user_input.strip()):
                self.user_info['email'] = user_input.strip()
            else:
                return "I need a valid email address to send your itinerary. Please provide an email in the format: example@email.com"
        elif self.conversation_state == 'days':
            try:
                days = int(user_input.strip())
                if 1 <= days <= 30:
                    self.user_info['days'] = days
                else:
                    return "Please enter a number of days between 1 and 30. This helps me create the perfect itinerary length for you!"
            except ValueError:
                return "Please enter a valid number (like 5 or 10) for the number of days you'd like to travel."
        else:
            self.user_info[self.conversation_state] = user_input.strip()

        return self.get_next_question()

    def generate_itinerary(self) -> str:
        if None in self.user_info.values():
            return self.get_next_question()

        prompt = f"""
Create a comprehensive, personalized travel itinerary for:

TRAVELER PROFILE:
- Name: {self.user_info['name']}
- Departing from: {self.user_info['source']}
- Destination: {self.user_info['destination']}
- Trip duration: {self.user_info['days']} days
- Total budget: ${self.user_info['budget']} USD
- Travel dates: {self.user_info['dates']}

REQUIREMENTS:
Please create a detailed itinerary that includes:

1. TRIP OVERVIEW & HIGHLIGHTS
   - Brief destination overview and what makes it special
   - Top 3-5 must-do experiences for this trip
   - Best aspects of traveling during {self.user_info['dates']}

2. FLIGHT RECOMMENDATIONS
   - Suggested flight routes and airlines
   - Estimated flight costs
   - Best booking timing and tips

3. ACCOMMODATION STRATEGY
   - 2-3 accommodation options within budget
   - Recommended neighborhoods/areas to stay
   - Estimated nightly rates

4. DETAILED DAY-BY-DAY ITINERARY
   - Specific activities with timing (morning, afternoon, evening)
   - Transportation between locations
   - Estimated costs for each activity
   - Restaurant recommendations for each day
   - Cultural tips and local etiquette

5. COMPREHENSIVE BUDGET BREAKDOWN
   - Flights: $X
   - Accommodation: $X (per night × {self.user_info['days']} nights)
   - Food: $X (breakdown by meal type)
   - Activities/Attractions: $X
   - Local transportation: $X
   - Shopping/Miscellaneous: $X
   - TOTAL: Should not exceed ${self.user_info['budget']}

6. PRACTICAL TRAVEL TIPS
   - Weather expectations and packing suggestions
   - Currency and payment methods
   - Important local customs
   - Safety considerations
   - Essential phrases in local language
   - Emergency contacts and embassy information

7. MONEY-SAVING TIPS
   - How to stretch the budget further
   - Free activities and experiences
   - Local alternatives to tourist traps

Make this itinerary exciting, practical, and perfectly tailored to {self.user_info['name']}'s {self.user_info['days']}-day adventure in {self.user_info['destination']}!
"""
        return self.get_model_response(prompt)
