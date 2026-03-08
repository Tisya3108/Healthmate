import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class HealthMateApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Health Mate - Daily Calorie Tracker")
        self.root.geometry("1200x700")
        self.root.configure(bg='#f0f8ff')
        
        # Initialize database
        self.setup_database()
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        
        self.setup_gui()
        self.refresh_data()
        self.update_datetime()
    
    def setup_database(self):
        """Initialize SQLite database and create tables"""
        try:
            self.conn = sqlite3.connect('health_mate.db', check_same_thread=False)
            self.cursor = self.conn.cursor()
            
            # Create tables
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS food_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    calories REAL NOT NULL,
                    category TEXT NOT NULL,
                    type TEXT NOT NULL DEFAULT 'manual'
                )
            ''')
            
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_intake (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    food_id INTEGER,
                    food_name TEXT NOT NULL,
                    calories REAL NOT NULL,
                    quantity REAL NOT NULL DEFAULT 1,
                    date TEXT NOT NULL,
                    FOREIGN KEY (food_id) REFERENCES food_items (id)
                )
            ''')
            
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    daily_calorie_goal REAL DEFAULT 2000,
                    created_date TEXT NOT NULL
                )
            ''')
            
            # Populate initial data
            self.populate_initial_data()
            self.conn.commit()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to initialize database: {e}")
    
    def populate_initial_data(self):
        """Populate database with initial food items"""
        try:
            # Check if food items already exist
            self.cursor.execute("SELECT COUNT(*) FROM food_items")
            count = self.cursor.fetchone()[0]
            
            if count == 0:
                # Indian food items
                indian_foods = [
                    ('Chapati', 70, 'Indian Bread', 'indian'),
                    ('Rice (1 cup)', 205, 'Grains', 'indian'),
                    ('Dal (1 bowl)', 150, 'Lentils', 'indian'),
                    ('Chicken Curry', 250, 'Non-Veg', 'indian'),
                    ('Paneer Butter Masala', 350, 'Vegetarian', 'indian'),
                    ('Samosa', 260, 'Snacks', 'indian'),
                    ('Idli', 60, 'Breakfast', 'indian'),
                    ('Dosa', 150, 'Breakfast', 'indian'),
                    ('Biryani', 400, 'Main Course', 'indian'),
                    ('Butter Chicken', 450, 'Non-Veg', 'indian'),
                    ('Roti', 100, 'Indian Bread', 'indian'),
                    ('Paratha', 200, 'Indian Bread', 'indian'),
                    ('Poha', 150, 'Breakfast', 'indian'),
                    ('Upma', 180, 'Breakfast', 'indian'),
                    ('Chole Bhature', 500, 'Main Course', 'indian')
                ]
                
                # International food items
                international_foods = [
                    ('Pizza (slice)', 285, 'Fast Food', 'international'),
                    ('Burger', 354, 'Fast Food', 'international'),
                    ('Pasta (1 cup)', 220, 'Italian', 'international'),
                    ('Sandwich', 300, 'Fast Food', 'international'),
                    ('Salad', 150, 'Healthy', 'international'),
                    ('Apple', 95, 'Fruits', 'international'),
                    ('Banana', 105, 'Fruits', 'international'),
                    ('Orange', 62, 'Fruits', 'international'),
                    ('Milk (1 cup)', 150, 'Dairy', 'international'),
                    ('Egg (boiled)', 78, 'Protein', 'international'),
                    ('Bread (slice)', 80, 'Grains', 'international'),
                    ('Cheese (slice)', 113, 'Dairy', 'international'),
                    ('Yogurt (1 cup)', 150, 'Dairy', 'international'),
                    ('Chicken Breast (100g)', 165, 'Protein', 'international'),
                    ('Fish (100g)', 206, 'Protein', 'international')
                ]
                
                # Insert all food items
                all_foods = indian_foods + international_foods
                self.cursor.executemany(
                    "INSERT INTO food_items (name, calories, category, type) VALUES (?, ?, ?, ?)",
                    all_foods
                )
            
            # Check if goal already exists and insert if not
            self.cursor.execute("SELECT COUNT(*) FROM user_goals")
            goal_count = self.cursor.fetchone()[0]
            
            if goal_count == 0:
                # Insert default calorie goal
                self.cursor.execute(
                    "INSERT INTO user_goals (daily_calorie_goal, created_date) VALUES (?, ?)",
                    (2000, datetime.now().strftime("%Y-%m-%d"))
                )
            
            self.conn.commit()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to populate initial data: {e}")
    
    def setup_gui(self):
        """Setup the main GUI components"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="Health Mate - Daily Calorie Tracker", 
                              font=('', 20, 'bold'), bg='#f0f8ff', fg='#2c3e50')
        title_label.pack(pady=10)
        
        # Date and time section
        datetime_frame = ttk.Frame(main_frame)
        datetime_frame.pack(fill=tk.X, pady=10)
        
        # Current date display
        self.date_label = tk.Label(datetime_frame, text="", font=('', 12, 'bold'), bg='#f0f8ff', fg='#2980b9')
        self.date_label.pack(side=tk.LEFT)
        
        # Current time display
        self.time_label = tk.Label(datetime_frame, text="", font=('', 12, 'bold'), bg='#f0f8ff', fg='#c0392b')
        self.time_label.pack(side=tk.RIGHT)
        
        # Goal section
        goal_frame = ttk.Frame(main_frame)
        goal_frame.pack(fill=tk.X, pady=5)
        
        self.goal_label = tk.Label(goal_frame, text="", font=('', 12, 'bold'), bg='#f0f8ff', fg='#e74c3c')
        self.goal_label.pack(side=tk.RIGHT)
        
        # Notebook for tabs (Only 3 tabs now)
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create tabs (Removed Add Food tab)
        self.dashboard_tab = ttk.Frame(notebook)
        self.food_log_tab = ttk.Frame(notebook)
        self.goals_tab = ttk.Frame(notebook)
        
        notebook.add(self.dashboard_tab, text="Dashboard")
        notebook.add(self.food_log_tab, text="Food Log")
        notebook.add(self.goals_tab, text="Goals")
        
        self.setup_dashboard_tab()
        self.setup_food_log_tab()
        self.setup_goals_tab()
    
    def update_datetime(self):
        """Update date and time display every second"""
        current_datetime = datetime.now()
        
        # Format date: Day, Month Date, Year
        date_str = current_datetime.strftime("%A, %B %d, %Y")
        # Format time: HH:MM:SS
        time_str = current_datetime.strftime("%I:%M:%S %p")
        
        self.date_label.config(text=f"Date: {date_str}")
        self.time_label.config(text=f"Time: {time_str}")
        
        # Update every second
        self.root.after(1000, self.update_datetime)
    
    def setup_dashboard_tab(self):
        """Setup dashboard tab with progress and charts"""
        # Progress frame
        progress_frame = ttk.LabelFrame(self.dashboard_tab, text="Today's Progress")
        progress_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.progress_label = tk.Label(progress_frame, text="", font=('', 14), 
                                      bg='#f0f8ff', justify=tk.LEFT, fg='#2c3e50')
        self.progress_label.pack(pady=15, padx=15, anchor=tk.W)
        
        # Chart frame
        chart_frame = ttk.LabelFrame(self.dashboard_tab, text="Weekly Calorie Trend")
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.setup_chart(chart_frame)
    
    def setup_chart(self, parent):
        """Setup matplotlib chart"""
        self.fig, self.ax = plt.subplots(figsize=(10, 4), facecolor='#f0f8ff')
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def setup_food_log_tab(self):
        """Setup food logging tab"""
        # Main frame with left and right panels
        main_log_frame = ttk.Frame(self.food_log_tab)
        main_log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Food database
        left_frame = ttk.LabelFrame(main_log_frame, text="Food Database")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Search frame
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(search_frame, text="🔍 Search Food:", font=('', 10), bg='#f0f8ff').pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30, font=('', 10))
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Add search button
        search_btn = ttk.Button(search_frame, text="Search", 
                              command=self.search_food_button)
        search_btn.pack(side=tk.LEFT, padx=5)
        
        # Add clear search button
        clear_btn = ttk.Button(search_frame, text="Clear", 
                             command=self.clear_search)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        search_entry.bind('<KeyRelease>', self.search_food_live)
        
        # Food list frame
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview for food items
        columns = ('ID', 'Name', 'Calories', 'Category', 'Type')
        self.food_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.food_tree.heading('ID', text='ID')
        self.food_tree.heading('Name', text='Food Name')
        self.food_tree.heading('Calories', text='Calories')
        self.food_tree.heading('Category', text='Category')
        self.food_tree.heading('Type', text='Type')
        
        self.food_tree.column('ID', width=50)
        self.food_tree.column('Name', width=200)
        self.food_tree.column('Calories', width=80)
        self.food_tree.column('Category', width=120)
        self.food_tree.column('Type', width=100)
        
        # Scrollbar for food tree
        food_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.food_tree.yview)
        self.food_tree.configure(yscrollcommand=food_scroll.set)
        
        self.food_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        food_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.food_tree.bind('<Double-1>', self.add_selected_food)
        
        # Quantity and add button
        add_frame = ttk.Frame(left_frame)
        add_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(add_frame, text="Quantity:", font=('', 10), bg='#f0f8ff').pack(side=tk.LEFT)
        self.quantity_var = tk.StringVar(value="1")
        quantity_entry = ttk.Entry(add_frame, textvariable=self.quantity_var, width=10, font=('', 10))
        quantity_entry.pack(side=tk.LEFT, padx=5)
        
        add_btn = ttk.Button(add_frame, text="➕ Add to Today's Log", 
                           command=self.add_selected_food_manual)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        # Right panel - Today's intake and manual entry
        right_frame = ttk.Frame(main_log_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Today's intake frame
        intake_frame = ttk.LabelFrame(right_frame, text="📅 Today's Food Intake")
        intake_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        intake_columns = ('ID', 'Food Name', 'Calories', 'Quantity', 'Total Calories')
        self.intake_tree = ttk.Treeview(intake_frame, columns=intake_columns, show='headings', height=10)
        
        # Configure intake columns
        for col in intake_columns:
            self.intake_tree.heading(col, text=col)
            self.intake_tree.column(col, width=100)
        
        # Scrollbar for intake tree
        intake_scroll = ttk.Scrollbar(intake_frame, orient=tk.VERTICAL, command=self.intake_tree.yview)
        self.intake_tree.configure(yscrollcommand=intake_scroll.set)
        
        self.intake_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        intake_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind Delete key to the treeview widget
        self.intake_tree.bind('<Delete>', self.delete_intake_entry_keyboard)
        
        # Delete button frame
        delete_frame = ttk.Frame(intake_frame)
        delete_frame.pack(fill=tk.X, padx=5, pady=5)
        
        delete_btn = ttk.Button(delete_frame, text="🗑️ Delete Selected Entry (Press Delete Key)", 
                              command=self.delete_selected_intake)
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        clear_all_btn = ttk.Button(delete_frame, text="🧹 Clear All Today's Entries", 
                                 command=self.clear_all_intake)
        clear_all_btn.pack(side=tk.RIGHT, padx=5)
        
        # Manual entry frame
        manual_frame = ttk.LabelFrame(right_frame, text="✏️ Manual Calorie Entry")
        manual_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Manual entry form
        manual_form = ttk.Frame(manual_frame)
        manual_form.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(manual_form, text="Food Name:", font=('', 9), bg='#f0f8ff').grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.manual_name_var = tk.StringVar()
        ttk.Entry(manual_form, textvariable=self.manual_name_var, width=20, font=('', 9)).grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(manual_form, text="Calories:", font=('', 9), bg='#f0f8ff').grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.manual_calories_var = tk.StringVar()
        ttk.Entry(manual_form, textvariable=self.manual_calories_var, width=10, font=('', 9)).grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(manual_form, text="Quantity:", font=('', 9), bg='#f0f8ff').grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.manual_quantity_var = tk.StringVar(value="1")
        ttk.Entry(manual_form, textvariable=self.manual_quantity_var, width=10, font=('', 9)).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(manual_form, text="➕ Add Manual Entry", 
                  command=self.add_manual_entry).grid(row=1, column=2, columnspan=2, padx=5, pady=5, sticky=tk.EW)
    
    def setup_goals_tab(self):
        """Setup goals tab"""
        # Goals frame
        goals_frame = ttk.LabelFrame(self.goals_tab, text="🎯 Daily Calorie Goal")
        goals_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(goals_frame, text="Set Your Daily Calorie Goal:", 
                font=('', 14), bg='#f0f8ff', fg='#2c3e50').pack(pady=20)
        
        goal_value_frame = ttk.Frame(goals_frame)
        goal_value_frame.pack(pady=10)
        
        self.goal_var = tk.StringVar()
        self.goal_entry = ttk.Entry(goal_value_frame, textvariable=self.goal_var, 
                                   width=10, font=('', 12), justify=tk.CENTER)
        self.goal_entry.pack(side=tk.LEFT, padx=10)
        
        tk.Label(goal_value_frame, text="calories per day", 
                font=('', 12), bg='#f0f8ff').pack(side=tk.LEFT, padx=10)
        
        ttk.Button(goals_frame, text="🔄 Update Goal", 
                  command=self.update_goal).pack(pady=20)
        
        # Current goal display
        self.current_goal_label = tk.Label(goals_frame, text="", font=('', 12, 'bold'), 
                                         bg='#f0f8ff', fg='#27ae60')
        self.current_goal_label.pack(pady=10)
        
        # Tips frame
        tips_frame = ttk.LabelFrame(self.goals_tab, text="💡 Health Tips")
        tips_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tips_text = """
• Average daily calorie needs:
  - Men: 2000-2500 calories
  - Women: 1800-2200 calories
  - Teens: 2200-3000 calories
  
• For weight loss: Reduce 500 calories from maintenance
• For weight gain: Add 500 calories to maintenance

Healthy Habits:
✓ Drink plenty of water throughout the day
✓ Include protein in every meal
✓ Eat more fruits and vegetables
✓ Limit processed foods and sugars
✓ Exercise regularly
✓ Get adequate sleep
"""
        
        tips_label = tk.Label(tips_frame, text=tips_text, font=('', 10),
                             bg='#f0f8ff', justify=tk.LEFT)
        tips_label.pack(pady=15, padx=15, anchor=tk.W)
    
    # Database operations
    def add_food_item(self, name, calories, category, food_type='manual'):
        """Add new food item to database"""
        try:
            self.cursor.execute(
                "INSERT INTO food_items (name, calories, category, type) VALUES (?, ?, ?, ?)",
                (name, calories, category, food_type)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to add food item: {e}")
            return None
    
    def get_food_items(self, search_term=None):
        """Get food items from database"""
        try:
            if search_term:
                self.cursor.execute(
                    "SELECT * FROM food_items WHERE name LIKE ? ORDER BY name",
                    (f'%{search_term}%',)
                )
            else:
                self.cursor.execute("SELECT * FROM food_items ORDER BY name")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to get food items: {e}")
            return []
    
    def add_daily_intake(self, food_id, food_name, calories, quantity, date):
        """Add food intake to daily log"""
        try:
            self.cursor.execute(
                "INSERT INTO daily_intake (food_id, food_name, calories, quantity, date) VALUES (?, ?, ?, ?, ?)",
                (food_id, food_name, calories, quantity, date)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to add intake: {e}")
            return None
    
    def get_daily_intake(self, date):
        """Get daily food intake"""
        try:
            self.cursor.execute(
                "SELECT * FROM daily_intake WHERE date = ? ORDER BY id DESC",
                (date,)
            )
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to get daily intake: {e}")
            return []
    
    def get_total_calories(self, date):
        """Get total calories for a date"""
        try:
            self.cursor.execute(
                "SELECT SUM(calories * quantity) FROM daily_intake WHERE date = ?",
                (date,)
            )
            result = self.cursor.fetchone()
            return result[0] if result and result[0] is not None else 0
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to get total calories: {e}")
            return 0
    
    def get_calorie_goal(self):
        """Get user's calorie goal"""
        try:
            self.cursor.execute("SELECT daily_calorie_goal FROM user_goals WHERE id = 1")
            result = self.cursor.fetchone()
            if result:
                return result[0]
            else:
                # If no goal exists, create one with default value
                self.cursor.execute(
                    "INSERT INTO user_goals (daily_calorie_goal, created_date) VALUES (?, ?)",
                    (2000, datetime.now().strftime("%Y-%m-%d"))
                )
                self.conn.commit()
                return 2000
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to get calorie goal: {e}")
            return 2000
    
    def update_calorie_goal(self, goal):
        """Update calorie goal"""
        try:
            # First check if a goal exists
            self.cursor.execute("SELECT COUNT(*) FROM user_goals WHERE id = 1")
            count = self.cursor.fetchone()[0]
            
            if count == 0:
                # Insert new goal
                self.cursor.execute(
                    "INSERT INTO user_goals (daily_calorie_goal, created_date) VALUES (?, ?)",
                    (goal, datetime.now().strftime("%Y-%m-%d"))
                )
            else:
                # Update existing goal
                self.cursor.execute(
                    "UPDATE user_goals SET daily_calorie_goal = ? WHERE id = 1",
                    (goal,)
                )
            
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to update goal: {e}")
            return False
    
    def delete_intake_entry(self, entry_id):
        """Delete intake entry"""
        try:
            self.cursor.execute("DELETE FROM daily_intake WHERE id = ?", (entry_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to delete entry: {e}")
            return False
    
    def clear_all_intake_entries(self, date):
        """Clear all intake entries for a specific date"""
        try:
            self.cursor.execute("DELETE FROM daily_intake WHERE date = ?", (date,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to clear entries: {e}")
            return False
    
    # GUI operations
    def refresh_data(self):
        """Refresh all data displays"""
        self.load_food_items()
        self.load_today_intake()
        self.update_progress()
        self.update_chart()
        self.update_goal_display()
    
    def load_food_items(self):
        """Load food items into treeview"""
        try:
            self.food_tree.delete(*self.food_tree.get_children())
            food_items = self.get_food_items()
            for item in food_items:
                self.food_tree.insert('', tk.END, values=item)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load food items: {e}")
    
    def load_today_intake(self):
        """Load today's intake into treeview"""
        try:
            self.intake_tree.delete(*self.intake_tree.get_children())
            intake_items = self.get_daily_intake(self.current_date)
            for item in intake_items:
                total_calories = item[3] * item[4]  # calories * quantity
                self.intake_tree.insert('', tk.END, values=(
                    item[0], item[2], item[3], item[4], f"{total_calories:.1f}"
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load intake: {e}")
    
    def search_food_live(self, event=None):
        """Search food items as user types"""
        search_term = self.search_var.get().strip()
        try:
            self.food_tree.delete(*self.food_tree.get_children())
            food_items = self.get_food_items(search_term)
            for item in food_items:
                self.food_tree.insert('', tk.END, values=item)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to search food items: {e}")
    
    def search_food_button(self):
        """Search food items when search button is clicked"""
        self.search_food_live()
    
    def clear_search(self):
        """Clear search and show all food items"""
        self.search_var.set("")
        self.load_food_items()
    
    def add_selected_food(self, event=None):
        """Add selected food to intake"""
        selection = self.food_tree.selection()
        if selection:
            self.add_selected_food_manual()
    
    def add_selected_food_manual(self):
        """Add selected food with quantity"""
        selection = self.food_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a food item")
            return
        
        try:
            item = self.food_tree.item(selection[0])['values']
            food_id, food_name, calories, category, food_type = item
            
            quantity = float(self.quantity_var.get())
            if quantity <= 0:
                messagebox.showerror("Error", "Please enter a valid quantity")
                return
            
            self.add_daily_intake(food_id, food_name, calories, quantity, self.current_date)
            self.load_today_intake()
            self.update_progress()
            self.update_chart()
            messagebox.showinfo("Success", f"Added {food_name} to today's log")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add food: {e}")
    
    def add_manual_entry(self):
        """Add manual calorie entry"""
        food_name = self.manual_name_var.get().strip()
        calories_str = self.manual_calories_var.get().strip()
        quantity_str = self.manual_quantity_var.get().strip()
        
        if not food_name or not calories_str:
            messagebox.showerror("Error", "Please enter food name and calories")
            return
        
        try:
            calories = float(calories_str)
            quantity = float(quantity_str) if quantity_str else 1.0
            if calories <= 0 or quantity <= 0:
                raise ValueError
            
            self.add_daily_intake(None, food_name, calories, quantity, self.current_date)
            self.load_today_intake()
            self.update_progress()
            self.update_chart()
            
            # Clear manual entry fields
            self.manual_name_var.set("")
            self.manual_calories_var.set("")
            self.manual_quantity_var.set("1")
            
            messagebox.showinfo("Success", "Manual entry added successfully")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for calories and quantity")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add manual entry: {e}")
    
    def delete_selected_intake(self):
        """Delete selected intake entry"""
        selection = self.intake_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an entry to delete")
            return
        
        try:
            entry_id = self.intake_tree.item(selection[0])['values'][0]
            food_name = self.intake_tree.item(selection[0])['values'][1]
            
            result = messagebox.askyesno("Confirm Delete", 
                                       f"Are you sure you want to delete '{food_name}'?")
            if result:
                success = self.delete_intake_entry(entry_id)
                if success:
                    self.load_today_intake()
                    self.update_progress()
                    self.update_chart()
                    messagebox.showinfo("Success", "Entry deleted successfully")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete entry: {e}")
    
    def delete_intake_entry_keyboard(self, event):
        """Delete intake entry from database (keyboard binding)"""
        self.delete_selected_intake()
    
    def clear_all_intake(self):
        """Clear all intake entries for today"""
        try:
            intake_items = self.get_daily_intake(self.current_date)
            if not intake_items:
                messagebox.showinfo("Info", "No entries to clear")
                return
            
            result = messagebox.askyesno("Confirm Clear All", 
                                       "Are you sure you want to clear ALL of today's entries?")
            if result:
                success = self.clear_all_intake_entries(self.current_date)
                if success:
                    self.load_today_intake()
                    self.update_progress()
                    self.update_chart()
                    messagebox.showinfo("Success", "All entries cleared successfully")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear entries: {e}")
    
    def update_goal(self):
        """Update calorie goal"""
        try:
            goal_str = self.goal_var.get().strip()
            if not goal_str:
                messagebox.showerror("Error", "Please enter a calorie goal")
                return
                
            goal = float(goal_str)
            if goal <= 0:
                messagebox.showerror("Error", "Please enter a positive number for calorie goal")
                return
            
            # Update the goal in database
            success = self.update_calorie_goal(goal)
            if success:
                # Refresh all displays to show updated goal
                self.update_goal_display()
                self.update_progress()
                self.update_chart()
                messagebox.showinfo("Success", f"Calorie goal updated to {goal} calories")
            else:
                messagebox.showerror("Error", "Failed to update calorie goal")
                
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for calorie goal")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update goal: {e}")
    
    def update_progress(self):
        """Update progress display"""
        try:
            total_calories = self.get_total_calories(self.current_date)
            goal = self.get_calorie_goal()
            remaining = goal - total_calories
            progress_percent = (total_calories/goal)*100 if goal > 0 else 0
            
            # Color coding based on progress
            if progress_percent < 70:
                color = '#27ae60'  # Green
                status = "Good progress!"
            elif progress_percent < 90:
                color = '#f39c12'  # Orange
                status = "Almost there!"
            else:
                color = '#e74c3c'  # Red
                status = "Goal reached!"
            
            progress_text = f"""Total Calories Today: {total_calories:.1f} cal
Daily Goal: {goal} cal
Remaining: {remaining:.1f} cal
Progress: {progress_percent:.1f}% of goal

Status: {status}"""
            
            self.progress_label.config(text=progress_text, fg=color)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update progress: {e}")
    
    def update_goal_display(self):
        """Update goal display"""
        try:
            goal = self.get_calorie_goal()
            # Update the main goal label
            self.goal_label.config(text=f"Daily Goal: {goal} calories")
            # Update the current goal label in Goals tab
            self.current_goal_label.config(text=f"Current Goal: {goal} calories")
            # Update the goal entry field with current value
            self.goal_var.set(str(goal))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update goal display: {e}")
    
    def update_chart(self):
        """Update weekly chart"""
        try:
            # Get last 7 days data
            dates = []
            calories = []
            
            for i in range(6, -1, -1):
                date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                total = self.get_total_calories(date)
                dates.append(date[-5:])  # Show only MM-DD
                calories.append(total)
            
            self.ax.clear()
            
            # Create bars with different colors based on goal
            goal = self.get_calorie_goal()
            colors = ['#27ae60' if cal <= goal else '#e74c3c' for cal in calories]
            bars = self.ax.bar(dates, calories, color=colors, alpha=0.7, edgecolor='black')
            
            # Add value labels on bars
            for bar, value in zip(bars, calories):
                if value > 0:
                    self.ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
                               f'{value:.0f}', ha='center', va='bottom', fontweight='bold')
            
            # Add goal line
            self.ax.axhline(y=goal, color='red', linestyle='--', linewidth=2, label=f'Daily Goal: {goal} cal')
            
            self.ax.set_ylabel('Calories')
            self.ax.set_xlabel('Date')
            self.ax.set_title('Weekly Calorie Intake Trend')
            self.ax.legend()
            self.ax.grid(True, alpha=0.3)
            
            # Rotate x-axis labels for better readability
            plt.setp(self.ax.get_xticklabels(), rotation=45)
            
            self.fig.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update chart: {e}")
    
    def __del__(self):
        """Close database connection when object is destroyed"""
        if hasattr(self, 'conn'):
            self.conn.close()

def main():
    """Main function to run the application"""
    try:
        root = tk.Tk()
        app = HealthMateApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Error: {e}")
        messagebox.showerror("Error", f"Application failed to start: {e}")

if __name__ == "__main__":
    main()
