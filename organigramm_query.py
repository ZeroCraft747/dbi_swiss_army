import mysql.connector
from mysql.connector import Error

# Konfiguration (passe an deine MySQL-Instanz an)
config = {
    'host': 'localhost',  # Oder deine IP
    'user': 'root',       # Dein MySQL-User
    'password': 'dein_passwort',  # Dein Passwort
    'database': 'military_database'
}

def connect_db():
    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            print("Erfolgreich mit MySQL verbunden!")
            return connection
    except Error as e:
        print(f"Fehler bei der Verbindung: {e}")
        return None

def fetch_hierarchy(connection):
    cursor = connection.cursor(dictionary=True)
    # Rekursive CTE für Hierarchie (MySQL 8+)
    query = """
    WITH RECURSIVE hierarchy AS (
        SELECT id, name, typ, ebene, uebergeordnete_einheit_id, CONCAT(name, ' (', typ, ')') as display
        FROM einheiten
        WHERE uebergeordnete_einheit_id IS NULL
        UNION ALL
        SELECT e.id, e.name, e.typ, e.ebene, e.uebergeordnete_einheit_id, 
               CONCAT(e.name, ' (', e.typ, ')') as display
        FROM einheiten e
        INNER JOIN hierarchy h ON e.uebergeordnete_einheit_id = h.id
    )
    SELECT * FROM hierarchy ORDER BY ebene, id;
    """
    cursor.execute(query)
    return cursor.fetchall()

def print_tree(hierarchy, parent_id=None, level=0):
    prefix = "  " * level
    for item in hierarchy:
        if item['uebergeordnete_einheit_id'] == parent_id:
            print(f"{prefix}- {item['display']} (Ebene {item['ebene']}, ID {item['id']})")
            print_tree(hierarchy, item['id'], level + 1)

def main():
    conn = connect_db()
    if conn:
        hierarchy = fetch_hierarchy(conn)
        print("\nOrganigramm (hierarchischer Baum):")
        print_tree(hierarchy)
        conn.close()
    else:
        print("Keine Verbindung – überprüfe config!")

if __name__ == "__main__":
    main()