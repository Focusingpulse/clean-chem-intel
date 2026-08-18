"""
Data models for Clean Chem Intel.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Grade(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"


class EvidenceLevel(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    EXTRAPOLATED = "Extrapolated"


@dataclass
class Ingredient:
    name: str
    cas_number: Optional[str] = None
    pubchem_cid: Optional[int] = None
    ghs_hazard: Optional[str] = None
    summary: Optional[str] = None
    # Scoring dimensions
    disclosure_quality: Optional[Grade] = None
    respiratory_impact: Optional[Grade] = None
    dermal_impact: Optional[Grade] = None
    endocrine_impact: Optional[Grade] = None
    organ_toxicity: Optional[Grade] = None
    environmental_impact: Optional[Grade] = None
    worker_safety: Optional[Grade] = None
    sensitive_occupant_flag: bool = False
    evidence_confidence: EvidenceLevel = EvidenceLevel.LOW
    # Chemical property flags for interaction rules
    is_volatile: bool = False
    is_sensitizer: bool = False
    is_penetration_enhancer: bool = False
    is_surfactant: bool = False
    is_biodegradable: Optional[bool] = None
    is_aquatic_toxic: Optional[bool] = None


@dataclass
class InteractionFlag:
    flag: str
    trigger: str
    concern: str
    ingredients: list[str] = field(default_factory=list)


@dataclass
class ProductAnalysis:
    product_name: str
    ingredients: list[Ingredient] = field(default_factory=list)
    interaction_flags: list[InteractionFlag] = field(default_factory=list)
    overall_grade: Optional[Grade] = None
    notes: list[str] = field(default_factory=list)
