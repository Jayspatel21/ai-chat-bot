import tkinter as tk
from tkinter import ttk, scrolledtext
import os
from dotenv import load_dotenv
from travel_planner_bot import TravelPlannerBot

class TravelPlannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Travel Planner")
        self.root.geometry("800x600")
        
        # Load API key and initialize bot
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")
        self.bot = TravelPlannerBot(api_key)
        
        # Create GUI elements
        self.create_widgets()
        
        # Start conversation
        self.display_bot_message(self.bot.get_next_question())

    def create_widgets(self):
        # Chat display area
        self.chat_display = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=20)
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Input frame
        input_frame = ttk.Frame(self.root)
        input_frame.pack(padx=10, pady=5, fill=tk.X)
        
        # User input field
        self.user_input = ttk.Entry(input_frame)
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Send button
        send_button = ttk.Button(input_frame, text="Send", command=self.process_input)
        send_button.pack(side=tk.RIGHT, padx=5)
        
        # Bind Enter key to send message
        self.user_input.bind("<Return>", lambda e: self.process_input())

    def display_bot_message(self, message):
        self.chat_display.insert(tk.END, "Bot: " + message + "\n\n")
        self.chat_display.see(tk.END)

    def display_user_message(self, message):
        self.chat_display.insert(tk.END, "You: " + message + "\n")
        self.chat_display.see(tk.END)

    def process_input(self):
        user_message = self.user_input.get().strip()
        if user_message:
            self.display_user_message(user_message)
            self.user_input.delete(0, tk.END)
            
            # Get bot response
            response = self.bot.process_input(user_message)
            self.display_bot_message(response)

def main():
    root = tk.Tk()
    app = TravelPlannerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()