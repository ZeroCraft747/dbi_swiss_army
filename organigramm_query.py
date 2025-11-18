import mysql.connector
from mysql.connector import Error

# ==================== KONFIGURATION ====================
config = {
    'host': 'marian',           # oder IP/Docker-Name
    'user': 'root',
    'password': 'deinPasswort123',
    'database': 'military_database'
}

# SVG-Einstellungen
SVG_WIDTH = 1600
SVG_HEIGHT = 1000
NODE_WIDTH = 220
NODE_HEIGHT = 60
HORIZONTAL_SPACING = 280   # Abstand zwischen Ebenen
VERTICAL_SPACING = 100     # Abstand zwischen Geschwisterknoten

# Farben pro Ebene (militärisch angehaucht)
LEVEL_COLORS = [
    "#1f4e79",  # Ebene 0 (Oberkommando) – Dunkelblau
    "#2e74b5",
    "#5b9bd5",
    "#a6bce2",
    "#c5d5ea",
    "#e2f0f8"
]

# ==================== DATENBANK ====================
def connect_db():
    try:
        conn = mysql.connector.connect(**config)
        if conn.is_connected():
            print("✓ Erfolgreich mit MySQL verbunden!")
            return conn
    except Error as e:
        print(f"✗ Fehler bei der Verbindung: {e}")
    return None

def fetch_hierarchy(conn):
    cursor = conn.cursor(dictionary=True)
    query = """
    WITH RECURSIVE hierarchy AS (
        SELECT id, name, typ, ebene, uebergeordnete_einheit_id,
               CAST(name AS CHAR(500)) AS sort_name
        FROM einheiten
        WHERE uebergeordnete_einheit_id IS NULL

        UNION ALL

        SELECT e.id, e.name, e.typ, e.ebene, e.uebergeordnete_einheit_id,
               CONCAT(h.sort_name, ' → ', e.name)
        FROM einheiten e
        INNER JOIN hierarchy h ON e.uebergeordnete_einheit_id = h.id
    )
    SELECT id, name, typ, ebene, uebergeordnete_einheit_id
    FROM hierarchy
    ORDER BY ebene, sort_name;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    return rows

# ==================== SVG GENERATOR ====================
class OrgChartSVG:
    def __init__(self):
        self.nodes = {}      # id → dict mit Koordinaten und Daten
        self.lines = []
        self.max_level = 0

    def build_tree(self, rows):
        # Kinder sammeln
        children = {}
        root = None
        for row in rows:
            pid = row['uebergeordnete_einheit_id']
            children.setdefault(pid, []).append(row)
            if pid is None:
                root = row

        # Rekursiv Positionen berechnen
        self._place_node(root, 0, 0, children)
        return root

    def _place_node(self, node, level, order, children_dict):
        self.max_level = max(self.max_level, level)

        # Position berechnen (Mitte der Geschwister)
        siblings = children_dict.get(node['uebergeordnete_einheit_id'] if level > 0 else None, [])
        idx = siblings.index(node)
        total = len(siblings)

        y = 100 + (order * VERTICAL_SPACING)
        if total > 1:
            y = 100 + VERTICAL_SPACING * (idx - (total-1)/2) * 1.2

        x = 150 + level * HORIZONTAL_SPACING

        self.nodes[node['id']] = {
            'x': x,
            'y': y,
            'data': node,
            'level': level
        }

        # Kinder rekursiv platzieren
        child_list = children_dict.get(node['id'], [])
        for i, child in enumerate(child_list):
            self._place_node(child, level + 1, i, children_dict)

            # Verbindungslinie speichern
            self.lines.append((node['id'], child['id']))

    def generate_svg(self, filename="military.svg"):
        svg_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg width="{SVG_WIDTH}" height="{SVG_HEIGHT}" xmlns="http://www.w3.org/2000/svg" style="background:#f8f9fa">',
            '  <defs>',
            '    <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">',
            '      <path d="M0,0 L0,6 L9,3 z" fill="#666"/>',
            '    </marker>',
            '  </defs>',
            '  <g font-family="Arial, Helvetica, sans-serif">'
        ]

        # Linien zuerst (damit sie unter den Kästen sind)
        for parent_id, child_id in self.lines:
            px = self.nodes[parent_id]['x'] + NODE_WIDTH
            py = self.nodes[parent_id]['y'] + NODE_HEIGHT // 2
            cx = self.nodes[child_id]['x']
            cy = self.nodes[child_id]['y'] + NODE_HEIGHT // 2

            # Horizontale Linie + Vertikale
            svg_lines.append(f'    <polyline points="{px},{py} {px+50},{py} {cx-20},{cy}" '
                             f'stroke="#666" stroke-width="2" fill="none" marker-end="url(#arrow)"/>')

        # Knoten (Rechtecke + Text)
        for node_id, info in self.nodes.items():
            x = info['x']
            y = info['y']
            data = info['data']
            level = info['level']
            color = LEVEL_COLORS[level % len(LEVEL_COLORS)]

            display_text = f"{data['name']} ({data['typ']})"

            # Rechteck
            svg_lines.append(f'    <rect x="{x}" y="{y}" width="{NODE_WIDTH}" height="{NODE_HEIGHT}" '
                             f'rx="8" fill="{color}" stroke="#333" stroke-width="2"/>')

            # Text (zwei Zeilen)
            svg_lines.append(f'    <text x="{x + NODE_WIDTH//2}" y="{y + 22}" text-anchor="middle" '
                             f'fill="white" font-weight="bold" font-size="14">{data["name"]}</text>')
            svg_lines.append(f'    <text x="{x + NODE_WIDTH//2}" y="{y + 42}" text-anchor="middle" '
                             f'fill="#eee" font-size="12">{data["typ"]} | ID: {data["id"]}</text>')

        svg_lines.append('  </g>')
        # Titel
        svg_lines.append(f'  <text x="{SVG_WIDTH//2}" y="40" text-anchor="middle" font-size="24" font-weight="bold" fill="#1f4e79">')
        svg_lines.append('    Militärisches Organigramm')
        svg_lines.append('  </text>')
        svg_lines.append('</svg>')

        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(svg_lines))

        print(f"✓ Organigramm erfolgreich als '{filename}' gespeichert! (Größe: {SVG_WIDTH}x{SVG_HEIGHT})")

# ==================== HAUPTPROGRAMM ====================
def main():
    conn = connect_db()
    if not conn:
        return

    rows = fetch_hierarchy(conn)
    conn.close()

    if not rows:
        print("✗ Keine Einheiten in der Datenbank gefunden.")
        return

    print(f"✓ {len(rows)} Einheiten geladen. Generiere SVG...")

    chart = OrgChartSVG()
    chart.build_tree(rows)
    chart.generate_svg("military.svg")

    print("\nFertig! Öffne die Datei 'military.svg' in deinem Browser oder Viewer.")

if __name__ == "__main__":
    main()