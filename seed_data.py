"""Optional utility: add sample complaints to an empty database."""
from database import init_db, add_sample_data

if __name__ == "__main__":
    init_db()
    count = add_sample_data()
    if count:
        print(f"Added {count} sample complaints.")
    else:
        print("Sample data was not added because the database already contains complaints.")
