"""
Schemas Pydantic para validação
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime, date

# ============================================
# EVENTOS
# ============================================

class EventBase(BaseModel):
    image: str = Field(..., min_length=1)
    alt: str = Field(..., min_length=1)
    title: str = Field(..., min_length=3, max_length=200)
    date: str
    date_event: str
    year: str = Field(..., pattern=r"^\d{4}$")
    description: str = Field(..., min_length=10)
    buttonText: str = Field(default="Reservar Vaga")
    eventName: str = Field(..., min_length=3)
    cities: List[str] = Field(default_factory=list)
    active_event: bool = Field(default=True)
    # NOVO: Link para o Ecommerce
    ecommerce_link: Optional[str] = None
    
    @field_validator('date_event')
    def validate_date_format(cls, v):
        """Valida formato da data"""
        try:
            date.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError('Data deve estar no formato YYYY-MM-DD')
    
    @field_validator('cities')
    def validate_cities(cls, v):
        """Remove cidades vazias"""
        return [city.strip() for city in v if city.strip()]


class EventCreate(EventBase):
    """Schema para criação de evento"""
    pass


class EventUpdate(BaseModel):
    """Schema para atualização parcial"""
    image: Optional[str] = None
    alt: Optional[str] = None
    title: Optional[str] = None
    date: Optional[str] = None
    date_event: Optional[str] = None
    year: Optional[str] = None
    description: Optional[str] = None
    buttonText: Optional[str] = None
    eventName: Optional[str] = None
    cities: Optional[List[str]] = None
    active_event: Optional[bool] = None
    ecommerce_link: Optional[str] = None
    
    @field_validator('date_event')
    def validate_date_format(cls, v):
        if v is not None:
            try:
                date.fromisoformat(v)
                return v
            except ValueError:
                raise ValueError('Data deve estar no formato YYYY-MM-DD')
        return v


class Event(BaseModel):
    """Schema de resposta com ID - mapeia do banco"""
    id: int
    image: str
    alt: str
    title: str
    date: str
    date_event: str
    year: str
    description: str
    buttonText: str = Field(alias='button_text')
    eventName: str = Field(alias='event_name')
    cities: List[str]
    active_event: bool
    # Mapeia o novo campo
    ecommerce_link: Optional[str] = None
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @field_validator('date_event', mode='before')
    def convert_date(cls, v):
        """Converte date object para string"""
        if isinstance(v, date):
            return v.isoformat()
        return v
    
    class Config:
        from_attributes = True
        populate_by_name = True

# ... Ratings permanecem iguais ...
class RatingBase(BaseModel):
    event_name: str = Field(..., min_length=3)
    reviewer_name: str = Field(..., min_length=2, max_length=100)
    score: int = Field(..., ge=0, le=5)
    comment: Optional[str] = Field(None, max_length=1000)
    
    @field_validator('score')
    def validate_score(cls, v):
        if not 0 <= v <= 5:
            raise ValueError('Score deve ser entre 0 e 5')
        return v

class RatingCreate(RatingBase):
    pass

class Rating(BaseModel):
    id: int
    event_name: str
    reviewer_name: str
    score: int
    comment: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
        populate_by_name = True