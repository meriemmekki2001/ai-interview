from pydantic import BaseModel
from typing import List, Optional, Dict, Literal


class BoardMember(BaseModel):
    name: str
    role: str
    independence: Optional[Literal["Independent", "Executive", "Non-Independent"]] = None


class BoardInfo(BaseModel):
    chair: Optional[BoardMember] = None
    members: List[BoardMember] = []
    counts: Optional[Dict[str, int]] = None


class GHG(BaseModel):
    base_year: Optional[int] = None
    scope1_tco2e: Optional[float] = None
    scope2_market_tco2e: Optional[float] = None
    scope2_location_tco2e: Optional[float] = None
    scope3_tco2e: Optional[float] = None
    total_tco2e: Optional[float] = None
    intensity_tco2e_per_eur_m: Optional[float] = None


class Policies(BaseModel):
    anti_corruption: Optional[bool] = None
    whistleblowing: Optional[bool] = None
    human_rights: Optional[bool] = None
    climate_policy: Optional[bool] = None
    dei_policy: Optional[bool] = None
    assurance: Optional[str] = None


class DocESG(BaseModel):
    company: Optional[str] = None
    year: Optional[int] = None
    board: Optional[BoardInfo] = None
    ghg: Optional[GHG] = None
    policies: Optional[Policies] = None
    governance: Optional[dict] = None
