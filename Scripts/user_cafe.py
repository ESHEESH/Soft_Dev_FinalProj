import tkinter as tk
from tkinter import ttk, messagebox

class CafePage(tk.Frame):
    def __init__(self, parent, controller, username):
        super().__init__(parent)
        self.controller = controller
        self.username = username
        
        # Title
        title = tk.Label(self, text="☕ Cafe Menu", font=("Arial", 24, "bold"), fg="#2c3e50")
        title.pack(pady=30)
        
        # PC Selection section
        pc_frame = tk.LabelFrame(self, text="🖥️ PC Selection", font=("Arial", 14, "bold"),
                                 bg="#ecf0f1", relief="ridge", bd=2, fg="#2c3e50")
        pc_frame.pack(pady=10, padx=80, fill="x")
        
        user_data = controller.get_user_data(username)
        
        if user_data['slot']:
            tk.Label(pc_frame, text=f"Currently using PC {user_data['slot']}", 
                    font=("Arial", 12), bg="#ecf0f1", fg="#27ae60").pack(pady=15)
            
            end_btn = tk.Button(pc_frame, text="End Session", 
                               command=self.end_session,
                               bg="#e74c3c", fg="white", font=("Arial", 11, "bold"),
                               width=15, cursor="hand2", relief="flat", pady=8)
            end_btn.pack(pady=(0, 15))
        else:
            tk.Label(pc_frame, text="No active PC session", 
                    font=("Arial", 12), bg="#ecf0f1", fg="#e67e22").pack(pady=15)
            
            select_btn = tk.Button(pc_frame, text="Select PC", 
                                  command=self.select_pc,
                                  bg="#3498db", fg="white", font=("Arial", 11, "bold"),
                                  width=15, cursor="hand2", relief="flat", pady=8)
            select_btn.pack(pady=(0, 15))
        
        # Food menu section
        food_frame = tk.LabelFrame(self, text="🍔 Food & Drinks", font=("Arial", 14, "bold"),
                                   bg="#ecf0f1", relief="ridge", bd=2, fg="#2c3e50")
        food_frame.pack(pady=10, padx=80, fill="both", expand=True)
        
        # Grid for food items
        items_frame = tk.Frame(food_frame, bg="#ecf0f1")
        items_frame.pack(pady=20, padx=20)
        
        food_items = controller.get_food_menu()
        
        row = 0
        col = 0
        for code, item in food_items.items():
            item_card = tk.Frame(items_frame, bg="white", relief="solid", bd=1)
            item_card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
            
            # Icon based on item type
            icon = "☕" if "Coffee" in item['name'] or "Softdrink" in item['name'] else "🍔"
            
            tk.Label(item_card, text=icon, font=("Arial", 32), bg="white").pack(pady=10)
            tk.Label(item_card, text=item['name'], font=("Arial", 13, "bold"), 
                    bg="white").pack()
            tk.Label(item_card, text=f"₱{item['price']}", font=("Arial", 12), 
                    bg="white", fg="#27ae60").pack(pady=5)
            tk.Label(item_card, text=f"+{item['points']} pts", font=("Arial", 10), 
                    bg="white", fg="#3498db").pack()
            
            order_btn = tk.Button(item_card, text="Order", 
                                 command=lambda c=code: self.order_item(c),
                                 bg="#27ae60", fg="white", font=("Arial", 10, "bold"),
                                 width=10, cursor="hand2", relief="flat")
            order_btn.pack(pady=10)
            
            col += 1
            if col > 1:  # 2 columns
                col = 0
                row += 1
    
    def select_pc(self):
        # Create PC selection popup
        popup = tk.Toplevel(self)
        popup.title("Select PC")
        popup.geometry("400x450")
        popup.resizable(False, False)
        popup.grab_set()
        
        tk.Label(popup, text="Available PCs", font=("Arial", 16, "bold")).pack(pady=20)
        
        slots = self.controller.get_pc_slots()
        
        # Grid for PC slots
        grid_frame = tk.Frame(popup)
        grid_frame.pack(pady=10)
        
        for i, (pc, status) in enumerate(slots.items()):
            row = i // 2
            col = i % 2
            
            is_vacant = status == "Vacant"
            bg_color = "#27ae60" if is_vacant else "#95a5a6"
            
            pc_btn = tk.Button(grid_frame, text=f"PC {pc}\n{status}", 
                              command=lambda p=pc: self.confirm_pc(p, popup) if is_vacant else None,
                              bg=bg_color, fg="white", font=("Arial", 12, "bold"),
                              width=12, height=3, cursor="hand2" if is_vacant else "arrow",
                              relief="flat", state="normal" if is_vacant else "disabled")
            pc_btn.grid(row=row, column=col, padx=10, pady=10)
    
    def confirm_pc(self, pc_num, popup):
        if self.controller.assign_pc(self.username, pc_num):
            messagebox.showinfo("Success", f"You are now using PC {pc_num}!")
            popup.destroy()
            self.controller.refresh_page()
        else:
            messagebox.showerror("Error", "PC is no longer available!")
    
    def end_session(self):
        if messagebox.askyesno("End Session", "Are you sure you want to end your session?"):
            self.controller.end_pc_session(self.username)
            messagebox.showinfo("Session Ended", "Your PC session has ended.")
            self.controller.refresh_page()
    
    def order_item(self, item_code):
        item = self.controller.get_food_menu()[item_code]
        if messagebox.askyesno("Confirm Order", 
                               f"Order {item['name']} for ₱{item['price']}?\n+{item['points']} points"):
            self.controller.place_order(self.username, item_code)
            messagebox.showinfo("Order Placed", 
                              f"Your {item['name']} has been ordered!\n+{item['points']} points added!")
