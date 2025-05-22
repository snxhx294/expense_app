from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with environment variable in production

# Database Configuration
db_config = {
    'host': "localhost",
    'user': "root",
    'password': "snxhx*472",
    'database': "expense_app"
}

# Decorator: Login Required
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("You need to log in first.")
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

# Helper: Fetch All Data
def fetch_all(query, params=None):
    try:
        with mysql.connector.connect(**db_config) as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params or ())
            return cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"Error fetching data: {err}")
        return []

# Route: Home
@app.route('/')
def home():
    return '''
    <h1>Welcome to the Expense Tracker</h1>
    <a href="/register">Register</a> |
    <a href="/login">Login</a>
    '''

# Route: Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password)

        try:
            with mysql.connector.connect(**db_config) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
                conn.commit()
            flash("User registered successfully! Please log in.")
            return redirect('/login')
        except mysql.connector.Error as err:
            flash(f"Error: {err}")
    return render_template('register.html')

# Route: Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        try:
            with mysql.connector.connect(**db_config) as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
                user = cursor.fetchone()
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                flash("Login successful!")
                return redirect('/view_expenses')
            else:
                flash("Invalid username or password.")
        except mysql.connector.Error as err:
            flash(f"Error: {err}")
    return render_template('login.html')

# Route: Add Expense
@app.route('/add_expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        category_id = request.form.get('category')
        subcategory_id = request.form.get('subcategory')
        amount = request.form.get('amount')
        title = request.form.get('title')
        description = request.form.get('description')

        try:
            with mysql.connector.connect(**db_config) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO expenses (user_id, category_id, subcategory_id, amount, title, description)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (session['user_id'], category_id, subcategory_id, amount, title, description))
                conn.commit()
            flash('Expense added successfully!')
            return redirect('/view_expenses')
        except mysql.connector.Error as err:
            flash(f"Error adding expense: {err}")

    categories = fetch_all("SELECT id, name FROM categories")
    subcategories = fetch_all("SELECT id, name FROM subcategories")
    return render_template('add_expense.html', categories=categories, subcategories=subcategories)

# Route: View Expenses
@app.route('/view_expenses', methods=['GET'])
@login_required
def view_expenses():
    expenses = fetch_all("""
    SELECT e.id, e.title, e.amount, e.description, c.name AS category, sc.name AS subcategory
    FROM expenses e
    JOIN categories c ON e.category_id = c.id
    JOIN subcategories sc ON e.subcategory_id = sc.id
    WHERE e.user_id = %s
    """, (session['user_id'],))
    return render_template('view_expenses.html', expenses=expenses)

# Route: Add Category
@app.route('/add_category', methods=['GET', 'POST'])
@login_required
def add_category():
    if request.method == 'POST':
        category_name = request.form.get('category_name')
        try:
            with mysql.connector.connect(**db_config) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO categories (name) VALUES (%s)", (category_name,))
                conn.commit()
            flash("Category added successfully!")
            return redirect('/add_category')
        except mysql.connector.Error as err:
            flash(f"Error: {err}")
    return render_template('add_category.html')

# Route: Add Subcategory
@app.route('/add_subcategory', methods=['GET', 'POST'])
@login_required
def add_subcategory():
    if request.method == 'POST':
        subcategory_name = request.form.get('subcategory_name')
        try:
            with mysql.connector.connect(**db_config) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO subcategories (name) VALUES (%s)", (subcategory_name,))
                conn.commit()
            flash("Subcategory added successfully!")
            return redirect('/add_subcategory')
        except mysql.connector.Error as err:
            flash(f"Error: {err}")
    return render_template('add_subcategory.html')

def fetch_all(query, params=None):
    with mysql.connector.connect(**db_config) as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        results = cursor.fetchall()
    return results

def get_expense_by_id(expense_id):
    with mysql.connector.connect(**db_config) as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM expenses WHERE id = %s", (expense_id,))
        expense = cursor.fetchone()
    return expense

def get_all_categories():
    return fetch_all("SELECT id, name FROM categories")

def get_all_subcategories():
    return fetch_all("SELECT id, name FROM subcategories")

def delete_expense_by_id(expense_id):
    try:
        with mysql.connector.connect(**db_config) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM expenses WHERE id = %s", (expense_id,))
            conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error deleting expense: {err}")
        return False

# Route: Edit Expense
@app.route('/edit_expense/<int:expense_id>', methods=['GET', 'POST'])
@login_required
def edit_expense(expense_id):
    if request.method == 'POST':
        # Handle form submission
        pass
    expense = get_expense_by_id(expense_id)  # Replace with your function to fetch the expense
    categories = get_all_categories()       # Replace with your function to fetch categories
    subcategories = get_all_subcategories() # Replace with your function to fetch subcategories
    return render_template('edit_expense.html', expense=expense, categories=categories, subcategories=subcategories)

# Route: Delete Expense
@app.route('/delete_expense/<int:expense_id>', methods=['GET', 'POST'])
@login_required
def delete_expense(expense_id):
    if request.method == 'POST':
        # Handle the deletion logic
        delete_expense_by_id(expense_id)  # Replace with your function to delete the expense
        flash('Expense deleted successfully!', 'success')
        return redirect('/view_expenses')

    expense = get_expense_by_id(expense_id)  # Replace with your function to fetch the expense
    return render_template('delete_expense.html', expense=expense)


if __name__ == '__main__':
    app.run(debug=True)
