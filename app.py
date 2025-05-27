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
        date = request.form.get('date')
        description = request.form.get('description')

        try:
            with mysql.connector.connect(**db_config) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO expenses (user_id, category_id, subcategory_id, amount, date, description)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (session['user_id'], category_id, subcategory_id, amount, date, description))
                conn.commit()
            flash('Expense added successfully!')
            return redirect('/view_expenses')
        except mysql.connector.Error as err:
            flash(f"Error adding expense: {err}")

    categories = fetch_all("SELECT id, name FROM categories")
    subcategories = fetch_all("SELECT id, name FROM subcategories")
    return render_template('add_expense.html', categories=categories, subcategories=subcategories)

#Route: View Expenses
@app.route('/view_expenses', methods=['GET'])
@login_required
def view_expenses():
    # Retrieve filter parameters from query string
    filter_date = request.args.get('date')
    filter_category = request.args.get('category')
    filter_payment = request.args.get('payment_method')

    # Base SQL query
    query = """
        SELECT e.id, e.date, e.amount, e.description, c.name AS category, sc.name AS subcategory
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        JOIN subcategories sc ON e.subcategory_id = sc.id
        WHERE e.user_id = %s
    """
    params = [session['user_id']]

    # Add filters dynamically
    if filter_date:
        query += " AND e.date = %s"
        params.append(filter_date)
    if filter_category:
        query += " AND c.name = %s"
        params.append(filter_category)
    if filter_payment:
        query += " AND sc.name = %s"
        params.append(filter_payment)

    # Execute the query
    expenses = fetch_all(query, tuple(params))

    # Fetch unique categories and subcategories for dropdowns
    categories = fetch_all("SELECT DISTINCT name FROM categories")
    subcategories = fetch_all("SELECT DISTINCT name FROM subcategories")

    return render_template(
        'view_expenses.html',
        expenses=expenses,
        categories=[c['name'] for c in categories],
        subcategories=[sc['name'] for sc in subcategories]
    )

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
        payment_method = request.form.get('payment_method_name')  # Match with the name in HTML
        try:
            with mysql.connector.connect(**db_config) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO subcategories (name) VALUES (%s)", (payment_method,))
                conn.commit()
            flash("Payment method added successfully!")
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
        # Fetch updated data from the form
        category_id = request.form.get('category')
        subcategory_id = request.form.get('subcategory')
        amount = request.form.get('amount')
        date = request.form.get('date')
        description = request.form.get('description')

        try:
            with mysql.connector.connect(**db_config) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE expenses
                    SET category_id = %s, subcategory_id = %s, amount = %s, date = %s, description = %s
                    WHERE id = %s AND user_id = %s
                """, (category_id, subcategory_id, amount, date, description, expense_id, session['user_id']))
                conn.commit()
            flash("Expense updated successfully!")
            return redirect('/view_expenses')
        except mysql.connector.Error as err:
            flash(f"Error updating expense: {err}")

    # Fetch the current expense details for the form
    expense = get_expense_by_id(expense_id)
    categories = get_all_categories()
    subcategories = get_all_subcategories()
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

# Route: Manage Categories
@app.route('/manage_categories', methods=['GET'])
@login_required
def manage_categories():
    try:
        # Fetch all categories and subcategories
        with mysql.connector.connect(**db_config) as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM categories")
            categories = cursor.fetchall()

            cursor.execute("SELECT * FROM subcategories")
            subcategories = cursor.fetchall()

        # Render the management page
        return render_template(
            "manage_categories.html",
            categories=categories,
            subcategories=subcategories
        )
    except mysql.connector.Error as err:
        flash(f"Error fetching categories: {err}", "danger")
        return redirect('/view_expenses')

# Route: Edit Category
@app.route('/edit_category/<int:category_id>', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    if request.method == 'POST':
        new_name = request.form['name']

        try:
            # Update the category name
            with mysql.connector.connect(**db_config) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE categories SET name = %s WHERE id = %s",
                    (new_name, category_id)
                )
                conn.commit()

            flash("Category updated successfully!", "success")
            return redirect('/manage_categories')
        except mysql.connector.Error as err:
            flash(f"Error updating category: {err}", "danger")

    # Fetch the category details for the form
    try:
        with mysql.connector.connect(**db_config) as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM categories WHERE id = %s", (category_id,))
            category = cursor.fetchone()

        if not category:
            flash("Category not found.", "danger")
            return redirect('/manage_categories')

        return render_template("edit_category.html", category=category)
    except mysql.connector.Error as err:
        flash(f"Error fetching category: {err}", "danger")
        return redirect('/manage_categories')

# Route: Delete Category
@app.route('/delete_category/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    try:
        with mysql.connector.connect(**db_config) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM categories WHERE id = %s", (category_id,))
            conn.commit()

        flash("Category deleted successfully!", "success")
    except mysql.connector.Error as err:
        flash(f"Error deleting category: {err}", "danger")

    return redirect('/manage_categories')

# Route: Edit Subcategory
@app.route('/edit_subcategory/<int:subcategory_id>', methods=['GET', 'POST'])
@login_required
def edit_subcategory(subcategory_id):
    if request.method == 'POST':
        new_name = request.form['name']

        try:
            # Update the subcategory name
            with mysql.connector.connect(**db_config) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE subcategories SET name = %s WHERE id = %s",
                    (new_name, subcategory_id)
                )
                conn.commit()

            flash("Subcategory updated successfully!", "success")
            return redirect('/manage_categories')
        except mysql.connector.Error as err:
            flash(f"Error updating subcategory: {err}", "danger")

    # Fetch the subcategory details for the form
    try:
        with mysql.connector.connect(**db_config) as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM subcategories WHERE id = %s", (subcategory_id,))
            subcategory = cursor.fetchone()

        if not subcategory:
            flash("Subcategory not found.", "danger")
            return redirect('/manage_categories')

        return render_template("edit_subcategory.html", subcategory=subcategory)
    except mysql.connector.Error as err:
        flash(f"Error fetching subcategory: {err}", "danger")
        return redirect('/manage_categories')

# Route: Delete Subcategory
@app.route('/delete_subcategory/<int:subcategory_id>', methods=['POST'])
@login_required
def delete_subcategory(subcategory_id):
    try:
        with mysql.connector.connect(**db_config) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM subcategories WHERE id = %s", (subcategory_id,))
            conn.commit()

        flash("Subcategory deleted successfully!", "success")
    except mysql.connector.Error as err:
        flash(f"Error deleting subcategory: {err}", "danger")

    return redirect('/manage_categories')

# Route: Logout
@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash("You have been logged out successfully.")
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
