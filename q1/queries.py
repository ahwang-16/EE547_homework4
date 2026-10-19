import psycopg2
import argparse
import json
import decimal
from datetime import datetime

# Helper to safely serialize SQL Decimals and Timestamps to JSON
def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

def run_query(conn, query_num, format_type):
    cur = conn.cursor()

    queries = {
        "Q1": {
            "description": "List all stops on Route 20 in order",
            "sql": """
                SELECT s.stop_name, ls.sequence, ls.time_offset
                FROM line_stops ls
                JOIN lines l ON ls.line_name = l.line_name
                JOIN stops s ON ls.stop_name = s.stop_name
                WHERE l.line_name = 'Route 20'
                ORDER BY ls.sequence;
            """
        },
        "Q2": {
            "description": "Trips during morning rush",
            "sql": """
                SELECT trip_id, line_name, scheduled_departure
                FROM trips
                WHERE CAST(scheduled_departure AS TIME) >= '07:00:00'
                  AND CAST(scheduled_departure AS TIME) < '09:00:00'
                ORDER BY scheduled_departure;
            """
        },
        "Q3": {
            "description": "Transfer stops (stops on 2+ routes)",
            "sql": """
                SELECT stop_name, count(line_name) as line_count
                FROM line_stops
                GROUP BY stop_name
                HAVING count(line_name) >= 2
                ORDER BY line_count DESC, stop_name;
            """
        },
        "Q4": {
            "description": "Complete route for trip T0001",
            "sql": """
                SELECT se.stop_name, se.scheduled, se.actual, se.passengers_on, se.passengers_off
                FROM stop_events se
                JOIN trips t ON se.trip_id = t.trip_id
                JOIN line_stops ls ON t.line_name = ls.line_name AND se.stop_name = ls.stop_name
                WHERE se.trip_id = 'T0001'
                ORDER BY ls.sequence;
            """
        },
        "Q5": {
            "description": "Routes serving both Wilshire / Veteran and Le Conte / Broxton",
            "sql": """
                SELECT line_name
                FROM line_stops
                WHERE stop_name = 'Wilshire / Veteran'
                INTERSECT
                SELECT line_name
                FROM line_stops
                WHERE stop_name = 'Le Conte / Broxton'
                ORDER BY line_name;
            """
        },
        "Q6": {
            "description": "Average ridership by line",
            "sql": """
                SELECT t.line_name, AVG(se.passengers_on) as avg_passengers
                FROM stop_events se
                JOIN trips t ON se.trip_id = t.trip_id
                GROUP BY t.line_name
                ORDER BY avg_passengers DESC;
            """
        },
        "Q7": {
            "description": "Top 10 busiest stops",
            "sql": """
                SELECT stop_name, SUM(passengers_on + passengers_off) as total_activity
                FROM stop_events
                GROUP BY stop_name
                ORDER BY total_activity DESC
                LIMIT 10;
            """
        },
        "Q8": {
            "description": "Count delays by line (more than 10 minutes late)",
            "sql": """
                SELECT t.line_name, COUNT(se.stop_name) as delay_count
                FROM stop_events se
                JOIN trips t ON se.trip_id = t.trip_id
                WHERE se.actual > se.scheduled + interval '10 minutes'
                GROUP BY t.line_name
                ORDER BY delay_count DESC;
            """
        },
        "Q9": {
            "description": "Trips with 3+ delayed stops",
            "sql": """
                SELECT trip_id, COUNT(stop_name) as delayed_stop_count
                FROM stop_events
                WHERE actual > scheduled + interval '10 minutes'
                GROUP BY trip_id
                HAVING COUNT(stop_name) >= 3
                ORDER BY delayed_stop_count DESC;
            """
        },
        "Q10": {
            "description": "Stops with above-average ridership",
            "sql": """
                WITH StopTotals AS (
                    SELECT stop_name, SUM(passengers_on) as total_boardings
                    FROM stop_events
                    GROUP BY stop_name
                ),
                OverallAverage AS (
                    SELECT AVG(total_boardings) as avg_boardings
                    FROM StopTotals
                )
                SELECT st.stop_name, st.total_boardings
                FROM StopTotals st, OverallAverage oa
                WHERE st.total_boardings > oa.avg_boardings
                ORDER BY st.total_boardings DESC;
            """
        }
    }

    if query_num not in queries:
        return None

    query_data = queries[query_num]
    cur.execute(query_data["sql"])

    rows = cur.fetchall()
    col_names = [desc[0] for desc in cur.description]
    results_list = [dict(zip(col_names, row)) for row in rows]

    output = {
        "query": query_num,
        "description": query_data["description"],
        "results": results_list,
        "count": len(results_list)
    }

    return output

def main():
    parser = argparse.ArgumentParser(description="Query transit database")
    parser.add_argument('query', help='Query to run (e.g., Q1, all)')
    parser.add_argument('--format', choices=['json', 'text'], default='text')

    parser.add_argument('--host', default='db')
    parser.add_argument('--dbname', default='transit')
    parser.add_argument('--user', default='transit')
    parser.add_argument('--password', default='transit123')

    args = parser.parse_args()

    try:
        conn = psycopg2.connect(
            host=args.host, dbname=args.dbname, user=args.user, password=args.password
        )

        queries_to_run = [f"Q{i}" for i in range(1, 11)] if args.query == 'all' else [args.query]

        all_outputs = []
        for q in queries_to_run:
            output = run_query(conn, q, args.format)
            if output:
                all_outputs.append(output)

        if args.format == 'json':
            print(json.dumps(all_outputs, indent=2, default=json_serial))
        else:
            for out in all_outputs:
                print(f"--- {out['query']}: {out['description']} ---")
                for row in out['results']:
                    print(row)
                print(f"Count: {out['count']}\n")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    main()
