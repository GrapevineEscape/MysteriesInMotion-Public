import csv
from app import create_app
from app.models import db, Show, Role

app = create_app()

def import_roles(csv_file):
    with app.app_context():
        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            roles = []

            for row in reader:
                # Find the Show by title
                show = Show.query.filter_by(title=row['show_title']).first()

                if show:
                    role = Role(
                        show_id=show.id,
                        name=row['role_name'],
                        gender=row['gender'],
                        age=row['age'],
                        description=row['description']
                    )
                    roles.append(role)
                else:
                    print(f"⚠️ Show not found: {row['show_title']} - Skipping role.")

            if roles:
                db.session.bulk_save_objects(roles)  # Bulk insert roles
                db.session.commit()
                print(f"✅ Imported {len(roles)} roles successfully!")
            else:
                print("❌ No valid roles imported.")

# Run the import
import_roles("role_seedupload.csv")
