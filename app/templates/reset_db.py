from app import create_app, db

app = create_app()

with app.app_context():
    # This will delete all existing data and recreate tables with the new columns
    db.drop_all()
    db.create_all()
    print("Database has been reset. Schema is now up to date.")