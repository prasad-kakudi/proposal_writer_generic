from flask import Flask, render_template, request, jsonify, session, send_file
import os
import uuid
from werkzeug.utils import secure_filename
from services.file_processor import FileProcessor
from services.gemini_service import GeminiService
from services.document_generator import DocumentGenerator
from utils.session_manager import SessionManager
from dotenv import load_dotenv
global env
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create directories if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Initialize services
file_processor = FileProcessor()
gemini_service = GeminiService()
document_generator = DocumentGenerator()
session_manager = SessionManager()

@app.route('/')
def index():
    # Initialize session if not exists
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    
    user_sessions = session_manager.get_user_sessions(session['user_id'])
    return render_template('index.html', sessions=user_sessions)

@app.route('/upload_rfp', methods=['POST'])
def upload_rfp():
    try:
        if 'rfp_file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400
        
        file = request.files['rfp_file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process file content
        content = file_processor.extract_text(filepath)
        
        # Analyze with Gemini
        requirements = gemini_service.analyze_rfp(content)
        
        # Update session
        session_data = session_manager.update_rfp_data(
            session['user_id'], filename, requirements, content
        )
        
        return jsonify({
            'success': True,
            'requirements': requirements,
            'filename': filename
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload_org', methods=['POST'])
def upload_org():
    try:
        if 'org_file' not in request.files:
            return jsonify({'error': 'No organization file selected'}), 400
        
        file = request.files['org_file']
        if file.filename == '':
            return jsonify({'error': 'No organization file selected'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process file content
        content = file_processor.extract_text(filepath)
        
        # Get current RFP requirements from session
        current_session = session_manager.get_current_session(session['user_id'])
        if not current_session or 'rfp_requirements' not in current_session:
            return jsonify({'error': 'Please upload RFP file first'}), 400
        
        # Analyze organization and create matching
        org_analysis = gemini_service.analyze_organization(content)
        matching_table = gemini_service.create_matching_table(
            current_session['rfp_requirements'], org_analysis
        )
        
        # Generate initial prompt
        response_prompt = gemini_service.generate_response_prompt(
            current_session['rfp_requirements'], org_analysis
        )
        
        # Update session
        session_manager.update_org_data(
            session['user_id'], filename, org_analysis, 
            matching_table, response_prompt
        )
        
        return jsonify({
            'success': True,
            'org_analysis': org_analysis,
            'matching_table': matching_table,
            'response_prompt': response_prompt,
            'filename': filename
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate_document', methods=['POST'])
def generate_document():
    try:
        data = request.get_json()
        final_prompt = data.get('prompt', '')
        
        if not final_prompt:
            return jsonify({'error': 'No prompt provided'}), 400
        
        # Generate document
        output_filename = f"rfp_response_{session['user_id'][:8]}.docx"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        document_generator.create_docx(final_prompt, output_path)
        
        # Update session with output file
        session_manager.update_output_file(session['user_id'], output_filename)
        
        return jsonify({
            'success': True,
            'download_url': f'/download/{output_filename}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_sessions')
def get_sessions():
    user_sessions = session_manager.get_user_sessions(session['user_id'])
    return jsonify(user_sessions)

@app.route('/delete_session/<int:session_id>', methods=['DELETE'])
def delete_session(session_id):
    try:
        session_manager.delete_session(session['user_id'], session_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)