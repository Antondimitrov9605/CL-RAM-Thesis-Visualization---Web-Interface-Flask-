"""
CL-RAM Thesis Visualization - Web Interface
Flask web application for generating and viewing visualizations
"""

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
import pandas as pd
from pathlib import Path
from datetime import datetime
import json
import threading
import sys
import os
from werkzeug.utils import secure_filename

sys.path.insert(0, os.path.dirname(__file__))
import visualization_engine as viz

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max

# Global state
current_status = {
    'running': False,
    'progress': 0,
    'message': 'Ready',
    'output_dir': None,
    'charts': [],
    'tables': [],
    'error': None
}

def parse_text_log(filepath):
    """Parse text log file into DataFrame"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by test blocks (separated by blank lines)
        blocks = [b.strip() for b in content.split('\n\n') if b.strip()]
        
        data = []
        for block in blocks:
            test = {}
            for line in block.split('\n'):
                line = line.strip()
                if 'Model:' in line or 'model:' in line:
                    test['model'] = line.split(':', 1)[1].strip()
                elif 'Category:' in line or 'category:' in line:
                    test['category'] = line.split(':', 1)[1].strip()
                elif 'Language:' in line or 'language:' in line:
                    test['language'] = line.split(':', 1)[1].strip()
                elif 'Temperature:' in line or 'temperature:' in line:
                    try:
                        test['temperature'] = float(line.split(':', 1)[1].strip())
                    except:
                        pass
                elif 'Success:' in line or 'success:' in line:
                    val = line.split(':', 1)[1].strip().lower()
                    test['success'] = 1 if val in ['true', '1', 'yes', 'success'] else 0
            
            if 'model' in test and 'category' in test:
                data.append(test)
        
        return pd.DataFrame(data) if data else None
    except Exception as e:
        print(f"Error parsing text file: {e}")
        return None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv', 'json', 'txt'}

def generate_visualizations(filepath):
    """Generate visualizations from file"""
    global current_status
    
    try:
        current_status['running'] = True
        current_status['progress'] = 5
        current_status['message'] = 'Loading data...'
        current_status['error'] = None
        
        # Load data
        filepath = Path(filepath)
        
        if filepath.suffix.lower() == '.csv':
            df = pd.read_csv(filepath, encoding='utf-8')
        elif filepath.suffix.lower() == '.json':
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            df = pd.DataFrame(data if isinstance(data, list) else [data])
        elif filepath.suffix.lower() == '.txt':
            # Parse text log file
            df = parse_text_log(filepath)
            if df is None:
                raise ValueError("Failed to parse text file")
        else:
            raise ValueError(f"Unsupported file type: {filepath.suffix}")
        
        current_status['progress'] = 10
        current_status['message'] = f'Loaded {len(df):,} records'
        
        # Create output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path("thesis_visualizations") / f"session_{timestamp}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        current_status['output_dir'] = str(output_dir)
        current_status['progress'] = 15
        
        # Generate visualizations
        total_steps = 11
        
        # 1. Linear progression
        current_status['message'] = 'Generating linear progression charts...'
        current_status['progress'] = 20
        try:
            viz.create_linear_progression_charts(df, output_dir)
        except Exception as e:
            print(f"Error in linear progression: {e}")
        
        # 2. Temperature analysis
        current_status['message'] = 'Generating temperature analysis...'
        current_status['progress'] = 30
        try:
            viz.create_enhanced_temperature_analysis(df, output_dir)
            viz.create_temperature_heatmaps(df, output_dir)
            viz.create_2d_temperature_language_comparison(df, output_dir)
        except Exception as e:
            print(f"Error in temperature analysis: {e}")
        
        # 3. Bar charts
        current_status['message'] = 'Generating bar charts...'
        current_status['progress'] = 40
        try:
            viz.create_enhanced_bar_charts(df, output_dir)
        except Exception as e:
            print(f"Error in bar charts: {e}")
        
        # 4. Pie charts
        current_status['message'] = 'Generating pie charts...'
        current_status['progress'] = 50
        try:
            viz.create_pie_charts(df, output_dir)
        except Exception as e:
            print(f"Error in pie charts: {e}")
        
        # 5. Heatmaps
        current_status['message'] = 'Generating heatmaps...'
        current_status['progress'] = 60
        try:
            viz.create_model_language_heatmap(df, output_dir)
            viz.create_category_language_heatmap(df, output_dir)
        except Exception as e:
            print(f"Error in heatmaps: {e}")
        
        # 6. Dashboard
        current_status['message'] = 'Generating dashboard...'
        current_status['progress'] = 70
        try:
            viz.create_analysis_summary_dashboard(df, output_dir)
        except Exception as e:
            print(f"Error in dashboard: {e}")
        
        # 7. Tables
        current_status['message'] = 'Generating statistical tables...'
        current_status['progress'] = 80
        try:
            viz.create_comparison_tables(df, output_dir)
            viz.create_temperature_comparison_table(df, output_dir)
            viz.create_model_specific_category_tables(df, output_dir)
        except Exception as e:
            print(f"Error in tables: {e}")
        
        # 8. Model-specific analysis
        current_status['message'] = 'Generating model-specific analysis...'
        current_status['progress'] = 90
        try:
            viz.create_model_specific_temperature_language_analysis(df, output_dir)
            viz.create_models_temperature_language_summary(df, output_dir)
            viz.create_detailed_model_language_comparison(df, output_dir)
        except Exception as e:
            print(f"Error in model analysis: {e}")
        
        # 9. HTML report
        current_status['message'] = 'Generating HTML report...'
        current_status['progress'] = 95
        try:
            files_dict = {
                'charts': list(output_dir.glob("**/*.png")),
                'tables': list(output_dir.glob("**/*.csv"))
            }
            viz.create_simple_html_report(df, output_dir, files_dict)
        except Exception as e:
            print(f"Error in HTML report: {e}")
        
        # Collect results
        current_status['charts'] = [str(f.relative_to(output_dir)) for f in output_dir.glob("**/*.png")]
        current_status['tables'] = [str(f.relative_to(output_dir)) for f in output_dir.glob("**/*.csv")]
        
        current_status['progress'] = 100
        current_status['message'] = f'Complete! Generated {len(current_status["charts"])} charts and {len(current_status["tables"])} tables'
        
    except Exception as e:
        current_status['error'] = str(e)
        current_status['message'] = f'Error: {str(e)}'
        import traceback
        traceback.print_exc()
    
    finally:
        current_status['running'] = False

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Use CSV or JSON'}), 400
    
    # Save file
    uploads_dir = Path(app.config['UPLOAD_FOLDER'])
    uploads_dir.mkdir(exist_ok=True)
    
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = uploads_dir / f"{timestamp}_{filename}"
    file.save(filepath)
    
    # Start generation in background
    thread = threading.Thread(target=generate_visualizations, args=(filepath,), daemon=True)
    thread.start()
    
    return jsonify({'success': True, 'message': 'File uploaded, generation started'})

@app.route('/status')
def get_status():
    """Get current status"""
    return jsonify(current_status)

@app.route('/chart/<path:filename>')
def get_chart(filename):
    """Serve chart image"""
    if current_status['output_dir']:
        return send_from_directory(current_status['output_dir'], filename)
    return "No output directory", 404

@app.route('/table/<path:filename>')
def get_table(filename):
    """Serve table CSV"""
    if current_status['output_dir']:
        filepath = Path(current_status['output_dir']) / filename
        if filepath.exists():
            df = pd.read_csv(filepath)
            return jsonify(df.to_dict('records'))
    return jsonify({'error': 'File not found'}), 404

@app.route('/download/<path:filename>')
def download_file(filename):
    """Download file"""
    if current_status['output_dir']:
        return send_from_directory(current_status['output_dir'], filename, as_attachment=True)
    return "No output directory", 404

@app.route('/reset', methods=['POST'])
def reset():
    """Reset application state"""
    global current_status
    current_status = {
        'running': False,
        'progress': 0,
        'message': 'Ready',
        'output_dir': None,
        'charts': [],
        'tables': [],
        'error': None
    }
    return jsonify({'success': True, 'message': 'Reset complete'})

if __name__ == '__main__':
    print("="*70)
    print("CL-RAM THESIS VISUALIZATION - WEB INTERFACE")
    print("="*70)
    print("\nStarting web server...")
    print("\nOpen your browser and go to:")
    print("  http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
