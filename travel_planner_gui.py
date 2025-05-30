import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import os
import re
from datetime import datetime
from dotenv import load_dotenv
from travel_planner_bot import TravelPlannerBot

class TravelPlannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🌍 TravelGenie - AI Travel Planner")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f8ff')
        
        # Configure style
        self.setup_styles()
        
        # Load API key and initialize bot
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key:
            messagebox.showerror("API Key Error", 
                               "GROQ_API_KEY not found in environment variables.\n"
                               "Please add your API key to a .env file.")
            return
            
        self.bot = TravelPlannerBot(api_key)
        
        # Enhanced travel-related keywords for better filtering
        self.travel_keywords = [
            'travel', 'trip', 'vacation', 'holiday', 'flight', 'hotel', 'destination',
            'booking', 'stay', 'tour', 'visit', 'journey', 'itinerary', 'budget',
            'accommodation', 'restaurant', 'attractions', 'activities', 'sightseeing',
            'tourism', 'explore', 'adventure', 'backpack', 'cruise', 'resort',
            'airport', 'visa', 'passport', 'currency', 'weather', 'climate',
            'culture', 'museum', 'beach', 'mountain', 'city', 'country'
        ]

        # Track conversation progress
        self.progress_steps = ['name', 'email', 'destination', 'source', 'days', 'budget', 'dates']
        self.current_step = 0

        # Create GUI elements
        self.create_widgets()
        
        # Start conversation
        self.display_bot_message(self.bot.get_next_question())

    def setup_styles(self):
        """Configure custom styles for the application"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure custom styles
        style.configure('Header.TLabel', 
                       background='#4a90e2', 
                       foreground='white', 
                       font=('Arial', 14, 'bold'),
                       padding=10)
        
        style.configure('Progress.TLabel',
                       font=('Arial', 10),
                       background='#f0f8ff')
        
        style.configure('Send.TButton',
                       font=('Arial', 10, 'bold'),
                       padding=5)

    def create_widgets(self):
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header section
        self.create_header(main_container)
        
        # Progress section
        self.create_progress_section(main_container)
        
        # Chat section
        self.create_chat_section(main_container)
        
        # Input section
        self.create_input_section(main_container)
        
        # Action buttons section
        self.create_action_buttons(main_container)

    def create_header(self, parent):
        """Create the header section with title and description"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = ttk.Label(
            header_frame,
            text="🌍 TravelGenie - Your AI Travel Assistant",
            style='Header.TLabel'
        )
        title_label.pack(fill=tk.X)
        
        # Description
        desc_text = """Plan your perfect trip with AI assistance! I'll help you create personalized itineraries, 
find the best flights and accommodations, and provide local insights - all within your budget."""
        
        desc_label = ttk.Label(
            header_frame,
            text=desc_text,
            wraplength=980,
            justify="center",
            font=('Arial', 10),
            background='#f0f8ff'
        )
        desc_label.pack(pady=5)

    def create_progress_section(self, parent):
        """Create progress tracking section"""
        progress_frame = ttk.LabelFrame(parent, text="Planning Progress", padding=10)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=len(self.progress_steps),
            length=400
        )
        self.progress_bar.pack(side=tk.LEFT, padx=(0, 10))
        
        # Progress label
        self.progress_label = ttk.Label(
            progress_frame,
            text="Step 1/7: Getting your name",
            style='Progress.TLabel'
        )
        self.progress_label.pack(side=tk.LEFT)
        
        # User info display
        self.info_display = ttk.Label(
            progress_frame,
            text="",
            style='Progress.TLabel',
            wraplength=300
        )
        self.info_display.pack(side=tk.RIGHT)

    def create_chat_section(self, parent):
        """Create the chat display section"""
        chat_frame = ttk.LabelFrame(parent, text="Conversation", padding=5)
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Chat display with custom formatting
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            height=15,
            font=('Arial', 10),
            bg='white',
            fg='black'
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for different message types
        self.chat_display.tag_configure("bot", foreground="#2c3e50", font=('Arial', 10))
        self.chat_display.tag_configure("user", foreground="#27ae60", font=('Arial', 10))
        self.chat_display.tag_configure("system", foreground="#8e44ad", font=('Arial', 10, 'italic'))

    def create_input_section(self, parent):
        """Create the user input section"""
        input_frame = ttk.LabelFrame(parent, text="Your Message", padding=5)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Input field with placeholder
        input_container = ttk.Frame(input_frame)
        input_container.pack(fill=tk.X)
        
        self.user_input = ttk.Entry(
            input_container,
            font=('Arial', 11),
            width=70
        )
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Send button
        self.send_button = ttk.Button(
            input_container,
            text="Send ✈️",
            command=self.process_input,
            style='Send.TButton'
        )
        self.send_button.pack(side=tk.RIGHT)
        
        # Bind Enter key
        self.user_input.bind("<Return>", lambda e: self.process_input())
        
        # Add input hints
        self.hint_label = ttk.Label(
            input_frame,
            text="💡 Tip: Be specific about your preferences for better recommendations!",
            font=('Arial', 9, 'italic'),
            foreground='#7f8c8d',
            background='#f0f8ff'
        )
        self.hint_label.pack(pady=2)

    def create_action_buttons(self, parent):
        """Create action buttons section"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X)
        
        # Clear chat button
        clear_button = ttk.Button(
            button_frame,
            text="🗑️ Clear Chat",
            command=self.clear_chat
        )
        clear_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Save conversation button
        save_button = ttk.Button(
            button_frame,
            text="💾 Save Conversation",
            command=self.save_conversation
        )
        save_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Restart planning button
        restart_button = ttk.Button(
            button_frame,
            text="🔄 Start New Trip",
            command=self.restart_planning
        )
        restart_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Help button
        help_button = ttk.Button(
            button_frame,
            text="❓ Help",
            command=self.show_help
        )
        help_button.pack(side=tk.RIGHT)

    def update_progress(self):
        """Update the progress bar and labels"""
        if self.bot.conversation_state in self.progress_steps:
            self.current_step = self.progress_steps.index(self.bot.conversation_state) + 1
        elif self.bot.conversation_state == 'init':
            self.current_step = 0
        else:
            self.current_step = len(self.progress_steps)
        
        self.progress_var.set(self.current_step)
        
        if self.current_step < len(self.progress_steps):
            step_name = self.progress_steps[self.current_step].replace('_', ' ').title()
            self.progress_label.config(text=f"Step {self.current_step + 1}/{len(self.progress_steps)}: {step_name}")
        else:
            self.progress_label.config(text="✅ Information Complete - Generating Itinerary!")
        
        # Update user info display
        self.update_info_display()

    def update_info_display(self):
        """Update the user information display"""
        info_parts = []
        for key, value in self.bot.user_info.items():
            if value:
                display_key = key.replace('_', ' ').title()
                if key == 'budget':
                    info_parts.append(f"{display_key}: ${value}")
                else:
                    info_parts.append(f"{display_key}: {value}")
        
        info_text = " | ".join(info_parts)
        if len(info_text) > 60:
            info_text = info_text[:57] + "..."
        
        self.info_display.config(text=info_text)

    def is_travel_related(self, message):
        """Enhanced travel-related message detection"""
        message = message.lower()
        
        # Always allow during info gathering phase
        if self.bot.conversation_state in ['name', 'email', 'destination', 'source', 'days', 'budget', 'dates']:
            return True
        
        # Check for travel keywords
        return any(keyword in message for keyword in self.travel_keywords)

    def display_bot_message(self, message):
        """Display bot message with enhanced formatting"""
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_display.insert(tk.END, f"🤖 TravelGenie [{timestamp}]:\n", "system")
        self.chat_display.insert(tk.END, f"{message}\n\n", "bot")
        self.chat_display.see(tk.END)
        self.update_progress()

    def display_user_message(self, message):
        """Display user message with enhanced formatting"""
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_display.insert(tk.END, f"👤 You [{timestamp}]:\n", "system")
        self.chat_display.insert(tk.END, f"{message}\n\n", "user")
        self.chat_display.see(tk.END)

    def process_input(self):
        """Process user input with enhanced validation"""
        user_message = self.user_input.get().strip()
        
        if not user_message:
            messagebox.showwarning("Empty Message", "Please enter a message before sending.")
            return
        
        # Check if message is travel-related or in info gathering phase
        if not self.is_travel_related(user_message):
            messagebox.showinfo(
                "Travel Assistant Only", 
                "I specialize in travel planning! Please ask me about:\n"
                "• Trip destinations and itineraries\n"
                "• Flight and hotel recommendations\n"
                "• Budget planning and tips\n"
                "• Local attractions and activities\n"
                "• Travel advice and logistics"
            )
            self.user_input.delete(0, tk.END)
            return
        
        # Display user message
        self.display_user_message(user_message)
        self.user_input.delete(0, tk.END)
        
        # Disable input while processing
        self.send_button.config(state='disabled', text='Processing...')
        self.user_input.config(state='disabled')
        
        # Process in a separate thread to avoid GUI freezing
        self.root.after(100, lambda: self.get_bot_response(user_message))

    def get_bot_response(self, user_message):
        """Get bot response and update GUI"""
        try:
            response = self.bot.process_input(user_message)
            self.display_bot_message(response)
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}\nPlease try again."
            self.display_bot_message(error_msg)
        finally:
            # Re-enable input
            self.send_button.config(state='normal', text='Send ✈️')
            self.user_input.config(state='normal')
            self.user_input.focus()

    def clear_chat(self):
        """Clear the chat display"""
        if messagebox.askyesno("Clear Chat", "Are you sure you want to clear the conversation?"):
            self.chat_display.delete(1.0, tk.END)

    def save_conversation(self):
        """Save the conversation to a file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Save Conversation"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("=== TravelGenie Conversation Log ===\n")
                    f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(self.chat_display.get(1.0, tk.END))
                
                messagebox.showinfo("Saved", f"Conversation saved to {filename}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save file: {str(e)}")

    def restart_planning(self):
        """Restart the planning process"""
        if messagebox.askyesno("New Trip", "Start planning a new trip? This will clear current progress."):
            # Reset bot state
            load_dotenv()
            api_key = os.getenv("GROQ_API_KEY")
            self.bot = TravelPlannerBot(api_key)
            
            # Reset progress
            self.current_step = 0
            self.progress_var.set(0)
            
            # Clear and restart
            self.chat_display.delete(1.0, tk.END)
            self.display_bot_message(self.bot.get_next_question())

    def show_help(self):
        """Show help dialog"""
        help_text = """🌍 TravelGenie Help

HOW TO USE:
1. Answer the questions step by step
2. Be specific about your preferences
3. Ask follow-up questions anytime

WHAT I CAN HELP WITH:
• Create detailed travel itineraries
• Find flights and accommodations
• Suggest attractions and activities
• Plan within your budget
• Provide local tips and insights

TIPS FOR BEST RESULTS:
• Mention your interests (culture, adventure, relaxation)
• Be specific about budget constraints
• Ask about local customs and food
• Request alternatives if needed

EXAMPLES:
• "I love museums and historic sites"
• "I prefer budget-friendly options"
• "What's the best local food to try?"
• "Are there any free activities?"

Need more help? Just ask me during our conversation!"""
        
        messagebox.showinfo("Help - TravelGenie", help_text)


def main():
    root = tk.Tk()
    
    # Set window icon (if available)
    try:
        root.iconbitmap('travel_icon.ico')  # Optional: add an icon file
    except:
        pass
    
    app = TravelPlannerGUI(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_reqwidth() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_reqheight() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()


if __name__ == "__main__":
    main()
