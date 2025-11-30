"""
Routes da API com Neon Postgres
"""
from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from database import execute_query
from schemas import Event, EventCreate, EventUpdate, Rating, RatingCreate

router = APIRouter()

# ============================================
# EVENTOS
# ============================================

@router.post("/events", response_model=Event, status_code=status.HTTP_201_CREATED, tags=["Events"])
async def create_event(event_data: EventCreate):
    """Cria um novo evento"""
    # Query atualizada com ecommerce_link
    query = """
        INSERT INTO events (image, alt, title, date, date_event, year, 
                          description, button_text, event_name, cities, active_event, ecommerce_link)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING *
    """
    params = (
        event_data.image, event_data.alt, event_data.title, event_data.date,
        event_data.date_event, event_data.year, event_data.description,
        event_data.buttonText, event_data.eventName, event_data.cities,
        event_data.active_event, event_data.ecommerce_link
    )
    
    try:
        result = execute_query(query, params, fetch="one")
        if not result:
            raise HTTPException(status_code=400, detail="Erro ao criar evento")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no banco: {str(e)}")


@router.get("/events", response_model=List[Event], tags=["Events"])
async def get_events(
    active_only: bool = Query(True, description="Filtrar apenas eventos ativos"),
    year: Optional[str] = Query(None, description="Filtrar por ano"),
    month: Optional[int] = Query(None, description="Filtrar por mês (1-12)"),
    limit: int = Query(100, le=500, description="Limite de resultados")
):
    """Lista eventos com filtros"""
    query = "SELECT * FROM events WHERE 1=1"
    params = []
    
    if active_only:
        query += " AND active_event = TRUE"
    
    if year:
        query += " AND year = %s"
        params.append(year)
    
    if month:
        query += " AND EXTRACT(MONTH FROM date_event) = %s"
        params.append(month)
    
    query += " ORDER BY date_event ASC LIMIT %s"
    params.append(limit)
    
    try:
        results = execute_query(query, tuple(params), fetch="all")
        return results or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events/upcoming", response_model=List[Event], tags=["Events"])
async def get_upcoming_events(limit: int = Query(10, le=50)):
    """Retorna próximos eventos"""
    query = """
        SELECT * FROM events 
        WHERE active_event = TRUE 
        AND date_event >= CURRENT_DATE
        ORDER BY date_event ASC 
        LIMIT %s
    """
    
    try:
        results = execute_query(query, (limit,), fetch="all")
        return results or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events/{event_id}", response_model=Event, tags=["Events"])
async def get_event_by_id(event_id: int):
    """Busca evento por ID"""
    query = "SELECT * FROM events WHERE id = %s"
    
    try:
        result = execute_query(query, (event_id,), fetch="one")
        if not result:
            raise HTTPException(status_code=404, detail=f"Evento {event_id} não encontrado")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/events/{event_id}", response_model=Event, tags=["Events"])
async def update_event(event_id: int, event_update: EventUpdate):
    """Atualiza um evento"""
    update_data = event_update.model_dump(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
    
    field_mapping = {
        'buttonText': 'button_text',
        'eventName': 'event_name',
        'active_event': 'active_event',
        'date_event': 'date_event',
        'ecommerce_link': 'ecommerce_link' # Mapeamento novo
    }
    
    set_clauses = []
    params = []
    
    for key, value in update_data.items():
        db_field = field_mapping.get(key, key)
        set_clauses.append(f"{db_field} = %s")
        params.append(value)
    
    params.append(event_id)
    
    query = f"""
        UPDATE events 
        SET {', '.join(set_clauses)}
        WHERE id = %s
        RETURNING *
    """
    
    try:
        result = execute_query(query, tuple(params), fetch="one")
        if not result:
            raise HTTPException(status_code=404, detail=f"Evento {event_id} não encontrado")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Events"])
async def delete_event(event_id: int):
    """Deleta um evento (soft delete)"""
    query = "UPDATE events SET active_event = FALSE WHERE id = %s RETURNING id"
    
    try:
        result = execute_query(query, (event_id,), fetch="one")
        if not result:
            raise HTTPException(status_code=404, detail=f"Evento {event_id} não encontrado")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ... Rotas de Ratings permanecem iguais ...
@router.post("/ratings", response_model=Rating, status_code=status.HTTP_201_CREATED, tags=["Ratings"])
async def create_rating(rating_data: RatingCreate):
    query = """
        INSERT INTO ratings (event_name, reviewer_name, score, comment)
        VALUES (%s, %s, %s, %s)
        RETURNING *
    """
    params = (rating_data.event_name, rating_data.reviewer_name, rating_data.score, rating_data.comment)
    try:
        result = execute_query(query, params, fetch="one")
        if not result: raise HTTPException(status_code=400, detail="Erro ao criar avaliação")
        return result
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@router.get("/ratings", response_model=List[Rating], tags=["Ratings"])
async def get_all_ratings(limit: int = Query(100, le=500)):
    query = "SELECT * FROM ratings ORDER BY created_at DESC LIMIT %s"
    try:
        results = execute_query(query, (limit,), fetch="all")
        return results or []
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@router.get("/ratings/event/{event_name}", response_model=List[Rating], tags=["Ratings"])
async def get_ratings_by_event(event_name: str):
    query = "SELECT * FROM ratings WHERE event_name = %s ORDER BY created_at DESC"
    try:
        results = execute_query(query, (event_name,), fetch="all")
        return results or []
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@router.get("/ratings/stats/{event_name}", tags=["Ratings"])
async def get_rating_stats(event_name: str):
    query = """
        SELECT COUNT(*) as total_ratings, AVG(score) as avg_rating, MAX(score) as max_rating, MIN(score) as min_rating
        FROM ratings WHERE event_name = %s
    """
    try:
        result = execute_query(query, (event_name,), fetch="one")
        if not result or result['total_ratings'] == 0:
            return {"event_name": event_name, "total_ratings": 0, "avg_rating": 0, "max_rating": 0, "min_rating": 0}
        return {"event_name": event_name, **result}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))