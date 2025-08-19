# app.py

import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

# Import the orchestrator function from your main.py
from server import orchestrate_analysis

# --- Configuration ---
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Checks if the file's extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/analyze', methods=['POST'])
def analyze_image_endpoint():
    """API endpoint to receive an image and return analysis JSON."""
    
    # 1. Check if the image file is in the request
    if 'image' not in request.files:
        return jsonify({"error": "No image file part in the request"}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({"error": "No selected image file"}), 400

    # 2. Validate the file
    if file and allowed_file(file.filename):
        # Secure the filename to prevent directory traversal attacks
        filename = secure_filename(file.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        try:
            # 3. Save the image temporarily
            file.save(image_path)
            
            # 4. Run your analysis logic
            analysis_result = orchestrate_analysis(image_path)
            
            # 5. Return the JSON result
            if "error" in analysis_result:
                return jsonify(analysis_result), 500
            return jsonify(analysis_result), 200

        finally:
            # 6. Clean up: delete the temporary image file
            if os.path.exists(image_path):
                os.remove(image_path)
                print(f"Cleaned up temporary file: {image_path}")

    else:
        return jsonify({"error": "File type not allowed"}), 400

if __name__ == '__main__':
    # Runs the Flask app on http://127.0.0.1:5000
    app.run(debug=True)