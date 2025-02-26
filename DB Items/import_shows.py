import csv
from app import create_app
from app.models import db, Show

app = create_app()

def import_shows(csv_file):
    with app.app_context():
        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            shows = [
                Show(
                    title=row['title'],
                    description=row['description'],
                    type=row['type'],
                    kid_friendly=(row['kid_friendly'].strip().lower() == 'true'),  # Convert string to boolean
                    script_path=row.get('script_path', None),
                    image_path=row.get('image_path', None),
                ) for row in reader
            ]
            db.session.bulk_save_objects(shows)  # Bulk insert
            db.session.commit()
            print(f"✅ Imported {len(shows)} shows successfully!")

# Run the import
import_shows("shows.csv")
