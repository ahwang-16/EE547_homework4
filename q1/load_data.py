import psycopg2
import csv
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description="Load transit data into PostgreSQL")
    parser.add_argument('--datadir', default='/app/data', help='Directory containing CSV files')
    parser.add_argument('--host', default='db')
    parser.add_argument('--dbname', default='transit')
    parser.add_argument('--user', default='transit')
    parser.add_argument('--password', default='transit123')

    args = parser.parse_args()

    tables_to_load = [
        {
            "file": "lines.csv",
            "sql": "INSERT INTO lines (line_name, vehicle_type) VALUES (%s, %s) ON CONFLICT (line_name) DO NOTHING"
        },
        {
            "file": "stops.csv",
            "sql": "INSERT INTO stops (stop_name, latitude, longitude) VALUES (%s, %s, %s) ON CONFLICT (stop_name) DO NOTHING"
        },
        {
            "file": "line_stops.csv",
            "sql": (
                "INSERT INTO line_stops (line_name, stop_name, sequence, time_offset) "
                "VALUES (%s, %s, %s, %s) ON CONFLICT (line_name, sequence) DO NOTHING"
            )
        },
        {
            "file": "trips.csv",
            "sql": (
                "INSERT INTO trips (trip_id, line_name, scheduled_departure, vehicle_id) "
                "VALUES (%s, %s, %s, %s) ON CONFLICT (trip_id) DO NOTHING"
            )
        },
        {
            "file": "stop_events.csv",
            "sql": (
                "INSERT INTO stop_events (trip_id, stop_name, scheduled, actual, passengers_on, passengers_off) "
                "VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (trip_id, stop_name) DO NOTHING"
            )
        }
    ]

    try:
        conn = psycopg2.connect(
            host=args.host, dbname=args.dbname, user=args.user, password=args.password
        )
        cur = conn.cursor()
        print(f"Connected to {args.user}@{args.host}")

        print("Creating schema...")
        with open('schema.sql', 'r') as f:
            schema_sql = f.read()
        cur.execute(schema_sql)
        conn.commit()
        print("Tables created: lines, stops, line_stops, trips, stop_events\n")

        total_rows = 0
        for table in tables_to_load:
            filepath = os.path.join(args.datadir, table["file"])

            with open(filepath, 'r') as csv_file:
                reader = csv.reader(csv_file)
                next(reader)

                data = list(reader)
                cur.executemany(table["sql"], data)

                rows_loaded = len(data)
                total_rows += rows_loaded
                print(f"Loading {filepath}... {rows_loaded:,} rows")

        conn.commit()
        print(f"\nTotal: {total_rows:,} rows loaded")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'conn' in locals():
            cur.close()
            conn.close()

if __name__ == '__main__':
    main()
