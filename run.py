from app import create_app, db
import os
from dotenv import load_dotenv

load_dotenv()

print("Initializing application...")
app = create_app()

if __name__ == '__main__':
    print("Checking setup...")
    # Ensure upload directory exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
        print(f"Created upload folder at {app.config['UPLOAD_FOLDER']}")
    
    # Create DB if not exists
    with app.app_context():
        db.create_all()
        print("Database initialized.")
        
    print("Starting Flask server on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
