import tkinter as tk
from tkinter import ttk, messagebox

class AccountPage(tk.Frame):
    def __init__(self, parent, controller, username):
        super().__init__(parent)
        self.controller = controller
        self.username = username
        
        # Title
        title = tk.Label(self, text="👤 Account", font=("Arial", 24, "bold"), fg="#2c3e50")
        title.pack(pady=30)
        
        # Account info frame
        info_frame = tk.Frame(self, bg="#ecf0f1", relief="ridge", bd=2)
        info_frame.pack(pady=20, padx=80, fill="both", expand=True)
        
        user_data = controller.get_user_data(username)
        
        # Username
        tk.Label(info_frame, text="Username", font=("Arial", 12, "bold"), 
                bg="#ecf0f1", fg="#7f8c8d").pack(pady=(30, 5))
        tk.Label(info_frame, text=username, font=("Arial", 18), 
                bg="#ecf0f1", fg="#2c3e50").pack()
        
        # Phone
        tk.Label(info_frame, text="Phone Number", font=("Arial", 12, "bold"), 
                bg="#ecf0f1", fg="#7f8c8d").pack(pady=(20, 5))
        tk.Label(info_frame, text=user_data['phone'], font=("Arial", 18), 
                bg="#ecf0f1", fg="#2c3e50").pack()
        
        # Status
        tk.Label(info_frame, text="Account Status", font=("Arial", 12, "bold"), 
                bg="#ecf0f1", fg="#7f8c8d").pack(pady=(20, 5))
        
        status_color = "#27ae60" if user_data['status'] == "Approved" else "#e67e22"
        tk.Label(info_frame, text=user_data['status'], font=("Arial", 18, "bold"), 
                bg="#ecf0f1", fg=status_color).pack()
        
        # Member since (placeholder)
        tk.Label(info_frame, text="Member Since", font=("Arial", 12, "bold"), 
                bg="#ecf0f1", fg="#7f8c8d").pack(pady=(20, 5))
        tk.Label(info_frame, text="December 2024", font=("Arial", 18), 
                bg="#ecf0f1", fg="#2c3e50").pack()
        
        # Buttons frame
        btn_frame = tk.Frame(info_frame, bg="#ecf0f1")
        btn_frame.pack(pady=30)
        
        # Edit phone button
        edit_btn = tk.Button(btn_frame, text="Edit Phone Number", 
                            command=self.edit_phone,
                            bg="#3498db", fg="white", font=("Arial", 11, "bold"),
                            width=18, cursor="hand2", relief="flat", pady=8)
        edit_btn.grid(row=0, column=0, padx=10)
        
        # Logout button
        logout_btn = tk.Button(btn_frame, text="Logout", 
                              command=self.logout,
                              bg="#e74c3c", fg="white", font=("Arial", 11, "bold"),
                              width=18, cursor="hand2", relief="flat", pady=8)
        logout_btn.grid(row=0, column=1, padx=10)
    
    def edit_phone(self):
        # Create popup for editing phone
        popup = tk.Toplevel(self)
        popup.title("Edit Phone Number")
        popup.geometry("350x150")
        popup.resizable(False, False)
        popup.grab_set()
        
        tk.Label(popup, text="New Phone Number:", font=("Arial", 11)).pack(pady=20)
        
        phone_entry = tk.Entry(popup, font=("Arial", 12), width=25)
        phone_entry.pack(pady=5)
        
        def save_phone():
            new_phone = phone_entry.get().strip()
            if not new_phone:
                messagebox.showerror("Error", "Phone number cannot be empty!")
                return
            
            self.controller.update_phone(self.username, new_phone)
            messagebox.showinfo("Success", "Phone number updated!")
            popup.destroy()
            self.controller.refresh_page()
        
        tk.Button(popup, text="Save", command=save_phone,
                 bg="#27ae60", fg="white", font=("Arial", 10, "bold"),
                 width=12, cursor="hand2").pack(pady=10)
    
    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.controller.logout()