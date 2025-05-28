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