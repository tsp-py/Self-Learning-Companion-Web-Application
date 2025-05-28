from flask import Blueprint, request, jsonify, session
from extensions import db
from models import LearningPath, PathResource, File
from datetime import datetime

paths = Blueprint('paths', __name__)

@paths.route('/paths', methods=['POST'])
def create_path():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    resources = data.get('resources', [])  # List of file IDs in order
    
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    
    if not resources:
        return jsonify({'error': 'At least one resource is required'}), 400
    
    # Verify all files exist and belong to user
    for file_id in resources:
        file = File.query.filter_by(id=file_id, user_id=session['user_id']).first()
        if not file:
            return jsonify({'error': f'File {file_id} not found or access denied'}), 404
    
    path = LearningPath(
        title=title,
        description=description,
        user_id=session['user_id']
    )
    db.session.add(path)
    db.session.flush()  # Get path ID before committing
    
    # Create path resources with order
    for index, file_id in enumerate(resources):
        resource = PathResource(
            path_id=path.id,
            file_id=file_id,
            order=index,
            user_id=session['user_id']
        )
        db.session.add(resource)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Learning path created successfully',
        'path': {
            'id': path.id,
            'title': path.title,
            'description': path.description
        }
    })

@paths.route('/paths', methods=['GET'])
def get_paths():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    paths = LearningPath.query.filter_by(user_id=session['user_id']).all()
    return jsonify({
        'paths': [{
            'id': path.id,
            'title': path.title,
            'description': path.description,
            'created_at': path.created_at.isoformat(),
            'resources': [{
                'id': resource.id,
                'file_id': resource.file_id,
                'order': resource.order,
                'completed': resource.completed,
                'completed_at': resource.completed_at.isoformat() if resource.completed_at else None
            } for resource in path.resources]
        } for path in paths]
    })

@paths.route('/paths/<int:path_id>', methods=['GET'])
def get_path(path_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    path = LearningPath.query.filter_by(id=path_id, user_id=session['user_id']).first()
    if not path:
        return jsonify({'error': 'Path not found'}), 404
    
    return jsonify({
        'path': {
            'id': path.id,
            'title': path.title,
            'description': path.description,
            'created_at': path.created_at.isoformat(),
            'resources': [{
                'id': resource.id,
                'file_id': resource.file_id,
                'file_name': File.query.get(resource.file_id).name,
                'order': resource.order,
                'completed': resource.completed,
                'completed_at': resource.completed_at.isoformat() if resource.completed_at else None
            } for resource in path.resources]
        }
    })

@paths.route('/paths/<int:path_id>/resources/<int:resource_id>/complete', methods=['POST'])
def complete_resource(path_id, resource_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    resource = PathResource.query.filter_by(
        id=resource_id,
        path_id=path_id,
        user_id=session['user_id']
    ).first()
    
    if not resource:
        return jsonify({'error': 'Resource not found'}), 404
    
    resource.completed = True
    resource.completed_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'Resource marked as completed',
        'resource': {
            'id': resource.id,
            'completed_at': resource.completed_at.isoformat()
        }
    }) 