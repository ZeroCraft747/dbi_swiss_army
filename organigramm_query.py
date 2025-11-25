# organigramm_query.py – Version für 16"-Bildschirm (1920×1080 oder größer)
import mysql.connector
from mysql.connector import Error

config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'mysql',
    'database': 'military_database'
}

# ==================== AUTOMATISCHE SKALIERUNG ====================
BASE_NODE_WIDTH = 210
BASE_NODE_HEIGHT = 65
BASE_H_SPACING = 260      # Horizontaler Abstand zwischen Ebenen
BASE_V_SPACING = 110      # Vertikaler Abstand zwischen Geschwistern

# Dynamische Anpassung je nach Hierarchiegröße
def calculate_dimensions(max_level, total_nodes):
    # Für die Schweizer Armee realistisch: max_level ≈ 5–6, total_nodes ≈ 100–200
    factor = 1.0

    if max_level >= 6 or total_nodes > 120:
        factor = 0.78   # Etwas kompakter
    if total_nodes > 180:
        factor = 0.68   # Noch kompakter bei sehr großen Strukturen

    node_w = int(BASE_NODE_WIDTH * factor)
    node_h = int(BASE_NODE_HEIGHT * factor)
    h_space = int(BASE_H_SPACING * factor)
    v_space = int(BASE_V_SPACING * factor)

    width = 400 + (max_level + 1) * h_space + 200
    height = max(1300, total_nodes * v_space // 4 + 300)   # Mindestens 900px hoch

    # Auf volle Bildschirmgröße begrenzen (16" Laptop = ca. 1920px breit)
    width = min(width, 1900)
    height = min(height, 1300)   # Lässt noch Platz für Browser-Leiste

    return {
        'width': width, 'height': height,
        'node_w': node_w, 'node_h': node_h,
        'h_space': h_space, 'v_space': v_space,
        'font_size_name': int(15 * factor),
        'font_size_typ': int(12 * factor)
    }

# ==================== DATENBANK ====================
def connect_db():
    try:
        conn = mysql.connector.connect(**config, charset='utf8mb4')
        if conn.is_connected():
            print("Erfolgreich mit MySQL verbunden!")
            return conn
    except Error as e:
        print(f"Fehler bei der Verbindung: {e}")
    return None

def fetch_hierarchy(conn):
    cursor = conn.cursor(dictionary=True)
    query = """
    WITH RECURSIVE hierarchy AS (
        SELECT id, name, typ, ebene, uebergeordnete_einheit_id
        FROM einheiten WHERE uebergeordnete_einheit_id IS NULL
        UNION ALL
        SELECT e.id, e.name, e.typ, e.ebene, e.uebergeordnete_einheit_id
        FROM einheiten e
        INNER JOIN hierarchy h ON e.uebergeordnete_einheit_id = h.id
    )
    SELECT id, name, typ, ebene, uebergeordnete_einheit_id
    FROM hierarchy
    ORDER BY ebene, name;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    return rows

# ==================== SVG-GENERATOR (optimiert) ====================
class OrgChartSVG:
    def __init__(self, dim):
        self.dim = dim
        self.nodes = {}
        self.lines = []
        self.max_y = 0

    def build_tree(self, rows):
        children = {}
        root = None
        for row in rows:
            pid = row['uebergeordnete_einheit_id']
            children.setdefault(pid, []).append(row)
            if pid is None:
                root = row

        self._place_node(root, 0, children)
        return root

    def _place_node(self, node, level, children_dict):
        siblings = children_dict.get(node['uebergeordnete_einheit_id'] if level > 0 else None, [])
        idx = siblings.index(node)
        total = len(siblings)

        # Vertikale Position: gleichmäßig verteilt
        if total == 1:
            y_offset = 0
        else:
            y_offset = (idx - (total - 1) / 2) * self.dim['v_space']

        x = 180 + level * self.dim['h_space']
        y = self.dim['height'] // 2 + y_offset

        self.nodes[node['id']] = {
            'x': x, 'y': y, 'data': node, 'level': level
        }
        self.max_y = max(self.max_y, abs(y_offset))

        # Kinder rekursiv
        child_list = children_dict.get(node['id'], [])
        for child in child_list:
            self._place_node(child, level + 1, children_dict)
            self.lines.append((node['id'], child['id']))

    def generate_svg(self, filename="military.svg"):
        d = self.dim
        svg = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg width="{d["width"]}" height="{d["height"]}" xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 {d["width"]} {d["height"]}" style="background:#f8f9fa; font-family: Arial, sans-serif;">',
            '  <defs>',
            '    <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">',
            '      <path d="M0,0 L0,6 L9,3 z" fill="#555"/>',
            '    </marker>',
            '  </defs>',
            f'  <text x="{d["width"]//2}" y="50" text-anchor="middle" font-size="28" font-weight="bold" fill="#1f4e79">',
            '    Schweizer Armee – Organigramm 2025',
            '  </text>'
        ]

        # Linien
        for pid, cid in self.lines:
            p = self.nodes[pid]
            c = self.nodes[cid]
            px = p['x'] + d['node_w']
            py = p['y'] + d['node_h'] // 2
            cx = c['x']
            cy = c['y'] + d['node_h'] // 2
            svg.append(f'    <path d="M{px},{py} H{px + 40} V{cy} H{cx}" '
                       f'stroke="#555" stroke-width="2" fill="none" marker-end="url(#arrow)"/>')

        # Knoten
        colors = ["#1f4e79", "#2e74b5", "#5b9bd5", "#a6bce2", "#c5d5ea", "#e2f0f8"]
        for info in self.nodes.values():
            x, y = info['x'], info['y']
            data = info['data']
            col = colors[data['ebene']-1 % len(colors)]

            display_name = data['name']
            if len(display_name) > 28:
                display_name = display_name[:25] + "..."

            # Box
            svg.append(f'    <rect x="{x}" y="{y}" width="{d["node_w"]}" height="{d["node_h"]}" '
                       f'rx="10" fill="{col}" stroke="#333" stroke-width="2"/>')
            # Name
            svg.append(f'    <text x="{x + d["node_w"]//2}" y="{y + 28}" text-anchor="middle" '
                       f'fill="white" font-weight="bold" font-size="{d["font_size_name"]}">{display_name}</text>')
            # Typ + Ebene
            svg.append(f'    <text x="{x + d["node_w"]//2}" y="{y + 48}" text-anchor="middle" '
                       f'fill="#fff" font-size="{d["font_size_typ"]}">{data["typ"]} (Ebene {data["ebene"]})</text>')

        svg.append('</svg>')

        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(svg))

        print(f"\nOrganigramm gespeichert als '{filename}'")
        print(f"   Größe: {d['width']} × {d['height']} Pixel → passt perfekt auf 16\" Bildschirm!")
        print("   Öffne die Datei einfach im Browser – alles sichtbar ohne Scrollen")

# ==================== MAIN ====================
def main():
    conn = connect_db()
    if not conn:
        return

    rows = fetch_hierarchy(conn)
    conn.close()

    if not rows:
        print("Keine Daten gefunden.")
        return

    max_level = max(r['ebene'] for r in rows)
    total_nodes = len(rows)
    print(f"{total_nodes} Einheiten geladen (max. Ebene {max_level}) – generiere optimales SVG...")

    dim = calculate_dimensions(max_level, total_nodes)
    chart = OrgChartSVG(dim)
    chart.build_tree(rows)
    chart.generate_svg("military.svg")

if __name__ == "__main__":
    main()