#!/usr/bin/env python3
import os
import json
import logging
import threading
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.utils import secure_filename

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("web_interface.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("web_interface")

# Flask app initialization
app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.urandom(24)

# Constants
CONFIG_FILE = 'data/config.json'
CSV_FILE = 'data/litclock_annotated.csv'
UPLOAD_FOLDER = 'data'
ALLOWED_EXTENSIONS = {'csv'}

# Set upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Import modules needed for clock control
try:
    from csv_to_json import convert_csv_to_json
except ImportError as e:
    logger.error(f"Error importing module: {e}")

# Global variable to signal clock to regenerate JSON
should_regenerate_json = False

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_config():
    """Load the current configuration"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        # Return default configuration
        return {
            "update_interval": 600,
            "font_size": 40,
            "show_book_info": True,
            "show_author": True,
            "content_filter": "all",
            "display_brightness": 100
        }

def save_config(config):
    """Save the configuration to file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        logger.info(f"Configuration saved: {config}")
        return True
    except Exception as e:
        logger.error(f"Error saving config: {e}")
        return False

@app.route('/')
def index():
    """Render the main settings page"""
    config = load_config()
    return render_template('index.html', config=config)

@app.route('/save_settings', methods=['POST'])
def save_settings():
    """Save updated settings"""
    try:
        config = load_config()
        
        # Update values from form
        config['update_interval'] = int(request.form.get('update_interval', 600))
        config['font_size'] = int(request.form.get('font_size', 40))
        config['show_book_info'] = 'show_book_info' in request.form
        config['show_author'] = 'show_author' in request.form
        config['content_filter'] = request.form.get('content_filter', 'all')
        config['display_brightness'] = int(request.form.get('display_brightness', 100))
        
        # Save the updated config
        if save_config(config):
            flash('Settings saved successfully!', 'success')
        else:
            flash('Error saving settings.', 'error')
            
        return redirect(url_for('index'))
        
    except Exception as e:
        logger.error(f"Error saving settings: {e}")
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    """Handle CSV file upload"""
    global should_regenerate_json
    
    if 'csv_file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('index'))
        
    file = request.files['csv_file']
    
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('index'))
        
    if file and allowed_file(file.filename):
        try:
            # Save the uploaded file
            filename = secure_filename('litclock_annotated.csv')
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Convert to JSON immediately
            json_path = os.path.join(app.config['UPLOAD_FOLDER'], 'quotes.json')
            if convert_csv_to_json(file_path, json_path):
                flash('CSV uploaded and converted to JSON successfully!', 'success')
                should_regenerate_json = True
            else:
                flash('CSV uploaded but error converting to JSON.', 'error')
                
            return redirect(url_for('index'))
            
        except Exception as e:
            logger.error(f"Error uploading CSV: {e}")
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('index'))
    else:
        flash('File type not allowed. Please upload a CSV file.', 'error')
        return redirect(url_for('index'))

@app.route('/api/config', methods=['GET'])
def get_config():
    """API endpoint to get current config"""
    return jsonify(load_config())

@app.route('/api/regenerate', methods=['POST'])
def regenerate_json():
    """API endpoint to regenerate JSON from CSV"""
    global should_regenerate_json
    
    if not os.path.exists(CSV_FILE):
        return jsonify({'success': False, 'error': 'CSV file not found'})
    
    try:
        json_path = os.path.join(app.config['UPLOAD_FOLDER'], 'quotes.json')
        if convert_csv_to_json(CSV_FILE, json_path):
            should_regenerate_json = True
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Failed to convert CSV to JSON'})
    except Exception as e:
        logger.error(f"Error regenerating JSON: {e}")
        return jsonify({'success': False, 'error': str(e)})

def create_template_folders():
    """Create necessary template and static folders"""
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)

