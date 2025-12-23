# 💰 Expense Management Application (Flask)

A **Flask-based expense management web application** that allows users to **register, log in, manage expenses, categories, and subcategories**, and view filtered expense records stored in a **MySQL database**.

This project demonstrates **full-stack web development using Flask**, authentication, database integration, CRUD operations, and server-side rendering with templates.

---

## 📌 Project Overview

Managing personal expenses efficiently requires structured tracking and categorization.
This application provides a secure platform where users can:

* Register and log in
* Add, edit, and delete expenses
* Categorize expenses and payment methods
* Filter expenses by date, category, amount, and payment method
* Manage categories and subcategories dynamically

The project follows Flask’s **MVC-style architecture** and uses **MySQL** for persistent storage.

---

## ✨ Features

* 🔐 User authentication (register, login, logout)
* ➕ Add expenses with category & payment method
* ✏️ Edit and delete expenses
* 📂 Category & subcategory management
* 🔍 Advanced expense filtering:

  * Date range
  * Category
  * Payment method
  * Amount range
* 🗄️ MySQL database integration
* 🧾 Secure password hashing
* 🎨 HTML templates with base layout
* ⚡ Flash messages for user feedback

---

## 🧩 Application Pages

* **Home Page** (`home.html`)
* **Register** (`register.html`)
* **Login / Logout** (`login.html`, `logout.html`)
* **Add Expense** (`add_expense.html`)
* **View Expenses** (`view_expenses.html`)
* **Edit Expense** (`edit_expense.html`)
* **Delete Expense** (`delete_expense.html`)
* **Manage Categories & Subcategories** (`manage_categories.html`)
* **Add/Edit Category** (`add_category.html`, `edit_category.html`)
* **Add/Edit Subcategory** (`add_subcategory.html`, `edit_subcategory.html`)

---

## 📂 Project Structure

```
expense_app/
│
├── app.py                    # Main Flask application
├── expense_app.db            # Database (MySQL schema used)
│
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── login.html
│   ├── logout.html
│   ├── register.html
│   ├── add_expense.html
│   ├── edit_expense.html
│   ├── delete_expense.html
│   ├── view_expenses.html
│   ├── manage_categories.html
│   ├── add_category.html
│   ├── edit_category.html
│   ├── add_subcategory.html
│   ├── edit_subcategory.html
│
├── README.md
```

---

## ⚙️ Technologies Used

* **Python**
* **Flask**
* **MySQL**
* **HTML / Jinja2 Templates**
* **Werkzeug Security**
* **Session-based Authentication**

---

## 🧠 Architecture Overview

* **Routes & Logic** → `app.py`
* **Templates (UI)** → HTML files
* **Database Layer** → MySQL (`users`, `expenses`, `categories`, `subcategories`)
* **Authentication** → Flask sessions + password hashing

---

## 🚀 Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/snxhx294/expense_app.git
cd expense_app
```

### 2️⃣ Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```bash
pip install flask mysql-connector-python werkzeug
```

---

## 🗄️ Database Setup (MySQL)

1. Create a MySQL database:

```sql
CREATE DATABASE expense_app;
```

2. Create required tables:

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE subcategories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    category_id INT,
    subcategory_id INT,
    amount DECIMAL(10,2),
    date DATE,
    description TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

3. Update database credentials in `app.py`:

```python
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'YOUR_PASSWORD',
    'database': 'expense_app'
}
```

---

## ▶️ Run the Application

```bash
python app.py
```

Visit:

```
http://127.0.0.1:5000/
```

---

## 🔐 Security Notes

* Passwords are hashed using `werkzeug.security`
* Protected routes require authentication
* Session-based login enforcement
* Flash messages used for error handling

⚠️ **Important:**
Move `secret_key` and DB credentials to environment variables in production.

---

## 🌱 Future Enhancements

* Monthly/annual expense reports
* Data visualization (charts)
* Export to CSV/PDF
* Role-based access (admin/user)
* REST API using Flask-RESTful
* Deployment (Render / Railway / AWS)
