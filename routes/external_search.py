from flask import Blueprint, jsonify, request, current_app, session
import requests
from extensions import limiter

external_search = Blueprint('external_search', __name__)

GOOGLE_SEARCH_URL = "https://www.googleapis.com/customsearch/v1"

@external_search.route('', methods=['GET'])
@limiter.limit("15/minute") # Limit external API calls
def search_google():
    """
    Performs a search using the Google Custom Search JSON API.
    Requires 'q' (query) and 'cx' (search engine ID) query parameters.
    Uses GOOGLE_CLOUD_API_KEY from app config.
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
        
    query = request.args.get('q')
    search_engine_id = request.args.get('cx')
    api_key = current_app.config.get('GOOGLE_CLOUD_API_KEY')

    if not query:
        return jsonify({'error': 'Search query parameter (q) is required'}), 400
    if not search_engine_id:
        return jsonify({'error': 'Search engine ID parameter (cx) is required'}), 400
    if not api_key:
        current_app.logger.error("GOOGLE_CLOUD_API_KEY is not configured.")
        return jsonify({'error': 'Server configuration error: API key missing'}), 500

    params = {
        'key': api_key,
        'cx': search_engine_id,
        'q': query,
        'num': 9 # Request 9 results (fits well in a 3-column grid)
    }

    try:
        response = requests.get(GOOGLE_SEARCH_URL, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        
        search_results = response.json()
        
        # Log the search query and engine ID for debugging/monitoring
        current_app.logger.info(f"Google Search performed: query='{query}', cx='{search_engine_id}'")
        
        # We can directly return the google response structure 
        # as the frontend is designed to handle it (specifically the 'items' array)
        return jsonify(search_results)

    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Google Custom Search API request failed: {e}")
        return jsonify({'error': 'Failed to connect to external search service'}), 503 # Service Unavailable
    except Exception as e:
        current_app.logger.error(f"An unexpected error occurred during Google search: {e}")
        return jsonify({'error': 'An internal server error occurred'}), 500 