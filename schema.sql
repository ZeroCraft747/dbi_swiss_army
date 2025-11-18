CREATE DATABASE military_database CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

CREATE USER 'marian'@'%' IDENTIFIED BY 'deinPasswort123';

GRANT ALL PRIVILEGES ON military_database.* TO 'marian'@'%';

FLUSH PRIVILEGES;

USE military_database;
SET FOREIGN_KEY_CHECKS = 0;


DROP TABLE IF EXISTS kommandostrukturen;
DROP TABLE IF EXISTS positionen;
DROP TABLE IF EXISTS personen;
DROP TABLE IF EXISTS einheiten;
DROP TABLE IF EXISTS dienstgrade;

SET FOREIGN_KEY_CHECKS = 1;



-- Tabelle: Dienstgrade
CREATE TABLE dienstgrade (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rang VARCHAR(50) NOT NULL UNIQUE,
    kategorie VARCHAR(30) NOT NULL,
    rang_nr INT NOT NULL
) ENGINE=InnoDB;

-- Tabelle: Einheiten (selbstreferenziell)
CREATE TABLE einheiten (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    typ VARCHAR(50) NOT NULL,
    ebene INT NOT NULL,
    uebergeordnete_einheit_id INT NULL,
    standort VARCHAR(100),
    FOREIGN KEY (uebergeordnete_einheit_id) REFERENCES einheiten(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Tabelle: Personen
CREATE TABLE personen (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vorname VARCHAR(50) NOT NULL,
    nachname VARCHAR(50) NOT NULL,
    dienstgrad_id INT NOT NULL,
    aktiv BOOLEAN DEFAULT 1,
    FOREIGN KEY (dienstgrad_id) REFERENCES dienstgrade(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Tabelle: Positionen
CREATE TABLE positionen (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bezeichnung VARCHAR(100) NOT NULL,
    einheit_id INT NOT NULL,
    person_id INT NULL,
    von_datum DATE,
    bis_datum DATE,
    ist_kommandant BOOLEAN DEFAULT 0,
    FOREIGN KEY (einheit_id) REFERENCES einheiten(id) ON DELETE CASCADE,
    FOREIGN KEY (person_id) REFERENCES personen(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Tabelle: Kommandostrukturen
CREATE TABLE kommandostrukturen (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vorgesetzte_position_id INT NOT NULL,
    untergebene_position_id INT NOT NULL,
    beziehungstyp VARCHAR(50) DEFAULT 'direkt',
    FOREIGN KEY (vorgesetzte_position_id) REFERENCES positionen(id) ON DELETE CASCADE,
    FOREIGN KEY (untergebene_position_id) REFERENCES positionen(id) ON DELETE CASCADE
) ENGINE=InnoDB;


CREATE INDEX idx_einheiten_ebene ON einheiten(ebene);
CREATE INDEX idx_einheiten_uebergeordnet ON einheiten(uebergeordnete_einheit_id);
CREATE INDEX idx_positionen_einheit ON positionen(einheit_id);
CREATE INDEX idx_positionen_person ON positionen(person_id);
CREATE INDEX idx_kommando_vorgesetzt ON kommandostrukturen(vorgesetzte_position_id);
CREATE INDEX idx_kommando_untergeordnet ON kommandostrukturen(untergebene_position_id);



-- Dienstgrade
INSERT INTO dienstgrade (rang, kategorie, rang_nr) VALUES
('General', 'Höhere Stabsoffiziere', 1),
('Korpskommandant', 'Höhere Stabsoffiziere', 2),
('Divisionär', 'Höhere Stabsoffiziere', 3),
('Brigadier', 'Höhere Stabsoffiziere', 4),
('Oberst i Gst', 'Stabsoffiziere', 5),
('Oberstleutnant i Gst', 'Stabsoffiziere', 6),
('Major', 'Stabsoffiziere', 7),
('Hauptmann', 'Subalternoffiziere', 8),
('Oberleutnant', 'Subalternoffiziere', 9),
('Leutnant', 'Subalternoffiziere', 10);

-- Einheitenhierarchie
INSERT INTO einheiten (name, typ, ebene, uebergeordnete_einheit_id, standort) VALUES
('Schweizer Armee', 'Oberkommando', 1, NULL, 'Bern'),
('Höheres Kommando der Armee', 'Kommando', 2, 1, 'Bern'),
('Kommando Ausbildung', 'Kommando', 2, 1, 'Luzern'),
('Kommando Operationen', 'Kommando', 2, 1, 'Bern'),
('Logistikbasis der Armee', 'Basis', 2, 1, 'Bern'),
('Territorialdivision 1', 'Division', 3, 3, 'Morges'),
('Territorialdivision 2', 'Division', 3, 3, 'Emmen'),
('Territorialdivision 3', 'Division', 3, 3, 'Zürich'),
('Territorialdivision 4', 'Division', 3, 3, 'Airolo'),
('Panzerbrigade 11', 'Brigade', 3, 3, 'Bremgarten'),
('Infanteriebrigade 1', 'Brigade', 3, 3, 'Chamblon'),
('Infanteriebrigade 2', 'Brigade', 3, 3, 'Kriens'),
('Gebirgsbrigade 12', 'Brigade', 3, 3, 'Andermatt'),
('Luftwaffe', 'Teilstreitkraft', 3, 1, 'Dübendorf'),
('Führungsunterstützungsbrigade 41', 'Brigade', 3, 3, 'Fribourg'),
('Panzerbataillon 12', 'Bataillon', 4, 10, 'Thun'),
('Panzerbataillon 14', 'Bataillon', 4, 10, 'Bremgarten'),
('Infanteriebataillon 56', 'Bataillon', 4, 11, 'Chamblon'),
('Infanteriebataillon 61', 'Bataillon', 4, 12, 'Kriens'),
('Gebirgsinfanteriebataillon 91', 'Bataillon', 4, 13, 'Andermatt'),
('Artilleriebataillon 10', 'Bataillon', 4, 11, 'Bière'),
('Aufklärungsbataillon 1', 'Bataillon', 4, 10, 'Drognens');

-- Personen
INSERT INTO personen (vorname, nachname, dienstgrad_id, aktiv) VALUES
('Thomas', 'Süssli', 1, 1),
('Peter', 'Müller', 2, 1),
('Hans', 'Meier', 3, 1),
('Fritz', 'Schmidt', 4, 1),
('Karl', 'Weber', 4, 1),
('Andreas', 'Fischer', 5, 1),
('Martin', 'Keller', 6, 1),
('Stefan', 'Bauer', 7, 1),
('Michael', 'Schneider', 8, 1),
('Daniel', 'Huber', 9, 1);

-- Positionen
INSERT INTO positionen (bezeichnung, einheit_id, person_id, von_datum, ist_kommandant) VALUES
('Chef der Armee', 1, 1, '2020-01-01', 1),
('Chef Höheres Kommando', 2, 2, '2021-03-01', 1),
('Kommandant Territorialdivision 1', 6, 3, '2022-01-01', 1),
('Kommandant Panzerbrigade 11', 10, 4, '2021-06-01', 1),
('Kommandant Infanteriebrigade 1', 11, 5, '2022-03-01', 1),
('Stabschef Panzerbrigade 11', 10, 6, '2021-06-01', 0),
('Kommandant Panzerbataillon 12', 16, 7, '2023-01-01', 1),
('Kommandant Infanteriebataillon 56', 18, 8, '2023-01-01', 1),
('S3 Operations', 16, 9, '2023-01-01', 0),
('Adjutant', 16, 10, '2023-01-01', 0);

-- Kommandostrukturen
INSERT INTO kommandostrukturen (vorgesetzte_position_id, untergebene_position_id, beziehungstyp) VALUES
(1, 2, 'direkt'),
(2, 3, 'direkt'),
(3, 4, 'direkt'),
(3, 5, 'direkt'),
(4, 6, 'stab'),
(4, 7, 'direkt'),
(5, 8, 'direkt'),
(7, 9, 'stab'),
(7, 10, 'stab');

