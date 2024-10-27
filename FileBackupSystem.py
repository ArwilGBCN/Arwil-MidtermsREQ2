from flask import Flask, request, render_template_string, redirect, url_for, flash
import shutil
import os
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for flashing messages

# Global variables for backup paths and destination
backup_paths = []
backup_destination = 'backup/'  # Default destination

def perform_backup():
    """Function to perform the backup operation."""
    for path in backup_paths:
        try:
            if os.path.isfile(path):
                shutil.copy2(path, backup_destination)
                print(f"Backup successful for file: {path}")
            elif os.path.isdir(path):
                dir_name = os.path.basename(path.rstrip('/\\'))
                shutil.copytree(path, os.path.join(backup_destination, dir_name), dirs_exist_ok=True)
                print(f"Backup successful for directory: {path}")
            else:
                print(f"Invalid path (not a file or directory): {path}")
        except Exception as e:
            print(f"Failed to back up {path}. Error: {e}")

# Schedule automatic backups (e.g., every 1 hour)
scheduler = BackgroundScheduler()
scheduler.add_job(perform_backup, 'interval', hours=1)
scheduler.start()

@app.route('/')
def index():
    html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>File Backup System</title>
        <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {
                background-color: #f8f9fa;
                padding: 20px;
            }
            .container {
                max-width: 800px;
                margin: auto;
                background-color: #fff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
            }
            .card {
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="text-center">File Backup System</h1>
            <hr>
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    <div class="alert alert-dismissible fade show">
                        {% for category, message in messages %}
                            <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                                {{ message }}
                                <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                                    <span aria-hidden="true">&times;</span>
                                </button>
                            </div>
                        {% endfor %}
                    </div>
                {% endif %}
            {% endwith %}

            <div class="card">
                <div class="card-header">
                    <h5>Add a Path to Backup (File or Directory)</h5>
                </div>
                <div class="card-body">
                    <form action="/add-path" method="POST">
                        <div class="form-group">
                            <label for="file_path">Enter Path of a File or Directory:</label>
                            <input type="text" class="form-control" id="file_path" name="file_path" required>
                        </div>
                        <button type="submit" class="btn btn-primary">Add Path</button>
                    </form>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <h5>Set Backup Destination</h5>
                </div>
                <div class="card-body">
                    <form action="/set-destination" method="POST">
                        <div class="form-group">
                            <label for="destination">Backup Destination:</label>
                            <input type="text" class="form-control" id="destination" name="destination" value="{{ backup_destination }}" required>
                        </div>
                        <button type="submit" class="btn btn-secondary">Set Destination</button>
                    </form>
                </div>
            </div>

            <div class="card">
                <div class="card-body text-center">
                    <form action="/backup-now" method="POST">
                        <button type="submit" class="btn btn-success">Backup Now</button>
                    </form>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <h5>Backup Paths</h5>
                </div>
                <div class="card-body">
                    <ul class="list-group">
                        {% for path in backup_paths %}
                            <li class="list-group-item">{{ path }}</li>
                        {% endfor %}
                    </ul>
                </div>
            </div>

            <div class="card mt-3">
                <div class="card-header">
                    <h5>Current Backup Destination</h5>
                </div>
                <div class="card-body">
                    <p class="font-weight-bold">{{ backup_destination }}</p>
                </div>
            </div>
        </div>

        <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.5.2/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    '''
    return render_template_string(html, backup_paths=backup_paths, backup_destination=backup_destination)

@app.route('/add-path', methods=['POST'])
def add_path():
    path = request.form.get('file_path')
    if path:
        if os.path.exists(path):
            if os.path.isfile(path):
                backup_paths.append(path)
                flash(f"File path added successfully: {path}", "success")
            elif os.path.isdir(path):
                backup_paths.append(path)
                flash(f"Directory path added successfully: {path}", "success")
            else:
                flash(f"Invalid path. Not a file or directory: {path}", "danger")
        else:
            flash(f"Path does not exist: {path}", "danger")
    return redirect(url_for('index'))

@app.route('/set-destination', methods=['POST'])
def set_destination():
    global backup_destination
    destination = request.form.get('destination')
    if destination:
        if not os.path.exists(destination):
            try:
                os.makedirs(destination)
                flash(f"Destination directory created: {destination}", "success")
            except Exception as e:
                flash(f"Failed to create destination directory. Error: {e}", "danger")
                return redirect(url_for('index'))
        backup_destination = destination
        flash(f"Backup destination updated to: {backup_destination}", "success")
    return redirect(url_for('index'))

@app.route('/backup-now', methods=['POST'])
def backup_now():
    perform_backup()
    flash("Backup completed successfully!", "success")
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Create backup directory if not exist
    if not os.path.exists(backup_destination):
        os.makedirs(backup_destination)

    app.run(debug=True)
