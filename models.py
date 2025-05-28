from extensions import db
from datetime import datetime, timedelta, timezone
import secrets
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    reset_token = db.Column(db.String(100))
    reset_token_expires = db.Column(db.DateTime)
    files = db.relationship('File', backref='user', lazy=True)
    reading_logs = db.relationship('ReadingLog', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_reset_token(self):
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expires = datetime.now(timezone.utc) + timedelta(hours=1)
        return self.reset_token

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_token = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime, nullable=False)
    last_activity = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    ip_address = db.Column(db.String(45))  # IPv6 compatible
    user_agent = db.Column(db.String(200))

    def is_valid(self):
        return datetime.now(timezone.utc) < self.expires_at

    @classmethod
    def create_session(cls, user_id, ip_address=None, user_agent=None):
        session = cls(
            user_id=user_id,
            session_token=secrets.token_urlsafe(32),
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(session)
        return session

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    filetype = db.Column(db.String(10))  # "pdf", "youtube", etc.
    path = db.Column(db.String(500))  # Local path or URL
    file_hash = db.Column(db.String(64), index=True, nullable=True)
    extracted_text = db.Column(db.Text)  # For search/future AI
    tags = db.Column(db.JSON)  # ["python", "machine-learning"]
    upload_date = db.Column(db.DateTime, default=datetime.now)
    word_count = db.Column(db.Integer, default=0)  # Store word count
    estimated_duration = db.Column(db.Integer, default=3600)  # Default 1 hour in seconds
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    reading_logs = db.relationship('ReadingLog', backref='file', lazy=True)

    __table_args__ = (db.UniqueConstraint('user_id', 'file_hash', name='uq_user_file_hash'),)

class ReadingLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    duration = db.Column(db.Integer)  # Seconds
    created_at = db.Column(db.DateTime, default=datetime.now)

class LearningPath(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.now)
    resources = db.relationship('PathResource', backref='learning_path', lazy=True, order_by='PathResource.sequence')

class PathResource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path_id = db.Column(db.Integer, db.ForeignKey('learning_path.id'), nullable=False)
    sequence = db.Column(db.Integer) # Simple 1-based sequence (renamed from 'order')
    duration_seconds = db.Column(db.Integer, nullable=True) # Store duration here
    is_upload = db.Column(db.Boolean, default=False, nullable=False) # Flag to indicate if it's an upload
    
    # Foreign key to EITHER File OR LearningPathUpload
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'), nullable=True) 
    learning_path_upload_id = db.Column(db.Integer, db.ForeignKey('learning_path_upload.id'), nullable=True)

    # Add a check constraint to ensure only one of file_id or learning_path_upload_id is set?
    # This depends on DB support and complexity needed.
    # __table_args__ = ( db.CheckConstraint('(file_id IS NULL AND learning_path_upload_id IS NOT NULL) OR (file_id IS NOT NULL AND learning_path_upload_id IS NULL)'), {} )

    completed = db.Column(db.Boolean, default=False) # Moved from old definition
    completed_at = db.Column(db.DateTime) # Moved from old definition
    
    # learning_path = db.relationship('LearningPath', backref=db.backref('path_resources', lazy=True, order_by='PathResource.sequence')) # REMOVED: Redundant due to backref in LearningPath.resources
    file = db.relationship('File') # Relationship to selected file
    # Explicitly specify the foreign key for the relationship
    learning_path_upload = db.relationship(
        'LearningPathUpload', 
        foreign_keys=[learning_path_upload_id], # Specify the FK column
        backref=db.backref('path_resource', uselist=False, lazy=True)
    )

# New model for uploads specifically for learning paths
class LearningPathUpload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.String(255), nullable=False) # Name of the file as uploaded by user
    stored_filename = db.Column(db.String(255), nullable=False, unique=True) # Secure name on the server
    file_path = db.Column(db.String(500), nullable=False) # Path on server relative to upload folder
    file_type = db.Column(db.String(50)) # MIME type
    file_size = db.Column(db.Integer) # Size in bytes
    upload_date = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # User who uploaded
    path_resource_id = db.Column(db.Integer, db.ForeignKey('path_resource.id'), nullable=True) # Link to the specific resource entry

    # Add relationship back to User if needed
    # user = db.relationship('User', backref=db.backref('learning_path_uploads', lazy=True))
    # path_resource = db.relationship('PathResource', backref=db.backref('upload', uselist=False, lazy=True)) 