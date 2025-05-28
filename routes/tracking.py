from flask import Blueprint, request, jsonify, session
from extensions import db
from models import ReadingLog, File
from datetime import datetime, timedelta, timezone
from sqlalchemy import func
import traceback

tracking = Blueprint('tracking', __name__)

@tracking.route('/start', methods=['POST'])
def start_reading_log():
    print(f"=== START TRACKING API CALLED ===")
    if 'user_id' not in session:
        print(f"Error: User not authenticated")
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    print(f"User ID from session: {user_id}")
    
    data = request.get_json()
    file_id = data.get('file_id')
    print(f"Request data: {data}")
    
    if not file_id:
        print(f"Error: Missing file_id in request")
        return jsonify({'error': 'File ID is required'}), 400
    
    # Verify file exists and belongs to user
    file = File.query.filter_by(id=file_id, user_id=user_id).first()
    if not file:
        print(f"Error: File {file_id} not found or doesn't belong to user {user_id}")
        return jsonify({'error': 'File not found or access denied'}), 404
    
    print(f"Found file: {file.id} - {file.name}")
    
    # Create new reading log entry with duration 0 initially
    log = ReadingLog(
        file_id=file_id,
        user_id=user_id,
        start_time=datetime.now(timezone.utc),
        duration=0
    )
    
    try:
        db.session.add(log)
        db.session.commit()
        print(f"Created new reading log: {log.id}")
        
        # Calculate total duration for this file
        total_duration = db.session.query(func.sum(ReadingLog.duration))\
            .filter(ReadingLog.file_id == file_id, ReadingLog.user_id == user_id)\
            .scalar() or 0
        
        print(f"Total duration for file {file_id}: {total_duration} seconds")
            
        return jsonify({
            'message': 'Reading log created',
            'log_id': log.id,
            'total_duration': total_duration
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating reading log: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to create reading log entry'}), 500

@tracking.route('/update', methods=['POST'])
def update_reading_log():
    print(f"=== UPDATE TRACKING API CALLED ===")
    if 'user_id' not in session:
        print(f"Error: User not authenticated")
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    print(f"User ID from session: {user_id}")
    
    data = request.get_json()
    print(f"Request data: {data}")
    
    log_id = data.get('log_id')
    session_duration = data.get('session_duration')
    
    if not log_id or session_duration is None:
        print(f"Error: Missing required parameters")
        return jsonify({'error': 'Log ID and session duration are required'}), 400
    
    try:
        # Ensure duration is a non-negative integer
        session_duration = max(0, int(session_duration))
        print(f"Parsed session duration: {session_duration}")
    except (ValueError, TypeError) as e:
        print(f"Error parsing duration: {e}")
        return jsonify({'error': 'Invalid duration format'}), 400

    # Find the specific log entry for this user
    log = ReadingLog.query.filter_by(
        id=log_id,
        user_id=user_id
    ).first()
    
    if not log:
        print(f"Error: Reading log {log_id} not found for user {user_id}")
        return jsonify({'error': 'Reading log session not found'}), 404
    
    print(f"Found reading log {log_id} for file {log.file_id}")
    print(f"Current duration: {log.duration}, updating to: {session_duration}")
    
    # Update the duration and end time
    try:
        # Make sure the duration value is valid (not None)
        old_duration = log.duration if log.duration is not None else 0 # Keep for logging
        new_session_duration = max(0, int(session_duration)) # Ensure non-negative int
        
        # Overwrite the duration for this specific log entry with the total received from frontend
        log.duration = new_session_duration 
        log.end_time = datetime.now(timezone.utc)
        
        print(f"Updated log duration from {old_duration} to {log.duration} (received {new_session_duration})") # Updated log message
        
        db.session.commit()
        print(f"Updated reading log {log_id} with new total duration {log.duration}") # Updated log message
        
        # Calculate new total duration for this file - sum all logs for this file
        total_duration = db.session.query(func.sum(ReadingLog.duration))\
            .filter(ReadingLog.file_id == log.file_id, ReadingLog.user_id == user_id)\
            .scalar() or 0

        print(f"New total duration for file {log.file_id}: {total_duration} seconds")
        
        # Return detailed information for debugging
        all_logs = ReadingLog.query.filter_by(
            file_id=log.file_id, 
            user_id=user_id
        ).all()
        
        log_details = [{
            'id': l.id,
            'duration': l.duration,
            'start': l.start_time.isoformat() if l.start_time else None,
            'end': l.end_time.isoformat() if l.end_time else None
        } for l in all_logs]
        
        print(f"All logs for file {log.file_id}: {log_details}")

        return jsonify({
            'message': 'Reading log updated',
            'log_id': log.id,
            'session_duration': session_duration,
            'total_file_duration': total_duration,
            'all_logs': log_details
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error updating reading log {log_id}: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Failed to update reading log: {str(e)}'}), 500

@tracking.route('/reset', methods=['POST'])
def reset_reading_time():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    data = request.get_json()
    file_id = data.get('file_id')
    
    if not file_id:
        return jsonify({'error': 'File ID is required'}), 400
    
    try:
        # Verify file exists and belongs to user
        file = File.query.filter_by(id=file_id, user_id=user_id).first()
        if not file:
            return jsonify({'error': 'File not found or access denied'}), 404
        
        # Delete all reading logs for this file
        ReadingLog.query.filter_by(file_id=file_id, user_id=user_id).delete()
        db.session.commit()
        
        return jsonify({
            'message': 'Reading time reset successfully',
            'file_id': file_id
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error resetting reading time: {e}")
        return jsonify({'error': 'Failed to reset reading time'}), 500

@tracking.route('/stats', methods=['GET'])
def get_stats():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Get last time spent
    total_time = db.session.query(func.sum(ReadingLog.duration))\
        .filter(ReadingLog.user_id == session['user_id'])\
        .scalar() or 0
    
    # Get time per file type
    time_by_type = db.session.query(
        File.filetype,
        func.sum(ReadingLog.duration).label('total_seconds')
    ).join(ReadingLog)\
    .filter(ReadingLog.user_id == session['user_id'])\
    .group_by(File.filetype)\
    .all()
    
    # Get time per file
    time_by_file = db.session.query(
        File.id,
        File.name,
        func.sum(ReadingLog.duration).label('total_seconds')
    ).join(ReadingLog)\
    .filter(ReadingLog.user_id == session['user_id'])\
    .group_by(File.id)\
    .all()
    
    # Get daily activity for the last 30 days
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    daily_activity = db.session.query(
        func.date(ReadingLog.start_time).label('date'),
        func.sum(ReadingLog.duration).label('total_seconds')
    ).filter(
        ReadingLog.user_id == session['user_id'],
        ReadingLog.start_time >= thirty_days_ago
    ).group_by(func.date(ReadingLog.start_time))\
    .all()
    
    return jsonify({
        'total_time': total_time,
        'by_type': [{
            'type': type_,
            'seconds': seconds or 0
        } for type_, seconds in time_by_type],
        'by_file': [{
            'id': id_,
            'name': name,
            'seconds': seconds or 0
        } for id_, name, seconds in time_by_file],
        'daily_activity': [{
            'date': date.isoformat(),
            'seconds': seconds or 0
        } for date, seconds in daily_activity]
    }) 