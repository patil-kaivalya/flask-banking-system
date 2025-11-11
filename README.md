
# 🏦 MyBank – Flask Banking Web App

A secure and user-friendly **banking web application** built with **Flask**, featuring user authentication, dashboard with masked personal information, password reset via tokenized links, and SQLite database integration.

---

## 🚀 Features

- 🔐 **User Authentication** – Signup, Login, and Logout system  
- 🧾 **Dashboard** – Displays masked phone, email, and random account balance  
- 💳 **Transaction Page** – Sample transaction history (credit/debit records)  
- 💸 **Fund Transfer Page** – Demo page for transfer functionality  
- 🔁 **Forgot & Reset Password** – Secure password reset via time-limited tokens  
- ⚙️ **Session Management** – Manages user sessions and prevents cache access after logout  
- 🧱 **SQLite Database** – Lightweight database to store user data securely  

---

## 🧰 Tech Stack

| Category | Technology |
|-----------|-------------|
| **Frontend** | HTML, CSS, Bootstrap |
| **Backend** | Flask (Python) |
| **Database** | SQLite3 |
| **Security** | bcrypt, itsdangerous, markupsafe |
| **Server** | Localhost (Flask built-in) |

---

## 📸 Screenshots
Page	Screenshot
🏠 Login Page	

🧾 Dashboard	

👤 Profile Page	

📝 Signup Page	

🔁 Forgot Password	

🔐 Reset Password	

💸 Fund Transfer Page	

💳 Transactions Page	

> 📂 screenshots inside the `/screenshots` folder.

---

## ⚙️ Setup Instructions

Follow these simple steps to run the project locally 👇  

### 1️⃣ Clone the repository
```bash
git clone https://github.com/patil-kaivalya/flask-banking-system
cd mybank-flask-app

### 2️⃣ Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate   # For Windows
# OR
source venv/bin/activate

### 3️⃣ Install dependencies
pip install -r requirements.txt

### 4️⃣ Run the Flask application
python app.py

### 5️⃣ Open in browser
http://127.0.0.1:500


**🧾 Project Structure**
mybank-flask-app/
│
├── app.py
├── bank.db
├── requirements.txt
├── templates/
│   ├── login.html
│   ├── signup.html
│   ├── dashboard.html
│   ├── profile.html
│   ├── transactions.html
│   ├── transfer.html
│   ├── forgot_password.html
│   └── reset_password.html
│
├── static/
│   ├── css/
│   └── images/
│
├── screenshots/
│   ├── login.png
│   ├── dashboard.png
│   ├── profile.png
│   ├── forgot_password.png
│   ├── reset_password.png
│   ├── fund_transfer.png
│   ├── transactions.png
│   └── singup.png
│
└── README.md

📦 Example Requirements
Flask==3.0.3
bcrypt==4.1.2
itsdangerous==2.2.0
MarkupSafe==3.0.2


requirements.txt in my project root.
```
✨ Author

👤 Kaivalya Patil
🎓 B.Tech in Artificial Intelligence & Machine Learning
📍 Sanjay Ghodawat University, Kolhapur
💼 Python Developer | Django | Flask | Data Science Enthusiast

📜 License

This project is open-source and available under the MIT License.


🌟 Show Your Support

If you like this project, consider giving it a ⭐ on GitHub!
Your support motivates continued development and improvements.
