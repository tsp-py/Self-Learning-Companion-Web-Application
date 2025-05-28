
# SoloLearn - Personal Learning Management System

A single-user learning management system with time tracking and analytics capabilities.

## Features

- Secure authentication (single user)
- Multi-format file ingestion (PDFs, Docs, Videos)
- Time tracking and analytics
- Custom learning paths
- Real-time visual analytics

## Prerequisites

- Python 3.8+
- Node.js 16+
- SQLite3

## Backend Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

4. Run the development server:
```bash
python app.py
```

The server will start at http://localhost:5000

## Default Credentials

- Email: admin@sololearn.com
- Password: securepassword123

## API Endpoints

### Authentication
- POST /api/auth/login - Login with email/password
- POST /api/auth/logout - End session
- GET /api/auth/me - Get current user

### Files
- POST /api/files/upload - Upload new file
- GET /api/files - List all files
- GET /api/files/:id - Get file details

### Learning Paths
- POST /api/paths - Create new path
- GET /api/paths - List all paths
- GET /api/paths/:id - Get path details
- POST /api/paths/:id/resources/:rid/complete - Mark resource as complete

### Time Tracking
- POST /api/tracking/start - Start reading session
- POST /api/tracking/end - End reading session
- GET /api/tracking/stats - Get usage statistics

## Security Notes

- Change the default password after first login
- Set a secure SECRET_KEY in production
- Enable HTTPS in production
- Configure proper CORS settings for production

## License

MIT License 

# Self-Learning-Companion-Web-Application
Built a Flask-based platform for solo learners to upload files, track study time, and visualize learning via graphs. Added a smart search tool to fetch external study materials (PDF, DOCX, etc.) directly within the app, making self-study more organized and efficient.

**A smart digital workspace for solo learners**  
Track what you read, how long you read, and explore new content — all from one powerful dashboard.

---

## 🚀 Features

✅ **Personal File Uploads** – Upload and manage your own learning materials.  
⏱️ **Time Tracking** – Know exactly how much time you spend on each file.  
📊 **Visual Learning Reports** – Interactive graphs to monitor your progress.  
🌐 **Built-in Content Scraper** – Search and fetch PDFs/DOCX from the web without leaving the platform.  
📁 **No Instructor Needed** – Designed for full autonomy and simplicity.

---

## 🧰 Tech Stack

| Layer        | Tech Used                      |
|--------------|--------------------------------|
| Backend      | Python, Flask                  |
| Frontend     | HTML, CSS, JavaScript          |
| Data Viz     | Chart.js                       |
| Scraping     | BeautifulSoup, Requests        |
| Auth & Logic | Flask Sessions, SQL/CSV/JSON   |

---

## 📸 Sneak Peek

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

