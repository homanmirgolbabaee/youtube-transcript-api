from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
import re
import os

app = Flask(__name__)

def extract_video_id(url):
    """Extract video ID from YouTube URL"""
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)',
        r'youtube\.com/watch\?.*v=([^&\n?#]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'active', 'message': 'YouTube Transcript API is running'})

@app.route('/transcript', methods=['POST'])
def get_transcript():
    """Get transcript from YouTube video URL"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided', 'success': False}), 400
        
        video_url = data.get('video_url')
        
        if not video_url:
            return jsonify({'error': 'No video_url field provided', 'success': False}), 400
        
        # Extract video ID
        video_id = extract_video_id(video_url)
        if not video_id:
            return jsonify({
                'error': 'Could not extract video ID from URL. Please provide a valid YouTube URL',
                'success': False
            }), 400
        
        # Fetch transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Format transcript into single string
        formatted_transcript = " ".join([entry['text'] for entry in transcript])
        
        return jsonify({
            'video_id': video_id,
            'transcript': formatted_transcript,
            'word_count': len(formatted_transcript.split()),
            'success': True
        })
    
    except Exception as e:
        return jsonify({
            'error': f'Failed to get transcript: {str(e)}',
            'success': False
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)