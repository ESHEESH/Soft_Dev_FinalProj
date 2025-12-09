import tkinter as tk
from tkinter import ttk, messagebox

class HomePage(tk.Frame):
    def __init__(self, parent, controller, username):
        super().__init__(parent)
        self.controller = controller
        self.username = username
        
        # Title
        title = tk.Label(self, text="🏠 Home", font=("Arial", 24, "bold"), fg="#2c3e50")
        title.pack(pady=30)
        
        # Welcome message
        welcome = tk.Label(self, text=f"Welcome back, {username}!", 
                          font=("Arial", 16), fg="#34495e")
        welcome.pack(pady=10)
        
        # User stats frame
        stats_frame = tk.Frame(self, bg="#ecf0f1", relief="ridge", bd=2)
        stats_frame.pack(pady=20, padx=50, fill="both", expand=True)
        
        user_data = controller.get_user_data(username)
        
        # Time remaining
        time_label = tk.Label(stats_frame, text=f"⏱️ Time Remaining", 
                             font=("Arial", 14, "bold"), bg="#ecf0f1")
        time_label.pack(pady=15)
        
        time_value = tk.Label(stats_frame, text=f"{user_data['time']} minutes", 
                             font=("Arial", 28, "bold"), fg="#27ae60", bg="#ecf0f1")
        time_value.pack()
        
        # Points
        points_label = tk.Label(stats_frame, text=f"⭐ Loyalty Points", 
                               font=("Arial", 14, "bold"), bg="#ecf0f1")
        points_label.pack(pady=(30, 5))
        
        points_value = tk.Label(stats_frame, text=f"{user_data['points']} pts", 
                               font=("Arial", 28, "bold"), fg="#3498db", bg="#ecf0f1")
        points_value.pack()
        
        # Streak
        streak_label = tk.Label(stats_frame, text=f"🔥 Login Streak", 
                               font=("Arial", 14, "bold"), bg="#ecf0f1")
        streak_label.pack(pady=(30, 5))
        
        streak_value = tk.Label(stats_frame, text=f"{user_data['streak']} days", 
                               font=("Arial", 28, "bold"), fg="#e74c3c", bg="#ecf0f1")
        streak_value.pack(pady=(0, 20))
        
        # PC Status
        if user_data['slot']:
            pc_label = tk.Label(stats_frame, text=f"💻 Currently using PC {user_data['slot']}", 
                               font=("Arial", 12), fg="#16a085", bg="#ecf0f1")
            pc_label.pack(pady=10)