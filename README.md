# Vehicle Parking Management Application
## vehicle-parking-app-v1
It is a multi-user app  that manages different parking lots, parking spots and parked vehicles.

Project was created as a part of course Modern Application developement I .

## Technologies and Libraries Used

| Technology or Library | Purpose |
|------------------------|---------|
| **Flask** | Lightweight micro web framework used to build the backend of application |
| **Flask-SQLAlchemy** | ORM used to define and interact with SQLite database using Python |
| **jinja2** | Flask’s default templating engine used to generate dynamic HTML from backend |
| **SQLite** | Lightweight relational database used to store user, parking lot, parking spot, and reservation data |
| **Bootstrap5** | Front-end CSS framework used for responsive design and prebuilt UI components |
| **HTML5 and CSS3** | Markup and styling for the application interface and layout |
| **ChartJs** | External JS library used to create summary charts |
| **Flask `flash()`** | Used to provide feedback messages to user and admin (e.g., success or failure) |
| **Flask `session`** | Used to manage authentication |


## 🚀 How to Run This App on Your System

Follow these steps to get the application running on your local machine:

### ✅ Step 1: Clone the Repository

```bash
git clone https://github.com/23f3003205/vehicle-parking-app.git
cd vehicle-parking-app
```


---

### 📦 Step 2: Create and Activate Virtual Environment (Recommended)

```bash
# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

---

### 📚 Step 3: Install All Dependencies

```bash
pip install -r requirements.txt
```

---

### 🏃 Step 4: Run the Application

```bash
python app.py
```

The server should start, and you can access the app in your browser at:

```
http://127.0.0.1:5000/
```

---



## File structure
```
VEHICLE-PARKING-APP/
│
├── .env # Environment variables
├── app.py # Entry point of the application
├── api.yaml # API documentation or schema file
├── requirements.txt # Required Python packages
├── README.md # Project documentation
│
├── instance/
│ └── vehicle_parking.sqlite3 # SQLite3 database
│
├── application/ # Core Flask application logic
│ ├── controllers.py # Handles routing and view logic
│ ├── database.py # Database setup and connection
│ ├── models.py # SQLAlchemy models
│ └── resources.py # API resource definitions
│
├── static/ # CSS files and other static content
│ ├── admin.css
│ ├── base.css
│ ├── login.css
│ └── registered_user_admin.css
│
├── templates/ # HTML templates
│ ├── admin/
│ │ ├── add_parking_lot.html
│ │ ├── admin_dashboard.html
│ │ ├── admin_search_page.html
│ │ ├── edit_parking_lot.html
│ │ ├── occupied_spot_detail.html
│ │ ├── register_user_detail.html
│ │ ├── summary_chart.html
│ │ └── view_del_spot.html
│ │
│ ├── auth/
│ │ ├── login.html
│ │ └── register.html
│ │
│ ├── base_layout/
│ │ ├── base_admin.html
│ │ └── base_user.html
│ │
│ └── user/
│ ├── book_parking_spot.html
│ ├── release_parking_spot.html
│ ├── user_dashboard.html
│ └── user_summary.html
```


## ✍️ Author

Harshit Singh Patel  
Feel free to contribute or raise an issue!

---

