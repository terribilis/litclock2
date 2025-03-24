#!/usr/bin/env python3
import os
import json
import logging
import threading
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.utils import secure_filename

# Set up logging
logger = logging.getLogger(__name__)

# Global variable to signal clock to regenerate JSON
should_regenerate_json = False

class WebInterface:
    def __init__(self, app=None, config_path='data/config.json'):
        self.app = app or Flask(__name__)
        self.app.secret_key = os.urandom(24)
        
        # Set up paths
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_path = os.path.join(self.base_dir, config_path)
        self.csv_path = os.path.join(self.base_dir, 'data', 'litclock_annotated.csv')
        self.upload_folder = os.path.join(self.base_dir, 'data')
        self.allowed_extensions = {'csv'}
        
        # Set upload folder
        self.app.config['UPLOAD_FOLDER'] = self.upload_folder
        
        # Make sure data directory exists
        os.makedirs(self.upload_folder, exist_ok=True)
        
        # Create default config if it doesn't exist
        if not os.path.exists(self.config_path):
            default_config = {
                "update_interval": 600,
                "font_size": 40,
                "show_book_info": True,
                "show_author": True,
                "content_filter": "all",
                "display_brightness": 100
            }
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=4)
        
        # Set up routes
        self.setup_routes()
        
        # Create template directories and files
        self.setup_templates()
    
    def setup_routes(self):
        """Set up Flask routes"""
        @self.app.route('/')
        def index():
            """Render the main settings page"""
            config = self.load_config()
            return render_template('index.html', config=config)

        @self.app.route('/save_settings', methods=['POST'])
        def save_settings():
            """Save updated settings"""
            try:
                config = self.load_config()
                
                # Update values from form
                config['update_interval'] = int(request.form.get('update_interval', 600))
                config['font_size'] = int(request.form.get('font_size', 40))
                config['show_book_info'] = 'show_book_info' in request.form
                config['show_author'] = 'show_author' in request.form
                config['content_filter'] = request.form.get('content_filter', 'all')
                config['display_brightness'] = int(request.form.get('display_brightness', 100))
                
                # Save the updated config
                if self.save_config(config):
                    flash('Settings saved successfully!', 'success')
                else:
                    flash('Error saving settings.', 'error')
                    
                return redirect(url_for('index'))
                
            except Exception as e:
                logger.error(f"Error saving settings: {e}")
                flash(f'Error: {str(e)}', 'error')
                return redirect(url_for('index'))

        @self.app.route('/upload_csv', methods=['POST'])
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
                
            if file and self.allowed_file(file.filename):
                try:
                    # Save the uploaded file
                    filename = secure_filename('litclock_annotated.csv')
                    file_path = os.path.join(self.app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    
                    # Convert to JSON immediately
                    json_path = os.path.join(self.app.config['UPLOAD_FOLDER'], 'quotes.json')
                    
                    # Import here to avoid circular imports
                    from litclock.utils.csv_converter import convert_csv_to_json
                    
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

        @self.app.route('/api/config', methods=['GET'])
        def get_config():
            """API endpoint to get current config"""
            return jsonify(self.load_config())

        @self.app.route('/api/regenerate', methods=['POST'])
        def regenerate_json():
            """API endpoint to regenerate JSON from CSV"""
            global should_regenerate_json
            
            if not os.path.exists(self.csv_path):
                return jsonify({'success': False, 'error': 'CSV file not found'})
            
            try:
                json_path = os.path.join(self.upload_folder, 'quotes.json')
                
                # Import here to avoid circular imports
                from litclock.utils.csv_converter import convert_csv_to_json
                
                if convert_csv_to_json(self.csv_path, json_path):
                    should_regenerate_json = True
                    return jsonify({'success': True})
                else:
                    return jsonify({'success': False, 'error': 'Failed to convert CSV to JSON'})
            except Exception as e:
                logger.error(f"Error regenerating JSON: {e}")
                return jsonify({'success': False, 'error': str(e)})
    
    def allowed_file(self, filename):
        """Check if the file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def load_config(self):
        """Load the current configuration"""
        try:
            with open(self.config_path, 'r') as f:
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
    
    def save_config(self, config):
        """Save the configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=4)
            logger.info(f"Configuration saved: {config}")
            return True
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return False
    
    def setup_templates(self):
        """Create necessary template and static folders"""
        templates_dir = os.path.join(self.base_dir, 'litclock', 'templates')
        static_dir = os.path.join(self.base_dir, 'litclock', 'static')
        css_dir = os.path.join(static_dir, 'css')
        js_dir = os.path.join(static_dir, 'js')
        
        os.makedirs(templates_dir, exist_ok=True)
        os.makedirs(static_dir, exist_ok=True)
        os.makedirs(css_dir, exist_ok=True)
        os.makedirs(js_dir, exist_ok=True)
        
        # Create the index template
        index_path = os.path.join(templates_dir, 'index.html')
        if not os.path.exists(index_path):
            with open(index_path, 'w') as f:
                f.write(self.get_index_template())
        
        # Create the CSS file
        css_path = os.path.join(css_dir, 'style.css')
        if not os.path.exists(css_path):
            with open(css_path, 'w') as f:
                f.write(self.get_css_template())
        
        # Create the JS file
        js_path = os.path.join(js_dir, 'script.js')
        if not os.path.exists(js_path):
            with open(js_path, 'w') as f:
                f.write(self.get_js_template())
    
    def get_index_template(self):
        """Return the HTML template for the index page"""
        return """
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
    
    def get_css_template(self):
        """Return the CSS template"""
        return """
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
    
    def get_js_template(self):
        """Return the JavaScript template"""
        return """
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
    
    def run(self, host='0.0.0.0', port=8080, debug=False):
        """Run the Flask web server"""
        logger.info(f"Starting web server on http://{host}:{port}/")
        self.app.run(host=host, port=port, debug=debug)

def start_web_server_thread(host='0.0.0.0', port=8080):
    """Start the web server in a separate thread"""
    web_interface = WebInterface()
    web_thread = threading.Thread(target=web_interface.run, args=(host, port, False))
    web_thread.daemon = True
    web_thread.start()
    return web_thread

def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("web_interface.log"),
            logging.StreamHandler()
        ]
    )
    
    parser = argparse.ArgumentParser(description='Web Interface for Literary Clock')
    parser.add_argument('--port', type=int, default=8080, help='Port to run the web server on')
    parser.add_argument('--host', default='0.0.0.0', help='Host to run the web server on')
    
    args = parser.parse_args()
    
    # Run the web server
    web_interface = WebInterface()
    web_interface.run(host=args.host, port=args.port)

if __name__ == "__main__":
    main() 