def create_templates():
    """Create the HTML templates"""
    index_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Literary Clock Settings</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <div class="container">
        <h1>Literary Clock Settings</h1>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert {{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <form method="post" action="/save_settings">
            <div class="form-group">
                <label for="update_interval">Update Interval (seconds):</label>
                <input type="number" id="update_interval" name="update_interval" min="60" value="{{ config.update_interval }}">
            </div>
            
            <div class="form-group">
                <label for="font_size">Font Size:</label>
                <input type="number" id="font_size" name="font_size" min="10" max="80" value="{{ config.font_size }}">
            </div>
            
            <div class="form-group checkbox">
                <input type="checkbox" id="show_book_info" name="show_book_info" {% if config.show_book_info %}checked{% endif %}>
                <label for="show_book_info">Show Book Information</label>
            </div>
            
            <div class="form-group checkbox">
                <input type="checkbox" id="show_author" name="show_author" {% if config.show_author %}checked{% endif %}>
                <label for="show_author">Show Author</label>
            </div>
            
            <div class="form-group">
                <label for="content_filter">Content Filter:</label>
                <select id="content_filter" name="content_filter">
                    <option value="all" {% if config.content_filter == 'all' %}selected{% endif %}>All</option>
                    <option value="sfw" {% if config.content_filter == 'sfw' %}selected{% endif %}>SFW Only</option>
                    <option value="nsfw" {% if config.content_filter == 'nsfw' %}selected{% endif %}>NSFW Only</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="display_brightness">Display Brightness:</label>
                <input type="range" id="display_brightness" name="display_brightness" min="0" max="100" value="{{ config.display_brightness }}">
                <span id="brightness_value">{{ config.display_brightness }}%</span>
            </div>
            
            <button type="submit" class="btn primary">Save Settings</button>
        </form>
        
        <hr>
        
        <h2>Upload New Quotes CSV</h2>
        <form method="post" action="/upload_csv" enctype="multipart/form-data">
            <div class="form-group">
                <label for="csv_file">Select CSV File:</label>
                <input type="file" id="csv_file" name="csv_file" accept=".csv">
            </div>
            
            <button type="submit" class="btn secondary">Upload CSV</button>
        </form>
        
        <hr>
        
        <button id="regenerate-btn" class="btn tertiary">Regenerate JSON</button>
    </div>
    
    <script src="/static/js/script.js"></script>
</body>
</html>
    """
    
    with open('templates/index.html', 'w') as f:
        f.write(index_html)
    
    css = """
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f5f5f5;
    padding: 20px;
}

.container {
    max-width: 800px;
    margin: 0 auto;
    background-color: #fff;
    padding: 20px;
    border-radius: 5px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

h1, h2 {
    margin-bottom: 20px;
    color: #444;
}

hr {
    margin: 30px 0;
    border: none;
    border-top: 1px solid #ddd;
}

.form-group {
    margin-bottom: 15px;
}

label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
}

.checkbox {
    display: flex;
    align-items: center;
}

.checkbox label {
    margin-bottom: 0;
    margin-left: 10px;
}

input[type="text"],
input[type="number"],
select {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 3px;
    font-size: 16px;
}

input[type="checkbox"] {
    width: 20px;
    height: 20px;
}

input[type="range"] {
    width: 80%;
    margin-right: 10px;
}

.btn {
    display: inline-block;
    padding: 10px 20px;
    border: none;
    border-radius: 3px;
    font-size: 16px;
    cursor: pointer;
    color: #fff;
    margin-top: 10px;
}

.primary {
    background-color: #4CAF50;
}

.secondary {
    background-color: #2196F3;
}

.tertiary {
    background-color: #ff9800;
}

.alert {
    padding: 10px;
    margin-bottom: 20px;
    border-radius: 3px;
}

.success {
    background-color: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

.error {
    background-color: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}

@media (max-width: 600px) {
    .container {
        padding: 10px;
    }
}
    """
    
    with open('static/css/style.css', 'w') as f:
        f.write(css)
        
    js = """
document.addEventListener('DOMContentLoaded', function() {
    // Update brightness value display
    const brightnessSlider = document.getElementById('display_brightness');
    const brightnessValue = document.getElementById('brightness_value');
    
    if (brightnessSlider && brightnessValue) {
        brightnessSlider.addEventListener('input', function() {
            brightnessValue.textContent = this.value + '%';
        });
    }
    
    // Regenerate JSON button
    const regenerateBtn = document.getElementById('regenerate-btn');
    
    if (regenerateBtn) {
        regenerateBtn.addEventListener('click', function() {
            this.disabled = true;
            this.textContent = 'Processing...';
            
            fetch('/api/regenerate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Add success message
                    const container = document.querySelector('.container');
                    const alert = document.createElement('div');
                    alert.className = 'alert success';
                    alert.textContent = 'JSON regenerated successfully!';
                    container.insertBefore(alert, container.firstChild);
                    
                    // Remove the alert after 3 seconds
                    setTimeout(() => {
                        alert.remove();
                    }, 3000);
                } else {
                    // Add error message
                    const container = document.querySelector('.container');
                    const alert = document.createElement('div');
                    alert.className = 'alert error';
                    alert.textContent = 'Error: ' + (data.error || 'Unknown error');
                    container.insertBefore(alert, container.firstChild);
                }
                
                this.disabled = false;
                this.textContent = 'Regenerate JSON';
            })
            .catch(error => {
                console.error('Error:', error);
                this.disabled = false;
                this.textContent = 'Regenerate JSON';
            });
        });
    }
});
    """
    
    with open('static/js/script.js', 'w') as f:
        f.write(js)

def run_web_server(host='0.0.0.0', port=8080):
    """Run the Flask web server"""
    create_template_folders()
    create_templates()
    
    # Make sure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Create default config if it doesn't exist
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            "update_interval": 600,
            "font_size": 40,
            "show_book_info": True,
            "show_author": True,
            "content_filter": "all",
            "display_brightness": 100
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(default_config, f, indent=4)
    
    # Run the Flask app
    logger.info(f"Starting web server on http://{host}:{port}/")
    app.run(host=host, port=port, debug=False)

def start_web_server_thread(host='0.0.0.0', port=8080):
    """Start the web server in a separate thread"""
    web_thread = threading.Thread(target=run_web_server, args=(host, port))
    web_thread.daemon = True
    web_thread.start()
    return web_thread

if __name__ == "__main__":
    run_web_server() 