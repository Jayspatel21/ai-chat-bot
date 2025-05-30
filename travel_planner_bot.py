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
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful travel planning assistant. Generate specific and detailed responses."
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
            return "Hello! I'm here to help you plan your trip. What's your name?"
        
        for field, value in self.user_info.items():
            if value is None:
                self.conversation_state = field
                prompt = f"Generate a friendly question asking for the user's {field} for travel planning."
                return self.get_model_response(prompt)
        
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
                return "Please provide a valid email address."
        elif self.conversation_state == 'days':
            try:
                days = int(user_input.strip())
                if 1 <= days <= 30:
                    self.user_info['days'] = days
                else:
                    return "Please enter a number of days between 1 and 30."
            except ValueError:
                return "Please enter a valid number of days."
        else:
            self.user_info[self.conversation_state] = user_input.strip()

        return self.get_next_question()

    def generate_itinerary(self) -> str:
        if None in self.user_info.values():
            return self.get_next_question()

        prompt = f"""
Generate a detailed travel itinerary with the following information:
- Traveler: {self.user_info['name']}
- From: {self.user_info['source']}
- To: {self.user_info['destination']}
- Duration: {self.user_info['days']} days
- Budget: {self.user_info['budget']} USD
- Dates: {self.user_info['dates']}

Include:
1. Suggested flight options
2. Recommended accommodations within budget
3. Day-by-day itinerary with specific attractions and activities
4. Budget breakdown
5. Local travel tips
6. Must-try local cuisine
"""
        return self.get_model_response(prompt)