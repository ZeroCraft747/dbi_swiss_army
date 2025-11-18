# Schweizer Armee Organigramm Generator

Dieses Projekt erstellt ein hierarchisches Organigramm der Schweizer Armee basierend auf einer MySQL-Datenbank mit Entity-Relationship-Modell (ERM).

## 📋 Projektübersicht

Das Projekt modelliert die vollständige hierarchische Struktur der Schweizer Armee und ermöglicht die Abfrage und Visualisierung der Kommandostrukturen über alle Ebenen hinweg.

## 📁 Projektstruktur

```
swiss-army-org/
├── README.md                    # Projektdokumentation
├── schema 3.sql                 # MySQL Datenbankschema mit Beispieldaten
└── organigramm_query.py         # Python-Script für hierarchische Abfragen
```

## 🗄️ Datenbankschema

Das ERM modelliert folgende Entitäten:

### Haupttabellen

- **`einheiten`**: Organisationseinheiten der Armee (selbstreferenziell)
  - Hierarchische Struktur über `uebergeordnete_einheit_id`
  - Ebenen 1-4: Oberkommando → Kommando/Division → Brigade → Bataillon
  
- **`dienstgrade`**: Militärische Ränge (General bis Leutnant)
  - Kategorisiert nach: Höhere Stabsoffiziere, Stabsoffiziere, Subalternoffiziere

- **`personen`**: Militärangehörige mit Dienstgrad

- **`positionen`**: Funktionen innerhalb der Hierarchie
  - Verknüpft Personen mit Einheiten
  - Zeitliche Zuordnung (von/bis Datum)
  - Kennzeichnung als Kommandant

- **`kommandostrukturen`**: Befehls- und Stabsbeziehungen
  - Direkte und indirekte Unterstellungsverhältnisse

## 🚀 Installation

### Voraussetzungen

- Python 3.8 oder höher
- MySQL 8.0+ (für rekursive CTEs)
- MySQL Connector für Python

### Setup Schritt-für-Schritt

1. **Repository klonen/Dateien herunterladen**

2. **Python Virtual Environment erstellen**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. **MySQL Connector installieren**
```bash
pip install mysql-connector-python
```

4. **MySQL Datenbank erstellen**
```bash
mysql -u root -p < "schema 3.sql"
```

Die Datenbank `military_database` wird automatisch erstellt und mit Beispieldaten gefüllt.

## ⚙️ Konfiguration

Bearbeite `organigramm_query.py` und passe die Datenbankverbindung an:

```python
config = {
    'host': 'localhost',        # Deine MySQL-Host-Adresse
    'user': 'root',             # Dein MySQL-Benutzername
    'password': 'dein_passwort',# Dein MySQL-Passwort
    'database': 'military_database'
}
```

## 📊 Verwendung

### Organigramm ausgeben

```bash
python organigramm_query.py
```

**Ausgabe-Beispiel:**
```
Erfolgreich mit MySQL verbunden!

Organigramm (hierarchischer Baum):
- Schweizer Armee (Oberkommando) (Ebene 1, ID 1)
  - Höheres Kommando der Armee (Kommando) (Ebene 2, ID 2)
  - Kommando Ausbildung (Kommando) (Ebene 2, ID 3)
    - Territorialdivision 1 (Division) (Ebene 3, ID 6)
    - Panzerbrigade 11 (Brigade) (Ebene 3, ID 10)
      - Panzerbataillon 12 (Bataillon) (Ebene 4, ID 16)
      - Panzerbataillon 14 (Bataillon) (Ebene 4, ID 17)
    ...
```

### Funktionsweise

Das Script nutzt eine **rekursive CTE (Common Table Expression)**, um die gesamte Hierarchie von der obersten Ebene (Schweizer Armee) bis zu den Bataillonen zu traversieren und baumartig darzustellen.

## 🔧 Anpassungen und Erweiterungen

### Eigene Daten hinzufügen

Neue Einheiten direkt in die Datenbank einfügen:

```sql
USE military_database;

INSERT INTO einheiten (name, typ, ebene, uebergeordnete_einheit_id, standort) 
VALUES ('Panzerbataillon 15', 'Bataillon', 4, 10, 'Zürich');
```

### Weitere Personen und Positionen

```sql
-- Neue Person
INSERT INTO personen (vorname, nachname, dienstgrad_id, aktiv) 
VALUES ('Max', 'Muster', 7, 1);

-- Position zuweisen
INSERT INTO positionen (bezeichnung, einheit_id, person_id, von_datum, ist_kommandant) 
VALUES ('Kommandant Panzerbataillon 15', 23, 11, '2024-01-01', 1);
```

### Script erweitern

Mögliche Erweiterungen für `organigramm_query.py`:

- Export als JSON oder XML
- Filterung nach bestimmten Ebenen
- Suche nach spezifischen Einheiten
- Visualisierung mit Graphviz oder Matplotlib

## 📈 Datenmodell-Details

### Hierarchie-Ebenen

| Ebene | Typ | Beispiele |
|-------|-----|-----------|
| 1 | Oberkommando | Schweizer Armee |
| 2 | Kommando/Basis | Höheres Kommando, Logistikbasis |
| 3 | Division/Brigade | Territorialdivision, Panzerbrigade |
| 4 | Bataillon | Panzerbataillon, Infanteriebataillon |

### Beziehungstypen

- **direkt**: Unmittelbare Kommandogewalt
- **stab**: Stabsposition ohne direkte Kommandogewalt

## 🛠️ Technische Details

- **Sprache**: Python 3.8+
- **Datenbank**: MySQL 8.0+ (UTF-8 mb4)
- **Libraries**: 
  - `mysql-connector-python`: Datenbankverbindung
- **Features**:
  - Rekursive Hierarchieabfragen mit CTEs
  - Selbstreferenzielle Tabellenstruktur
  - Foreign Key Constraints für Datenintegrität

## 📚 Beispieldaten

Die Datenbank enthält:
- **22 Einheiten** (vom Oberkommando bis zu Bataillonen)
- **10 Dienstgrade** (General bis Leutnant)
- **10 Personen** mit aktiven Positionen
- **10 Positionen** inkl. Chef der Armee
- **9 Kommandostrukturen**

## 🔍 Häufige Probleme

### Verbindungsfehler
```
Fehler bei der Verbindung: Access denied for user 'root'@'localhost'
```
**Lösung**: Überprüfe Benutzername und Passwort in der `config`

### Encoding-Probleme
Die Datenbank nutzt UTF-8 mb4. Bei Anzeigeproblemen:
```python
connection = mysql.connector.connect(**config, charset='utf8mb4')
```

### Rekursive CTE nicht verfügbar
**Voraussetzung**: MySQL 8.0 oder höher. Prüfe Version mit:
```bash
mysql --version
```

## 📝 Lizenz

Dieses Projekt dient zu Bildungszwecken.

## 👥 Autoren

WH & MA 4.11 Projekt

## 📌 Hinweise

Die Struktur basiert auf der Organisation der Schweizer Armee (Stand 2024). Die Daten sind vereinfacht und dienen als Beispiel für die Modellierung militärischer Hierarchien.

---

**Stand**: November 2024