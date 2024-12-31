# Storage Ultilization Dashboard

A Flask-based web application that provides a dynamic and visually appealing dashboard for monitoring and managing storage utlization across drives and directories. It offers insights into storage usage, detailed directory views, and sugestions for file removal when space is constrained.

---

## Features

- **Drive Monitoring**: Displays all available drives with their storage statistics.
- **Dynamic Directory views**: Explore directires dynamically with detailed information on files and subdirectories.
- **Visualization**: Use pie charts to visually represent storage usage.
- **File Removal SUggestions**: Recommends files for removal based on last access time when storage usage exceeds a defined threshold.
- **Responsive Design**: A moder, user-friendly, and responsive UI for seamless navigation.

---

## Technologies Used

-**Backend**: Flask
-**Frontend**: HTML,CSS, Chart.js
-**Libraries**: `psutil`,`os`,`concurrent.futures`

---

## Prerequisites
Ensure the following are installed:

- Python 3.7+
- pip

---

## Setup and Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/RohithgowdaM/storage-dashboard.git
   cd storage-dashboard
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the Flask application:
   ```bash
   python app.py
   ```

4. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

---

## Project Structure

```
storage-dashboard/
├── templates/
│   ├── index.html       # Drive view template
│   ├── directory.html   # Directory view template
├── static/              # Static files (if any)
├── app.py               # Main application logic
├── requirements.txt     # Project dependencies
├── README.md            # Project documentation
```

---

## API Endpoints

- `/`: Home route displaying all drives and their storage statistics.
- `/directory?path=<path>`: Displays details for a specific directory.
- `/api/directory?path=<path>`: API endpoint for fetching directory data in JSON format.

---

## Customization

- **Drive Threshold**: Adjust the `threshold` parameter in the `suggest_files_for_removal` function to change the storage usage percentage that triggers suggestions.
- **Visualization Colors**: Modify the `backgroundColor` in the Chart.js configuration for custom chart colors.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

---

## Contributions

Contributions are welcome! Please submit a pull request or open an issue for any feature requests or bug reports.

---

## Author

- **Rohith Gowda M**: [GitHub Profile](https://github.com/RohithgowdaM)
