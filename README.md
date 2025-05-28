# SoloLearn – Personal Learning Management System

A single-user learning management system to upload files, track study time, and visualize learning progress with real-time analytics.

---

## Features

- Secure single-user authentication  
- Upload and manage PDFs, DOCX, Videos  
- Track time spent on each learning resource  
- Create and follow custom learning paths  
- Real-time interactive progress graphs  
- Built-in web scraper to fetch external study materials  

---

## Tech Stack

| Layer        | Technology                  |
|--------------|-----------------------------|
| Backend      | Python, Flask               |
| Frontend     | HTML, CSS, JavaScript       |
| Database     | SQLite3                    |
| Data Visualization | Chart.js              |
| Web Scraping | BeautifulSoup, Requests     |
| Auth & Logic | Flask Sessions, SQL/CSV/JSON|

---

## Getting Started

### Prerequisites

- Python 3.8+  
- Node.js 16+  
- SQLite3  

### Setup Instructions

1. Clone the repo:
   ```
   git clone https://github.com/tsp-py/self-learning-companion-Web-Application.git
   cd self-learning-companion-Web-Application
2. Create and activate a Python virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
3. Install dependencies:
   ```
   pip install -r requirements.txt
4. Initialize the database:
   ```
   flask db init
   flask db migrate
   flask db upgrade
5. Run the Flask development server:
   ```
   python app.py
6. Open your browser at http://localhost:5000

## 📡 API Endpoints

### 🔐 Authentication
- `POST /api/auth/login` – User login  
- `POST /api/auth/logout` – Logout  
- `GET /api/auth/me` – Get current user info  

### 📁 File Management
- `POST /api/files/upload` – Upload a file  
- `GET /api/files` – List all files  
- `GET /api/files/:id` – File details  

### 🧭 Learning Paths
- `POST /api/paths` – Create a learning path  
- `GET /api/paths` – List all paths  
- `GET /api/paths/:id` – Path details  
- `POST /api/paths/:id/resources/:rid/complete` – Mark resource as complete  

### ⏱️ Time Tracking
- `POST /api/tracking/start` – Start session  
- `POST /api/tracking/end` – End session  
- `GET /api/tracking/stats` – Get usage stats  

## 📸 Screenshots

🖼️Screenshots of file manager, usage graphs, and smart search.

Register Page Display

<img width="496" alt="image" src="https://github.com/user-attachments/assets/68c7e749-aea4-424c-ad18-9de2ea0a6a3a" />

Login Page Display

<img width="496" alt="image" src="https://github.com/user-attachments/assets/3cb93362-e117-483f-9121-74d964fd189f" />

User Interface

<img width="499" alt="image" src="https://github.com/user-attachments/assets/90f18cde-a047-4c0d-aace-9ab75057f089" />

File Management Dashboard

<img width="496" alt="image" src="https://github.com/user-attachments/assets/31d57d43-11a7-46e3-a0cf-bae9e01d72f0" />

File View Dashboard

<img width="500" alt="image" src="https://github.com/user-attachments/assets/69cc312d-be13-4f36-8e48-d94054d0fbaa" />

Graphical Visuvalization 

<img width="496" alt="image" src="https://github.com/user-attachments/assets/1d4237df-3515-492b-b33b-cfc2bf03a2d9" />

External Resources(Searches)

<img width="496" alt="image" src="https://github.com/user-attachments/assets/5168a696-07da-4db7-a7fd-e39542f05d4e" />

---

## 🛠️ Getting Started

```bash
git clone https://github.com/tsp-py/self-learning-companion-Web-Application.git
cd self-learning-companion-Web-Applicationb
pip install -r requirements.txt
python app.py

http://localhost:5000

