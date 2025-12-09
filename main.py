import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# For PC lock functionality
try:
    import ctypes
    import win32con
    import win32gui
    PC_LOCK_ENABLED = True
except ImportError:
    PC_LOCK_ENABLED = False
    print("PC Lock features require pywin32: pip install pywin32")

# Import your pages
try:
    from Scripts.user_home import HomePage
    from Scripts.user_account import AccountPage
    from Scripts.user_cafe import CafePage
except ImportError:
    # Create dummy classes for testing
    class HomePage:
        def __init__(self, parent, app, username):
            self.frame = tk.Frame(parent, bg="white")
            tk.Label(self.frame, text="Home Page", font=("Arial", 24)).pack(pady=50)
            self.frame.pack(fill="both", expand=True)
    
    class AccountPage:
        def __init__(self, parent, app, username):
            self.frame = tk.Frame(parent, bg="white")
            tk.Label(self.frame, text="Account Page", font=("Arial", 24)).pack(pady=50)
            self.frame.pack(fill="both", expand=True)
    
    class CafePage:
        def __init__(self, parent, app, username):
            self.frame = tk.Frame(parent, bg="white")
            tk.Label(self.frame, text="Cafe Page", font=("Arial", 24)).pack(pady=50)
            self.frame.pack(fill="both", expand=True)

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Initialize variables first
        self.users = {}
        self.admins = {
            "admin": {"password": "admin123", "status": "Approved"}  # Default admin
        }
        self.pending_admins = {}
        self.food_items = {
            "C1": {"name": "Coffee", "price": 50, "points": 1},
            "S1": {"name": "Softdrink", "price": 30, "points": 1},
            "B1": {"name": "Burger", "price": 80, "points": 2},
            "F1": {"name": "Fries", "price": 40, "points": 1},
        }
        self.slots = {i: "Vacant" for i in range(1, 11)}
        
        self.current_user = None
        self.system_locked = True
        
        # Setup window
        self.setup_window()
        
        # Bind keys
        self.bind_keys()
        
        # Show login
        self.show_login()
    
    def setup_window(self):
        """Setup window properties"""
        self.attributes('-fullscreen', True)
        self.title("Cafe PC System - Locked")
        self.attributes('-topmost', True)
        self.overrideredirect(True)
    
    def bind_keys(self):
        """Bind keyboard shortcuts"""
        self.bind_all("<Alt_L>", self.disable_keys)
        self.bind_all("<Alt_R>", self.disable_keys)
        self.bind_all("<Control_L>", self.disable_keys)
        self.bind_all("<Control_R>", self.disable_keys)
        self.bind_all("<Tab>", self.disable_keys)
        self.bind_all("<Escape>", self.show_escape_dialog)
        
        # Enable Windows key blocking if available
        if PC_LOCK_ENABLED:
            self.block_windows_key()
    
    def disable_keys(self, event):
        """Disable Alt, Ctrl, Tab keys"""
        return "break"
    
    def show_escape_dialog(self, event=None):
        """Show password dialog for escaping - ALWAYS works"""
        self.show_unlock_dialog()
        return "break"
    
    def show_unlock_dialog(self):
        """Dialog for unlocking system"""
        popup = tk.Toplevel(self)
        popup.title("System Unlock")
        popup.geometry("350x200")
        popup.resizable(False, False)
        popup.attributes('-topmost', True)
        popup.grab_set()
        
        # Center the dialog
        popup.update_idletasks()
        x = (self.winfo_screenwidth() - popup.winfo_width()) // 2
        y = (self.winfo_screenheight() - popup.winfo_height()) // 2
        popup.geometry(f"+{x}+{y}")
        
        tk.Label(popup, text="🔒 System Unlock", font=("Arial", 16, "bold"), fg="#e74c3c").pack(pady=15)
        tk.Label(popup, text="Admin password required", font=("Arial", 10)).pack(pady=5)
        
        tk.Label(popup, text="Admin Password:", font=("Arial", 11)).pack(pady=(10, 0))
        password_entry = tk.Entry(popup, font=("Arial", 12), width=20, show="*")
        password_entry.pack(pady=10)
        password_entry.focus()
        
        def unlock_system():
            password = password_entry.get().strip()
            
            # Check admin passwords
            for admin_info in self.admins.values():
                if admin_info["password"] == password:
                    popup.destroy()
                    self.system_locked = False
                    
                    # Ask what to do
                    choice = messagebox.askyesno("Unlocked", 
                        "System unlocked!\n\nDo you want to exit the application?", 
                        parent=self)
                    
                    if choice:
                        if PC_LOCK_ENABLED:
                            self.enable_windows_key()
                        self.quit()
                    else:
                        # Continue with unlocked system
                        if PC_LOCK_ENABLED:
                            self.enable_windows_key()
                        # Remove topmost attribute to allow minimizing
                        self.attributes('-topmost', False)
                        # Restore window decorations for minimizing
                        self.overrideredirect(False)
                        self.title("Cafe PC System - Unlocked")
                        # If user is logged in, show their interface
                        if self.current_user:
                            self.show_main_interface()
                        else:
                            self.show_login()
                    return
            
            messagebox.showerror("Error", "Incorrect password!", parent=popup)
            password_entry.delete(0, tk.END)
        
        def cancel():
            popup.destroy()
        
        btn_frame = tk.Frame(popup)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Unlock", command=unlock_system,
                 bg="#27ae60", fg="white", font=("Arial", 10, "bold"),
                 width=10, cursor="hand2").pack(side="left", padx=10)
        
        tk.Button(btn_frame, text="Cancel", command=cancel,
                 bg="#95a5a6", fg="white", font=("Arial", 10),
                 width=10, cursor="hand2").pack(side="left", padx=10)
        
        # Enter key to unlock
        popup.bind('<Return>', lambda e: unlock_system())
    
    def block_windows_key(self):
        """Block Windows key using low-level keyboard hook"""
        if PC_LOCK_ENABLED:
            try:
                # Register hotkey to block Windows key
                user32 = ctypes.windll.user32
                user32.RegisterHotKey(None, 1, win32con.MOD_WIN, win32con.VK_LWIN)
                user32.RegisterHotKey(None, 2, win32con.MOD_WIN, win32con.VK_RWIN)
                
                # Also block Alt+Tab
                user32.RegisterHotKey(None, 3, win32con.MOD_ALT, win32con.VK_TAB)
            except:
                pass
    
    def enable_windows_key(self):
        """Enable Windows key"""
        if PC_LOCK_ENABLED:
            try:
                user32 = ctypes.windll.user32
                user32.UnregisterHotKey(None, 1)
                user32.UnregisterHotKey(None, 2)
                user32.UnregisterHotKey(None, 3)
            except:
                pass
    
    # ... [Keep all other methods exactly as they were in your original code] ...
    # Only changed the __init__ and added setup_window(), bind_keys() methods
    # All other methods remain exactly the same as in your original code
    
    def show_new_admin_request(self):
        popup = tk.Toplevel(self)
        popup.title("Request Admin Account")
        popup.geometry("400x350")
        popup.resizable(False, False)
        popup.attributes('-topmost', True)
        popup.grab_set()
        
        tk.Label(popup, text="Request Admin Account", font=("Arial", 16, "bold")).pack(pady=15)
        tk.Label(popup, text="Your request will need approval from existing admin", 
                font=("Arial", 9), fg="#7f8c8d").pack(pady=5)
        
        tk.Label(popup, text="Admin ID:", font=("Arial", 11)).pack(pady=(10, 0))
        admin_id_entry = tk.Entry(popup, font=("Arial", 12), width=25)
        admin_id_entry.pack(pady=5)
        
        tk.Label(popup, text="Password:", font=("Arial", 11)).pack(pady=(5, 0))
        password_entry = tk.Entry(popup, font=("Arial", 12), width=25, show="*")
        password_entry.pack(pady=5)
        
        tk.Label(popup, text="Confirm Password:", font=("Arial", 11)).pack(pady=(5, 0))
        confirm_password_entry = tk.Entry(popup, font=("Arial", 12), width=25, show="*")
        confirm_password_entry.pack(pady=5)
        
        tk.Label(popup, text="Full Name:", font=("Arial", 11)).pack(pady=(5, 0))
        name_entry = tk.Entry(popup, font=("Arial", 12), width=25)
        name_entry.pack(pady=5)
        
        def request_admin():
            try:
                admin_id = admin_id_entry.get().strip()
                password = password_entry.get().strip()
                confirm_password = confirm_password_entry.get().strip()
                name = name_entry.get().strip()
                
                if not admin_id or not password or not name:
                    messagebox.showerror("Error", "All fields are required!")
                    return
                
                if password != confirm_password:
                    messagebox.showerror("Error", "Passwords do not match!")
                    return
                
                if len(password) < 6:
                    messagebox.showerror("Error", "Password must be at least 6 characters!")
                    return
                
                if admin_id in self.admins or admin_id in self.pending_admins:
                    messagebox.showerror("Error", "Admin ID already exists!")
                    return
                
                self.pending_admins[admin_id] = {
                    "password": password,
                    "name": name,
                    "status": "Pending"
                }
                
                messagebox.showinfo("Success", "Admin request submitted! Wait for approval.")
                popup.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Request failed: {str(e)}")
        
        tk.Button(popup, text="Submit Request", command=request_admin,
                 bg="#3498db", fg="white", font=("Arial", 11, "bold"),
                 width=15, cursor="hand2", relief="flat", pady=8).pack(pady=15)
    
    def show_forgot_password(self):
        popup = tk.Toplevel(self)
        popup.title("Forgot Password")
        popup.geometry("400x250")
        popup.resizable(False, False)
        popup.attributes('-topmost', True)
        popup.grab_set()
        
        tk.Label(popup, text="Reset Password", font=("Arial", 16, "bold")).pack(pady=15)
        tk.Label(popup, text="Enter your username and phone number", 
                font=("Arial", 10), fg="#7f8c8d").pack(pady=5)
        
        tk.Label(popup, text="Username:", font=("Arial", 11)).pack(pady=(10, 0))
        username_entry = tk.Entry(popup, font=("Arial", 12), width=25)
        username_entry.pack(pady=5)
        
        tk.Label(popup, text="Phone Number:", font=("Arial", 11)).pack(pady=(5, 0))
        phone_entry = tk.Entry(popup, font=("Arial", 12), width=25)
        phone_entry.pack(pady=5)
        
        def reset_password():
            try:
                username = username_entry.get().strip()
                phone = phone_entry.get().strip()
                
                if not username or not phone:
                    messagebox.showerror("Error", "All fields are required!")
                    return
                
                if username not in self.users:
                    messagebox.showerror("Error", "Username not found!")
                    return
                
                if self.users[username]["phone"] != phone:
                    messagebox.showerror("Error", "Phone number does not match!")
                    return
                
                # Show password reset dialog
                popup.destroy()
                self.show_new_password_dialog(username)
            except Exception as e:
                messagebox.showerror("Error", f"Reset failed: {str(e)}")
        
        tk.Button(popup, text="Verify & Reset", command=reset_password,
                 bg="#27ae60", fg="white", font=("Arial", 11, "bold"),
                 width=15, cursor="hand2", relief="flat", pady=8).pack(pady=15)
    
    def show_new_password_dialog(self, username):
        popup = tk.Toplevel(self)
        popup.title("New Password")
        popup.geometry("350x250")
        popup.resizable(False, False)
        popup.attributes('-topmost', True)
        popup.grab_set()
        
        tk.Label(popup, text="Set New Password", font=("Arial", 16, "bold")).pack(pady=15)
        tk.Label(popup, text=f"For user: {username}", 
                font=("Arial", 10), fg="#7f8c8d").pack(pady=5)
        
        tk.Label(popup, text="New Password:", font=("Arial", 11)).pack(pady=(10, 0))
        new_password_entry = tk.Entry(popup, font=("Arial", 12), width=25, show="*")
        new_password_entry.pack(pady=5)
        
        tk.Label(popup, text="Confirm Password:", font=("Arial", 11)).pack(pady=(5, 0))
        confirm_password_entry = tk.Entry(popup, font=("Arial", 12), width=25, show="*")
        confirm_password_entry.pack(pady=5)
        
        def save_new_password():
            new_password = new_password_entry.get().strip()
            confirm_password = confirm_password_entry.get().strip()
            
            if not new_password:
                messagebox.showerror("Error", "Password cannot be empty!")
                return
            
            if new_password != confirm_password:
                messagebox.showerror("Error", "Passwords do not match!")
                return
            
            if len(new_password) < 4:
                messagebox.showerror("Error", "Password must be at least 4 characters!")
                return
            
            self.users[username]["password"] = new_password
            messagebox.showinfo("Success", "Password reset successfully! You can now login.")
            popup.destroy()
        
        tk.Button(popup, text="Reset Password", command=save_new_password,
                 bg="#27ae60", fg="white", font=("Arial", 11, "bold"),
                 width=15, cursor="hand2", relief="flat", pady=8).pack(pady=15)
    
    def show_admin_login(self):
        popup = tk.Toplevel(self)
        popup.title("Admin Login")
        popup.geometry("350x250")
        popup.resizable(False, False)
        popup.attributes('-topmost', True)
        popup.grab_set()
        
        tk.Label(popup, text="Admin Login", font=("Arial", 16, "bold")).pack(pady=20)
        
        tk.Label(popup, text="Admin ID:", font=("Arial", 11)).pack(pady=(5, 0))
        admin_id_entry = tk.Entry(popup, font=("Arial", 12), width=20)
        admin_id_entry.pack(pady=10)
        
        tk.Label(popup, text="Password:", font=("Arial", 11)).pack(pady=(5, 0))
        password_entry = tk.Entry(popup, font=("Arial", 12), width=20, show="*")
        password_entry.pack(pady=10)
        
        def verify_admin():
            admin_id = admin_id_entry.get().strip()
            password = password_entry.get().strip()
            
            # Check against admin database
            if admin_id in self.admins and self.admins[admin_id]["password"] == password:
                if self.admins[admin_id]["status"] == "Approved":
                    popup.destroy()
                    # When admin logs in, unlock system partially
                    if self.system_locked:
                        self.system_locked = False
                        if PC_LOCK_ENABLED:
                            self.enable_windows_key()
                        self.attributes('-topmost', False)
                        self.title("Cafe PC System - Admin Mode")
                    self.show_admin_panel()
                else:
                    messagebox.showwarning("Pending", "Your admin account is pending approval!")
            else:
                messagebox.showerror("Error", "Incorrect admin ID or password!")
        
        tk.Button(popup, text="Login", command=verify_admin,
                 bg="#e74c3c", fg="white", font=("Arial", 11, "bold"),
                 width=12, cursor="hand2", relief="flat", pady=8).pack(pady=15)
        
        # Add new admin button (not highlighted)
        tk.Button(popup, text="Request New Admin Account", command=self.show_new_admin_request,
                 bg="#ecf0f1", fg="#7f8c8d", font=("Arial", 9),
                 width=25, cursor="hand2", relief="flat", pady=5).pack(pady=5)
    
    def show_admin_panel(self):
        admin_window = tk.Toplevel(self)
        admin_window.title("Admin Panel")
        admin_window.geometry("700x500")
        admin_window.resizable(False, False)
        admin_window.attributes('-topmost', True)
        
        tk.Label(admin_window, text="Admin Dashboard", font=("Arial", 20, "bold")).pack(pady=20)
        
        # Tabs
        tab_control = ttk.Notebook(admin_window)
        
        # Pending user approvals tab
        pending_tab = tk.Frame(tab_control, bg="white")
        tab_control.add(pending_tab, text="Pending Users")
        
        tk.Label(pending_tab, text="Pending User Accounts", 
                font=("Arial", 14, "bold"), bg="white").pack(pady=15)
        
        pending_frame = tk.Frame(pending_tab, bg="white")
        pending_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        pending_users = [u for u in self.users if self.users[u]["status"] == "Pending"]
        
        if not pending_users:
            tk.Label(pending_frame, text="No pending user approvals", 
                    font=("Arial", 12), bg="white", fg="#95a5a6").pack(pady=50)
        else:
            for username in pending_users:
                user_info = self.users[username]
                user_card = tk.Frame(pending_frame, bg="#ecf0f1", relief="ridge", bd=2)
                user_card.pack(pady=5, padx=10, fill="x")
                
                info_text = f"Username: {username} | Phone: {user_info['phone']}"
                tk.Label(user_card, text=info_text, font=("Arial", 11), 
                        bg="#ecf0f1", anchor="w").pack(side="left", padx=15, pady=10)
                
                btn_frame = tk.Frame(user_card, bg="#ecf0f1")
                btn_frame.pack(side="right", padx=10)
                
                tk.Button(btn_frame, text="✓ Approve", 
                         command=lambda u=username: self.approve_user(u, admin_window),
                         bg="#27ae60", fg="white", font=("Arial", 9, "bold"),
                         width=10, cursor="hand2").pack(side="left", padx=5)
                
                tk.Button(btn_frame, text="✗ Reject", 
                         command=lambda u=username: self.reject_user(u, admin_window),
                         bg="#e74c3c", fg="white", font=("Arial", 9, "bold"),
                         width=10, cursor="hand2").pack(side="left", padx=5)
        
        # Pending admin approvals tab
        pending_admin_tab = tk.Frame(tab_control, bg="white")
        tab_control.add(pending_admin_tab, text="Pending Admins")
        
        tk.Label(pending_admin_tab, text="Pending Admin Requests", 
                font=("Arial", 14, "bold"), bg="white").pack(pady=15)
        
        pending_admin_frame = tk.Frame(pending_admin_tab, bg="white")
        pending_admin_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        if not self.pending_admins:
            tk.Label(pending_admin_frame, text="No pending admin requests", 
                    font=("Arial", 12), bg="white", fg="#95a5a6").pack(pady=50)
        else:
            for admin_id, admin_info in self.pending_admins.items():
                admin_card = tk.Frame(pending_admin_frame, bg="#fff3cd", relief="ridge", bd=2)
                admin_card.pack(pady=5, padx=10, fill="x")
                
                info_text = f"Admin ID: {admin_id} | Name: {admin_info['name']}"
                tk.Label(admin_card, text=info_text, font=("Arial", 11), 
                        bg="#fff3cd", anchor="w").pack(side="left", padx=15, pady=10)
                
                btn_frame = tk.Frame(admin_card, bg="#fff3cd")
                btn_frame.pack(side="right", padx=10)
                
                tk.Button(btn_frame, text="✓ Approve", 
                         command=lambda aid=admin_id: self.approve_admin(aid, admin_window),
                         bg="#27ae60", fg="white", font=("Arial", 9, "bold"),
                         width=10, cursor="hand2").pack(side="left", padx=5)
                
                tk.Button(btn_frame, text="✗ Reject", 
                         command=lambda aid=admin_id: self.reject_admin(aid, admin_window),
                         bg="#e74c3c", fg="white", font=("Arial", 9, "bold"),
                         width=10, cursor="hand2").pack(side="left", padx=5)
        
        # All users tab
        users_tab = tk.Frame(tab_control, bg="white")
        tab_control.add(users_tab, text="All Users")
        
        tk.Label(users_tab, text="All User Accounts", 
                font=("Arial", 14, "bold"), bg="white").pack(pady=15)
        
        users_frame = tk.Frame(users_tab, bg="white")
        users_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        if not self.users:
            tk.Label(users_frame, text="No users found", 
                    font=("Arial", 12), bg="white", fg="#95a5a6").pack(pady=50)
        else:
            for username, info in self.users.items():
                user_card = tk.Frame(users_frame, bg="#ecf0f1", relief="ridge", bd=2)
                user_card.pack(pady=5, padx=10, fill="x")
                
                status_color = "#27ae60" if info['status'] == "Approved" else "#e67e22"
                info_text = f"{username} | {info['phone']} | Time: {info['time']}m | Points: {info['points']}"
                
                tk.Label(user_card, text=info_text, font=("Arial", 10), 
                        bg="#ecf0f1", anchor="w").pack(side="left", padx=15, pady=10)
                
                tk.Label(user_card, text=info['status'], font=("Arial", 10, "bold"),
                        bg="#ecf0f1", fg=status_color).pack(side="right", padx=15)
        
        tab_control.pack(expand=1, fill="both", padx=20, pady=10)
    
    def approve_admin(self, admin_id, admin_window):
        if admin_id in self.pending_admins:
            admin_info = self.pending_admins[admin_id]
            self.admins[admin_id] = {
                "password": admin_info["password"],
                "name": admin_info["name"],
                "status": "Approved"
            }
            del self.pending_admins[admin_id]
            messagebox.showinfo("Success", f"Admin '{admin_id}' has been approved!")
            admin_window.destroy()
            self.show_admin_panel()
    
    def reject_admin(self, admin_id, admin_window):
        if messagebox.askyesno("Confirm", f"Reject admin request '{admin_id}'?"):
            del self.pending_admins[admin_id]
            messagebox.showinfo("Rejected", f"Admin request '{admin_id}' has been rejected.")
            admin_window.destroy()
            self.show_admin_panel()
    
    def approve_user(self, username, admin_window):
        if username in self.users:
            self.users[username]["status"] = "Approved"
            self.users[username]["time"] = 100  # Give 100 mins on approval
            messagebox.showinfo("Success", f"User '{username}' has been approved!")
            admin_window.destroy()
            self.show_admin_panel()
    
    def reject_user(self, username, admin_window):
        if messagebox.askyesno("Confirm", f"Reject user '{username}'? This will delete their account."):
            del self.users[username]
            messagebox.showinfo("Rejected", f"User '{username}' has been rejected.")
            admin_window.destroy()
            self.show_admin_panel()
    
    def show_login(self):
        # Clear window
        for widget in self.winfo_children():
            widget.destroy()
        
        # Login screen
        login_frame = tk.Frame(self, bg="#ecf0f1")
        login_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(login_frame, text="🔒 Cafe PC System", font=("Arial", 32, "bold"), 
                fg="#2c3e50", bg="#ecf0f1").pack(pady=30)
        
        tk.Label(login_frame, text="PC Locked - Login Required", font=("Arial", 14), 
                fg="#e74c3c", bg="#ecf0f1").pack(pady=5)
        
        # Username field
        tk.Label(login_frame, text="Username:", font=("Arial", 14), 
                bg="#ecf0f1").pack(pady=10)
        username_entry = tk.Entry(login_frame, font=("Arial", 16), width=25)
        username_entry.pack(pady=10)
        username_entry.focus()
        
        # Password field
        tk.Label(login_frame, text="Password:", font=("Arial", 14), 
                bg="#ecf0f1").pack(pady=10)
        password_entry = tk.Entry(login_frame, font=("Arial", 16), width=25, show="*")
        password_entry.pack(pady=10)
        
        btn_frame = tk.Frame(login_frame, bg="#ecf0f1")
        btn_frame.pack(pady=30)
        
        tk.Button(btn_frame, text="Login", 
                 command=lambda: self.login(username_entry.get(), password_entry.get()),
                 bg="#27ae60", fg="white", font=("Arial", 14, "bold"),
                 width=12, cursor="hand2", relief="flat", pady=12).grid(row=0, column=0, padx=15)
        
        tk.Button(btn_frame, text="Sign Up", command=self.show_signup,
                 bg="#3498db", fg="white", font=("Arial", 14, "bold"),
                 width=12, cursor="hand2", relief="flat", pady=12).grid(row=0, column=1, padx=15)
        
        # Forgot password link
        forgot_btn = tk.Button(login_frame, text="Forgot Password?", 
                              command=self.show_forgot_password,
                              bg="#ecf0f1", fg="#3498db", font=("Arial", 12, "underline"),
                              relief="flat", cursor="hand2", bd=0)
        forgot_btn.pack(pady=10)
        
        # Admin button at bottom
        admin_frame = tk.Frame(self, bg="#ecf0f1")
        admin_frame.pack(side="bottom", pady=20)
        
        tk.Button(admin_frame, text="🔓 Admin Login", command=self.show_admin_login,
                 bg="#e74c3c", fg="white", font=("Arial", 12, "bold"),
                 width=15, cursor="hand2", relief="flat", pady=8).pack()
        
        # Escape info label
        tk.Label(admin_frame, text="Press ESC for emergency unlock", 
                font=("Arial", 9), fg="#95a5a6", bg="#ecf0f1").pack(pady=5)
        
        # Bind Enter key to login
        username_entry.bind('<Return>', lambda e: password_entry.focus())
        password_entry.bind('<Return>', lambda e: self.login(username_entry.get(), password_entry.get()))
    
    def show_signup(self):
        popup = tk.Toplevel(self)
        popup.title("Sign Up")
        popup.geometry("400x400")
        popup.resizable(False, False)
        popup.attributes('-topmost', True)
        popup.grab_set()
        
        tk.Label(popup, text="Create Account", font=("Arial", 16, "bold")).pack(pady=15)
        
        tk.Label(popup, text="Username:", font=("Arial", 11)).pack(pady=(5, 0))
        username_entry = tk.Entry(popup, font=("Arial", 12), width=25)
        username_entry.pack(pady=5)
        
        tk.Label(popup, text="Password:", font=("Arial", 11)).pack(pady=(5, 0))
        password_entry = tk.Entry(popup, font=("Arial", 12), width=25, show="*")
        password_entry.pack(pady=5)
        
        tk.Label(popup, text="Confirm Password:", font=("Arial", 11)).pack(pady=(5, 0))
        confirm_password_entry = tk.Entry(popup, font=("Arial", 12), width=25, show="*")
        confirm_password_entry.pack(pady=5)
        
        tk.Label(popup, text="Phone:", font=("Arial", 11)).pack(pady=(5, 0))
        phone_entry = tk.Entry(popup, font=("Arial", 12), width=25)
        phone_entry.pack(pady=5)
        
        def signup():
            try:
                username = username_entry.get().strip()
                password = password_entry.get().strip()
                confirm_password = confirm_password_entry.get().strip()
                phone = phone_entry.get().strip()
                
                print(f"Signup attempt - Username: {username}, Password length: {len(password)}, Phone: {phone}")  # Debug
                
                if not username or not password or not phone:
                    messagebox.showerror("Error", "All fields are required!")
                    return
                
                if password != confirm_password:
                    messagebox.showerror("Error", "Passwords do not match!")
                    return
                
                if len(password) < 4:
                    messagebox.showerror("Error", "Password must be at least 4 characters!")
                    return
                
                if username in self.users:
                    messagebox.showerror("Error", "Username already exists!")
                    return
                
                self.users[username] = {
                    "password": password,
                    "phone": phone,
                    "time": 0,
                    "points": 0,
                    "streak": 0,
                    "last_login": None,
                    "status": "Pending",
                    "slot": None
                }
                
                print(f"User created successfully: {username}")  # Debug
                messagebox.showinfo("Success", "Account created! Please wait for admin approval.")
                popup.destroy()
            except Exception as e:
                print(f"Signup error: {e}")  # Debug
                messagebox.showerror("Error", f"Signup failed: {str(e)}")
        
        submit_btn = tk.Button(popup, text="Create Account", command=signup,
                              bg="#27ae60", fg="white", font=("Arial", 11, "bold"),
                              width=15, cursor="hand2", relief="flat", pady=8)
        submit_btn.pack(pady=15)
    
    def login(self, username, password):
        username = username.strip()
        password = password.strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Username and password cannot be empty!")
            return
        
        if username not in self.users:
            messagebox.showerror("Error", "Account not found!")
            return
        
        if self.users[username]["password"] != password:
            messagebox.showerror("Error", "Incorrect password!")
            return
        
        if self.users[username]["status"] != "Approved":
            messagebox.showwarning("Pending Approval", "Your account is pending admin approval.")
            return
        
        self.current_user = username
        
        # When user logs in, unlock system partially
        if self.system_locked:
            self.system_locked = False
            if PC_LOCK_ENABLED:
                self.enable_windows_key()
            # Remove topmost attribute to allow minimizing
            self.attributes('-topmost', False)
            # Restore window decorations for minimize/maximize/close buttons
            self.overrideredirect(False)
            self.title("Cafe PC System - User Mode")
        
        self.show_main_interface()
    
    def show_main_interface(self):
        # Clear window
        for widget in self.winfo_children():
            widget.destroy()
        
        # Create main container
        main_container = tk.Frame(self)
        main_container.pack(fill="both", expand=True)
        
        # Sidebar (left navigation)
        sidebar = tk.Frame(main_container, bg="#34495e", width=250)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        
        # Logo/Brand at top of sidebar
        logo_frame = tk.Frame(sidebar, bg="#2c3e50", height=150)
        logo_frame.pack(fill="x")
        logo_frame.pack_propagate(False)
        
        # Create circular logo
        canvas = tk.Canvas(logo_frame, width=120, height=120, bg="#2c3e50", highlightthickness=0)
        canvas.pack(pady=15)
        
        # Draw circles for logo
        canvas.create_oval(10, 10, 110, 110, fill="#95a5a6", outline="#7f8c8d", width=3)
        canvas.create_text(60, 60, text="@", font=("Arial", 48, "bold"), fill="white")
        
        # Navigation buttons container
        nav_container = tk.Frame(sidebar, bg="#34495e")
        nav_container.pack(fill="both", expand=True)
        
        self.nav_buttons = {}
        
        # Home button
        home_btn = tk.Button(nav_container, text="  🏠  Home", 
                           command=lambda: self.show_page("home"),
                           bg="#34495e", fg="white", font=("Arial", 14),
                           anchor="w", padx=20, pady=15, cursor="hand2", 
                           relief="flat", activebackground="#2c3e50", 
                           activeforeground="white", bd=0)
        home_btn.pack(fill="x")
        self.nav_buttons["home"] = home_btn
        
        # Cafe button
        cafe_btn = tk.Button(nav_container, text="  ☕  Cafe", 
                           command=lambda: self.show_page("cafe"),
                           bg="#34495e", fg="white", font=("Arial", 14),
                           anchor="w", padx=20, pady=15, cursor="hand2", 
                           relief="flat", activebackground="#2c3e50", 
                           activeforeground="white", bd=0)
        cafe_btn.pack(fill="x")
        self.nav_buttons["cafe"] = cafe_btn
        
        # Account button
        account_btn = tk.Button(nav_container, text="  👤  Account", 
                               command=lambda: self.show_page("account"),
                               bg="#34495e", fg="white", font=("Arial", 14),
                               anchor="w", padx=20, pady=15, cursor="hand2", 
                               relief="flat", activebackground="#2c3e50", 
                               activeforeground="white", bd=0)
        account_btn.pack(fill="x")
        self.nav_buttons["account"] = account_btn
        
        # Logout button at bottom
        logout_frame = tk.Frame(sidebar, bg="#34495e")
        logout_frame.pack(side="bottom", fill="x", pady=20)
        
        tk.Button(logout_frame, text="  🔓  Logout", command=self.logout,
                 bg="#e74c3c", fg="white", font=("Arial", 12, "bold"),
                 anchor="w", padx=20, pady=12, cursor="hand2", 
                 relief="flat", activebackground="#c0392b", bd=0).pack(fill="x")
        
        # Content area (right side)
        self.content_frame = tk.Frame(main_container, bg="white")
        self.content_frame.pack(side="right", fill="both", expand=True)
        
        # Show home page by default
        self.show_page("home")
        
        # Update window state to normal (allows minimizing)
        self.state('normal')
    
    def show_page(self, page_id):
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Update button colors (highlight active)
        for btn_id, btn in self.nav_buttons.items():
            if btn_id == page_id:
                btn.config(bg="#7f8c8d")  # Lighter gray for active
            else:
                btn.config(bg="#34495e")  # Dark gray for inactive
        
        # Show requested page
        if page_id == "home":
            page = HomePage(self.content_frame, self, self.current_user)
        elif page_id == "account":
            page = AccountPage(self.content_frame, self, self.current_user)
        elif page_id == "cafe":
            page = CafePage(self.content_frame, self, self.current_user)
        
        page.pack(fill="both", expand=True)
    
    def refresh_page(self):
        # Find current active page and refresh it
        current_page = None
        for btn_id, btn in self.nav_buttons.items():
            if btn.cget("bg") == "#3498db":
                current_page = btn_id
                break
        
        if current_page:
            self.show_page(current_page)
    
    # Data access methods
    def get_user_data(self, username):
        return self.users.get(username, {})
    
    def get_food_menu(self):
        return self.food_items
    
    def get_pc_slots(self):
        return self.slots
    
    def update_phone(self, username, new_phone):
        if username in self.users:
            self.users[username]["phone"] = new_phone
    
    def assign_pc(self, username, pc_num):
        if self.slots[pc_num] == "Vacant":
            self.slots[pc_num] = "Occupied"
            self.users[username]["slot"] = pc_num
            return True
        return False
    
    def end_pc_session(self, username):
        if self.users[username]["slot"]:
            pc = self.users[username]["slot"]
            self.slots[pc] = "Vacant"
            self.users[username]["slot"] = None
    
    def place_order(self, username, item_code):
        item = self.food_items[item_code]
        self.users[username]["points"] += item["points"]
    
    def logout(self):
        # Lock system again when user logs out
        self.system_locked = True
        self.current_user = None
        
        # Re-enable PC lock features
        if PC_LOCK_ENABLED:
            self.block_windows_key()
        
        # Go back to fullscreen locked mode
        self.attributes('-fullscreen', True)
        self.attributes('-topmost', True)
        self.overrideredirect(True)
        self.title("Cafe PC System - Locked")
        
        # Show login screen
        self.show_login()


if __name__ == "__main__":
    # Install required packages if not available
    if not PC_LOCK_ENABLED:
        print("Note: PC Lock features disabled. Install pywin32 for full lock functionality:")
        print("pip install pywin32")
    
    app = MainApp()
    
    try:
        app.mainloop()
    except KeyboardInterrupt:
        # Clean up Windows key blocking
        if PC_LOCK_ENABLED:
            app.enable_windows_key()