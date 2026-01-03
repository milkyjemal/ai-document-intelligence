from datetime import date
from typing import List, Optional, Literal

from pydantic import BaseModel, Field, field_validator


# -------------------------
# Shared sub-models
# -------------------------

class Party(BaseModel):
    name: str = Field(..., min_length=1)
    address: Optional[str] = None
    phone: Optional[str] = None


class Location(BaseModel):
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None


class LineItem(BaseModel):
    description: str = Field(..., min_length=1)
    pieces: Optional[int] = Field(None, ge=0)
    weight_lb: Optional[float] = Field(None, ge=0)
    nmfc: Optional[str] = None
    freight_class: Optional[str] = None

    @field_validator("freight_class")
    @classmethod
    def validate_freight_class(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value

        allowed = {
            "50", "55", "60", "65", "70", "77.5",
            "85", "92.5", "100", "110", "125",
            "150", "175", "200", "250", "300",
            "400", "500",
        }

        if value not in allowed:
            raise ValueError(f"invalid freight class: {value}")

        return value


# -------------------------
# Main BOL schema (v1)
# -------------------------

class BolV1(BaseModel):
    # Document
    document_type: Literal["BOL"] = "BOL"
    carrier_name: Optional[str] = None
    bol_number: str = Field(..., min_length=1, max_length=64)
    shipment_date: Optional[date] = None

    # Parties
    shipper: Optional[Party] = None
    consignee: Optional[Party] = None

    # Locations
    origin: Optional[Location] = None
    destination: Optional[Location] = None

    # Freight
    line_items: List[LineItem] = Field(default_factory=list)
    total_pieces: Optional[int] = Field(None, ge=0)
    total_weight_lb: Optional[float] = Field(None, ge=0)

    # References
    po_numbers: List[str] = Field(default_factory=list)
    pro_number: Optional[str] = None
    reference_numbers: List[str] = Field(default_factory=list)

    # Extraction metadata
    confidence: float = Field(..., ge=0.0, le=1.0)
    warnings: List[str] = Field(default_factory=list)

    @field_validator("po_numbers", "reference_numbers")
    @classmethod
    def strip_empty_strings(cls, values: List[str]) -> List[str]:
        return [v.strip() for v in values if v and v.strip()]
