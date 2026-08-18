"""
SQLite database for Clean Chem Intel.

Stores products, ingredients, and their analysis results.
"""
import sqlite3
from pathlib import Path
from typing import Optional

from .models import Ingredient, ProductAnalysis, Grade, EvidenceLevel


DB_PATH = Path(__file__).resolve().parents[2] / "data" / "clean_chem.db"


SCHEMA = """
CREATE TABLE IF NOT EXISTS ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    cas_number TEXT,
    pubchem_cid INTEGER,
    ghs_hazard TEXT,
    summary TEXT,
    respiratory_impact TEXT,
    dermal_impact TEXT,
    endocrine_impact TEXT,
    organ_toxicity TEXT,
    environmental_impact TEXT,
    worker_safety TEXT,
    sensitive_occupant_flag INTEGER DEFAULT 0,
    evidence_confidence TEXT DEFAULT 'Low',
    is_volatile INTEGER DEFAULT 0,
    is_sensitizer INTEGER DEFAULT 0,
    is_penetration_enhancer INTEGER DEFAULT 0,
    is_surfactant INTEGER DEFAULT 0,
    is_biodegradable INTEGER,
    is_aquatic_toxic INTEGER
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    brand TEXT,
    category TEXT,
    notes TEXT,
    overall_grade TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS product_ingredients (
    product_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    raw_name TEXT,
    PRIMARY KEY (product_id, ingredient_id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id)
);
"""


def init_db(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Initialize the database with schema. Returns a connection."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


def upsert_ingredient(conn: sqlite3.Connection, ingredient: Ingredient) -> int:
    """Insert or update an ingredient. Returns the ingredient ID."""
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO ingredients (
            name, cas_number, pubchem_cid, ghs_hazard, summary,
            respiratory_impact, dermal_impact, endocrine_impact,
            organ_toxicity, environmental_impact, worker_safety,
            sensitive_occupant_flag, evidence_confidence,
            is_volatile, is_sensitizer, is_penetration_enhancer,
            is_surfactant, is_biodegradable, is_aquatic_toxic
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
            cas_number=excluded.cas_number,
            pubchem_cid=excluded.pubchem_cid,
            ghs_hazard=excluded.ghs_hazard,
            summary=excluded.summary
        """,
        (
            ingredient.name,
            ingredient.cas_number,
            ingredient.pubchem_cid,
            ingredient.ghs_hazard,
            ingredient.summary,
            ingredient.respiratory_impact.value if ingredient.respiratory_impact else None,
            ingredient.dermal_impact.value if ingredient.dermal_impact else None,
            ingredient.endocrine_impact.value if ingredient.endocrine_impact else None,
            ingredient.organ_toxicity.value if ingredient.organ_toxicity else None,
            ingredient.environmental_impact.value if ingredient.environmental_impact else None,
            ingredient.worker_safety.value if ingredient.worker_safety else None,
            int(ingredient.sensitive_occupant_flag),
            ingredient.evidence_confidence.value if ingredient.evidence_confidence else "Low",
            int(ingredient.is_volatile),
            int(ingredient.is_sensitizer),
            int(ingredient.is_penetration_enhancer),
            int(ingredient.is_surfactant),
            int(ingredient.is_biodegradable) if ingredient.is_biodegradable is not None else None,
            int(ingredient.is_aquatic_toxic) if ingredient.is_aquatic_toxic is not None else None,
        )
    )
    conn.commit()
    return cursor.lastrowid


def insert_product(conn: sqlite3.Connection, name: str, brand: str = None,
                   category: str = None, notes: str = None) -> int:
    """Insert a product. Returns the product ID."""
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (name, brand, category, notes) VALUES (?, ?, ?, ?)",
        (name, brand, category, notes)
    )
    conn.commit()
    return cursor.lastrowid


def link_product_ingredient(conn: sqlite3.Connection, product_id: int,
                            ingredient_id: int, position: int, raw_name: str = None):
    """Link a product to an ingredient at a given position in the ingredient list."""
    conn.execute(
        "INSERT OR REPLACE INTO product_ingredients (product_id, ingredient_id, position, raw_name) VALUES (?, ?, ?, ?)",
        (product_id, ingredient_id, position, raw_name)
    )
    conn.commit()


def get_ingredient_by_name(conn: sqlite3.Connection, name: str) -> Optional[Ingredient]:
    """Look up an ingredient by name (case-insensitive)."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ingredients WHERE lower(name) = lower(?)", (name,))
    row = cursor.fetchone()
    if not row:
        return None
    return _row_to_ingredient(row)


def _row_to_ingredient(row) -> Ingredient:
    """Convert a database row to an Ingredient object."""
    return Ingredient(
        name=row[1],
        cas_number=row[2],
        pubchem_cid=row[3],
        ghs_hazard=row[4],
        summary=row[5],
        respiratory_impact=Grade(row[6]) if row[6] else None,
        dermal_impact=Grade(row[7]) if row[7] else None,
        endocrine_impact=Grade(row[8]) if row[8] else None,
        organ_toxicity=Grade(row[9]) if row[9] else None,
        environmental_impact=Grade(row[10]) if row[10] else None,
        worker_safety=Grade(row[11]) if row[11] else None,
        sensitive_occupant_flag=bool(row[12]),
        evidence_confidence=EvidenceLevel(row[13]) if row[13] else EvidenceLevel.LOW,
        is_volatile=bool(row[14]),
        is_sensitizer=bool(row[15]),
        is_penetration_enhancer=bool(row[16]),
        is_surfactant=bool(row[17]),
        is_biodegradable=bool(row[18]) if row[18] is not None else None,
        is_aquatic_toxic=bool(row[19]) if row[19] is not None else None,
    )
