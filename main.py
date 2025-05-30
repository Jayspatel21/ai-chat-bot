import os
from dotenv import load_dotenv
from travel_planner_bot import TravelPlannerBot

def main():
    # Load environment variables
    load_dotenv()
    
    # Get API key from environment variable
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("Error: GROQ_API_KEY not found in environment variables")
        return

    bot = TravelPlannerBot(api_key)
    print(bot.get_next_question())

    while True:
        user_input = input("> ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Thank you for using the Travel Planner Bot. Goodbye!")
            break

        response = bot.process_input(user_input)
        print(response)

if __name__ == "__main__":
    main()