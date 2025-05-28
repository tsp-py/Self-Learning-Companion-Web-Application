from flask import Blueprint, jsonify, request, session
from extensions import db, limiter
from models import File
from sqlalchemy import or_

resources = Blueprint('resources', __name__)

@resources.route('/search', methods=['GET'])
@limiter.limit("30/minute")
def search_resources():
    """
    Search resources based on query parameters
    query params:
        q: search query (optional)
        type: resource type filter (optional)
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    user_id = session['user_id']
    search_query = request.args.get('q', '')
    resource_type = request.args.get('type', 'all')

    # Build the search query
    query = File.query.filter_by(user_id=user_id)
    
    # Apply resource type filter if specified
    if resource_type and resource_type != 'all':
        query = query.filter_by(filetype=resource_type)
    
    # Apply search if specified
    if search_query:
        # Search in name, extracted text and tags
        search_filter = or_(
            File.name.ilike(f'%{search_query}%'),
            File.extracted_text.ilike(f'%{search_query}%')
        )
        query = query.filter(search_filter)
    
    # Execute query and format results
    files = query.order_by(File.upload_date.desc()).all()
    
    results = []
    for file in files:
        # Convert tags from JSON if available
        tags = file.tags if file.tags else []
        
        results.append({
            'id': file.id,
            'title': file.name,
            'description': file.extracted_text[:150] + '...' if file.extracted_text and len(file.extracted_text) > 150 else (file.extracted_text or 'No description available'),
            'type': file.filetype or 'document',
            'tags': tags,
            'upload_date': file.upload_date.isoformat() if file.upload_date else None,
            'word_count': file.word_count,
            'estimated_duration': file.estimated_duration
        })
    
    return jsonify(results)

@resources.route('/types', methods=['GET'])
def get_resource_types():
    """Get all available resource types in the system"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    
    # Get distinct file types from the database
    file_types = db.session.query(File.filetype).filter(
        File.user_id == user_id,
        File.filetype.isnot(None)
    ).distinct().all()
    
    # Extract types from result tuples and filter out None values
    types_list = [t[0] for t in file_types if t[0]]
    
    return jsonify(types_list) 