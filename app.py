from flask import Flask, jsonify, request, session, render_template, redirect, url_for, send_from_directory
from datetime import datetime, timedelta, timezone
import os
import bcrypt
from extensions import db, csrf, cors, limiter
from flask_migrate import Migrate
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from routes.auth import auth, login_required
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sololearn.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024  # 25MB max file size
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx', 'pptx', 'mp4', 'mov'} # Define allowed extensions
# TODO: Move API Key to environment variable for security
app.config['GOOGLE_CLOUD_API_KEY'] = 'AIzaSyBdLj-ThGSzotJDhMYCGNube5YQwCDScow'

# Helper function for checking file extensions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
cors.init_app(app, supports_credentials=True)
limiter.init_app(app)

# Ensure upload directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
print(f"\n*** Files will be stored in: {app.config['UPLOAD_FOLDER']} ***\n")

# Register blueprints before importing/using models in routes
from routes.auth import auth
from routes.files import files
from routes.paths import paths
from routes.tracking import tracking
from routes.resources import resources
from routes.external_search import external_search

app.register_blueprint(auth, url_prefix='/api/auth')
app.register_blueprint(files, url_prefix='/api/files')
app.register_blueprint(paths, url_prefix='/api/paths')
app.register_blueprint(tracking, url_prefix='/api/tracking')
app.register_blueprint(resources, url_prefix='/api/resources')
app.register_blueprint(external_search, url_prefix='/api/external-search')

# === Route for Statistics Page ===
@app.route('/stats')
@login_required
def stats_page():
    # This route just renders the HTML page.
    # The data for the charts will be fetched via separate API calls from the frontend JS.
    return render_template('statistics.html')
# === End Stats Page Route ===

# === API Endpoint for Daily Reading Time ===
@app.route('/api/stats/reading-time-daily')
@login_required
def stats_reading_time_daily():
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    user_id = session['user_id']
    
    try:
        # Get data for the last 30 days (adjust as needed)
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        
        # Query using func.date for grouping by date (works for SQLite, adjust for other DBs if needed)
        # For PostgreSQL: use func.date_trunc('day', ReadingLog.end_time)
        daily_stats = db.session.query(
            func.date(ReadingLog.end_time).label('date'),
            # Calculate sum in minutes (integer division or float division)
            (func.sum(ReadingLog.duration) / 60.0).label('total_duration_minutes') 
        ).filter(
            ReadingLog.user_id == user_id,
            ReadingLog.end_time >= thirty_days_ago, # Filter for recent data
            ReadingLog.duration > 0 # Only include logs with actual duration
        ).group_by(
            func.date(ReadingLog.end_time)
        ).order_by(
            func.date(ReadingLog.end_time)
        ).all()
        
        # Format data for Chart.js (labels = dates, data = durations)
        labels = [entry.date for entry in daily_stats]
        # Use the duration in minutes
        data = [entry.total_duration_minutes for entry in daily_stats]
        
        return jsonify({'labels': labels, 'data': data}), 200
        
    except Exception as e:
        app.logger.error(f"Error fetching daily stats: {e}")
        return jsonify({'error': 'Failed to retrieve daily statistics', 'details': str(e)}), 500
# === End Daily Stats API ===

# === API Endpoint for Time Per Resource ===
@app.route('/api/stats/reading-time-per-resource')
@login_required
def stats_reading_time_per_resource():
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    user_id = session['user_id']
    
    try:
        # Query to get total duration per file, join with File table for name
        # Limit to top 10 most time spent
        resource_stats = db.session.query(
            File.name.label('file_name'), # Assuming File model has 'name'
            # Calculate sum in minutes
            (func.sum(ReadingLog.duration) / 60.0).label('total_duration_minutes') 
        ).join(File, ReadingLog.file_id == File.id) \
        .filter(
            ReadingLog.user_id == user_id,
            ReadingLog.duration > 0 # Only include logs with actual duration
        ).group_by(
            File.id, File.name # Group by file ID and name
        ).order_by(
            # Order by duration (original sum in seconds still works for ordering)
            func.sum(ReadingLog.duration).desc() # Order by total duration descending
        ).limit(10).all() # Get top 10
        
        # Format data for Chart.js (labels = file names, data = durations)
        labels = [entry.file_name for entry in resource_stats]
        # Use the duration in minutes
        data = [entry.total_duration_minutes for entry in resource_stats]
        
        return jsonify({'labels': labels, 'data': data}), 200
        
    except Exception as e:
        app.logger.error(f"Error fetching resource stats: {e}")
        return jsonify({'error': 'Failed to retrieve resource statistics', 'details': str(e)}), 500
