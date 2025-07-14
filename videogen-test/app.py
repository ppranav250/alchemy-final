from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import logging
from api.orchestrator import process_research_paper

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_paper():
    data = request.get_json()
    paper_url = data.get('url')

    if not paper_url:
        return jsonify({'error': 'URL is required'}), 400

    # Call the orchestrator function which handles the entire workflow
    result = process_research_paper(paper_url)

    if 'error' in result:
        return jsonify(result), 500
    
    return jsonify(result)

# Add a route to serve the generated media files
@app.route('/media/<path:filename>')
def media_files(filename):
    return send_from_directory('media', filename)

if __name__ == '__main__':
    # Ensure the media directory exists
    os.makedirs('media/audio', exist_ok=True)
    app.run(debug=True)
