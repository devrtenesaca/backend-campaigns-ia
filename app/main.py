from fastapi import FastAPI
from app.config.settings import get_settings
from app.presentation.api.routers import campaign_contacts, campaigns, auth, users

def _load_all_models() -> None:
    # Importaciones por efecto colateral: registran los mappers en Base.metadata
    import app.infrastructure.db.users                 
    import app.infrastructure.db.refresh_tokens        
    import app.infrastructure.db.revoked_access_tokens  
    import app.infrastructure.db.callbot_campaign_types      
    import app.infrastructure.db.callbot_campaigns                
    import app.infrastructure.db.callbot_campaign_contacts                 
    from sqlalchemy.orm import configure_mappers
    configure_mappers()

# Carga los modelos ANTES de crear la app / montar routers / abrir sesiones
_load_all_models()

settings = get_settings()
app = FastAPI(title=settings.APP_NAME)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(campaigns.router)
app.include_router(campaign_contacts.router)

@app.get("/")
def root():
    return {"app": settings.APP_NAME, "env": settings.APP_ENV}