# === End Resource Stats API ===

# Initialize database and create admin user
with app.app_context():
    # Import models within the app context to ensure they are registered
    from models import *
    
    # Create tables if they don't exist (won't drop existing data)
    db.create_all()
    
    # Check if admin user exists, create if not
    admin = User.query.filter_by(email="admin@sololearn.com").first()
    if not admin:
        admin = User(
            email="admin@sololearn.com",
            name="Admin",
            is_active=True,
            is_admin=True,
            last_login=datetime.now(timezone.utc)
        )
        admin.set_password("securepassword123")
        db.session.add(admin)
        db.session.commit()
        print("\n*** Admin user created ***\n")
    
    # Print total user count
    try:
        user_count = User.query.count()
        print(f"\n*** Total Registered Users: {user_count} ***\n")
        
        # Print total files in system
        file_count = File.query.count()
        print(f"*** Total Files in System: {file_count} ***\n")
    except Exception as e:
        print(f"Error querying database: {e}")

# Helper for formatting duration in Jinja template
def format_duration_filter(seconds):
    if seconds is None or seconds < 0:
        return '0s'
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0 or hours > 0: # Show minutes if hours exist
        parts.append(f"{minutes}m")
    parts.append(f"{secs}s")
    return ' '.join(parts)

app.jinja_env.filters['format_duration'] = format_duration_filter

@app.route('/')
def root():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login')
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/register')
def register_page():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/files')
def files_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('files.html')

@app.route('/resources')
def resources_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('resources.html')

@app.route('/courses')
def courses_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('courses.html')

@app.route('/practice')
def practice_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('practice.html')

@app.route('/external-content')
@login_required
def external_content():
    return render_template('external_content.html')

@app.route('/test-search')
@login_required
def test_search():
    return render_template('test_search.html')

@app.route('/reading-list')
def reading_list_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('reading_list.html')

@app.route('/files/view/<int:file_id>')
def view_file_page(file_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    file = File.query.filter_by(id=file_id, user_id=user_id).first_or_404()
    
    # Calculate total duration from ReadingLog entries for this file/user
    total_duration = db.session.query(func.sum(ReadingLog.duration))\
        .filter_by(file_id=file.id, user_id=user_id)\
        .scalar() or 0
    
    print(f"Calculated total duration for file {file_id}: {total_duration} seconds")
    
    # Get all reading logs for this file to debug
    logs = ReadingLog.query.filter_by(file_id=file.id, user_id=user_id).all()
    log_details = [{
        'id': log.id,
        'duration': log.duration,
        'start': log.start_time.isoformat() if log.start_time else None,
        'end': log.end_time.isoformat() if log.end_time else None
    } for log in logs]
    
    print(f"Reading logs for file {file_id}: {log_details}")
    
    return render_template('file_view.html', 
                         file=file, 
                         total_duration_seconds=total_duration,
                         estimated_duration=file.estimated_duration)

# New route to securely serve uploaded files
@app.route('/files/serve/<int:file_id>')
def serve_file(file_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    user_id = session['user_id']
    file = File.query.filter_by(id=file_id, user_id=user_id).first_or_404()

    if not file.path:
        return jsonify({'error': 'File path not found'}), 404

    # Convert relative path to absolute path
    absolute_path = os.path.join(os.getcwd(), file.path)
    
    if not os.path.exists(absolute_path):
        return jsonify({'error': 'File not found on server'}), 404

    # Extract directory and filename from the absolute path
    directory = os.path.dirname(absolute_path)
    filename = os.path.basename(absolute_path)
    
    # Use send_from_directory for security
    # Set as_attachment=False to display inline (important for PDF embed)
    return send_from_directory(directory, filename, 
                             as_attachment=False, 
                             download_name=file.name) # Provides original filename if user saves

@app.route('/files/preview/<int:file_id>')
@login_required
def preview_file(file_id):
    try:
        # Get the file from database
        file = File.query.filter_by(id=file_id, user_id=session['user_id']).first_or_404()
        
        # Return the extracted text content for preview
        if file.extracted_text:
            return jsonify({
                'content': file.extracted_text,
                'name': file.name,
                'type': file.filetype
            })
        else:
            return jsonify({'error': 'No preview available for this file'}), 404
            
    except Exception as e:
        app.logger.error(f"Error previewing file {file_id}: {e}")
        return jsonify({'error': 'File preview failed'}), 500

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now(timezone.utc).isoformat()})

if __name__ == '__main__':
    app.run(debug=True, port=8000) 