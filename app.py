from flask import Flask, render_template, request, jsonify
import os
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from datetime import datetime
import psutil
import webbrowser
from waitress import serve 

app = Flask(__name__)

# Thread pool executor for parallel processing
executor = ThreadPoolExecutor()

# Custom Jinja2 filter for formatting datetime
def datetimeformat(value, format='%Y-%m-%d %H:%M:%S'):
    return datetime.fromtimestamp(value).strftime(format)

app.jinja_env.filters['datetimeformat'] = datetimeformat

# Helper Functions
def get_drive_info():
    """Get a list of drives and their storage statistics."""
    drives = []
    partitions = psutil.disk_partitions()
    for partition in partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            drives.append({
                'device': partition.device,
                'mountpoint': partition.mountpoint,
                'total': usage.total,
                'used': usage.used,
                'free': usage.free,
                'percent': usage.percent
            })
        except PermissionError:
            continue
    return drives

def get_directory_size(path):
    """Calculate the total size of a directory recursively."""
    total_size = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                total_size += os.path.getsize(fp)
            except FileNotFoundError:
                pass
    return total_size

@lru_cache(maxsize=10)
def get_directory_info(path, sort_by="size"):
    """Retrieve directory information with sorting and caching."""
    directory_data = {'files': [], 'directories': []}
    try:
        entries = os.scandir(path)
        for entry in entries:
            try:
                stats = entry.stat()
                if entry.is_file():
                    directory_data['files'].append({
                        'name': entry.name,
                        'size': stats.st_size,
                        'atime': getattr(stats, 'st_atime', None),
                        'mtime': stats.st_mtime,
                        'path': entry.path
                    })
                elif entry.is_dir():
                    directory_data['directories'].append({
                        'name': entry.name,
                        'size': get_directory_size(entry.path),
                        'atime': getattr(stats, 'st_atime', None),
                        'path': entry.path
                    })
            except Exception as e:
                print(f"Error processing entry {entry}: {e}")

        # Sorting
        if sort_by == "recent":
            directory_data['files'].sort(key=lambda x: x['atime'], reverse=True)
            directory_data['directories'].sort(key=lambda x: x['atime'], reverse=True)
        elif sort_by == "least":
            directory_data['files'].sort(key=lambda x: x['atime'])
            directory_data['directories'].sort(key=lambda x: x['atime'])
        else:  # Default to sorting by size
            directory_data['files'].sort(key=lambda x: x['size'], reverse=True)
            directory_data['directories'].sort(key=lambda x: x['size'], reverse=True)
    except Exception as e:
        print(f"Error reading directory {path}: {e}")
    return directory_data

def suggest_files_for_removal(path, threshold=40):
    """Suggest files for removal when drive is almost full."""
    drives = get_drive_info()
    suggestions = []
    for drive in drives:
        if drive['percent'] >= threshold and path.startswith(drive['mountpoint']):
            directory_data = get_directory_info(path, sort_by="least")
            suggestions.extend(directory_data['files'][:5])  # Suggest top 5 least accessed files
    return suggestions

# Routes
@app.route("/")
def home():
    drives = get_drive_info()
    return render_template("index.html", drives=drives)

@app.route("/directory")
def directory_view():
    try:
        path = request.args.get("path", "")
        sort_by = request.args.get("sort", "size")
        if not os.path.exists(path):
            return jsonify({"error": "Path does not exist"}), 404
        directory_data = get_directory_info(path, sort_by)
        suggestions = suggest_files_for_removal(path)
        return render_template("directory.html", directory=path, data=directory_data, suggestions=suggestions)
    except:
        print("Unknown error")

@app.route("/api/directory")
def api_directory_view():
    """API to fetch directory data."""
    path = request.args.get("path", "")
    sort_by = request.args.get("sort", "size")
    if not os.path.exists(path):
        return jsonify({"error": "Path does not exist"}), 404
    directory_data = get_directory_info(path, sort_by)
    return jsonify(directory_data)

@app.route("/api/remove_file", methods=["POST"])
def remove_file():
    """API to remove a file and recompute storage."""
    file_path = request.json.get("file_path", "")
    if not os.path.exists(file_path):
        return jsonify({"error": "File does not exist"}), 404
    try:
        os.remove(file_path)
        drive_info = get_drive_info()
        return jsonify({"success": True, "updated_drive_info": drive_info})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/compress', methods=['POST'])
def compress_files():
    try:
        data = request.get_json()
        items = data.get('items', [])

        if not items:
            return jsonify({"success": False, "error": "No items selected for compression."})

        # Determine the common parent directory
        parent_dir = os.path.commonpath(items)

        # Create a unique zip file name in the parent directory
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        zip_filename = f"compressed_{timestamp}.zip"
        zip_filepath = os.path.join(parent_dir, zip_filename)

        # Create the zip file
        with zipfile.ZipFile(zip_filepath, 'w') as zipf:
            for item in items:
                if os.path.exists(item):
                    if os.path.isfile(item):
                        # Add file to the zip
                        zipf.write(item, os.path.basename(item))
                    elif os.path.isdir(item):
                        # Add directory recursively to the zip
                        for root, dirs, files in os.walk(item):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, parent_dir)  # Preserve directory structure
                                zipf.write(file_path, arcname)
                else:
                    return jsonify({"success": False, "error": f"Item '{item}' does not exist."})

        return jsonify({"success": True, "message": f"Files compressed and saved as {zip_filepath}"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# Run App
if __name__ == "__main__":
    webbrowser.open("http://127.0.0.1:5000")
    serve(app, host="0.0.0.0", port=5000)