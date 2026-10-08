from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models.database import init_db
from app.routers import portfolio, trades, market, analysis, training

app = FastAPI(title="NexusTrade API", version="1.0.0", description="AI-Powered Stock Trading Simulator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(portfolio.router)
app.include_router(trades.router)
app.include_router(market.router)
app.include_router(analysis.router)
app.include_router(training.router)


@app.on_event("startup")
async def startup():
    init_db()
    # Optional: schedule weekly model retraining
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from app.models.database import SessionLocal
        from app.services.training_service import train_model

        scheduler = AsyncIOScheduler()

        def weekly_retrain():
            db = SessionLocal()
            try:
                result = train_model(db)
                import logging
                logging.getLogger(__name__).info(f"Weekly retrain: {result}")
            finally:
                db.close()

        scheduler.add_job(weekly_retrain, "cron", day_of_week="sun", hour=2, minute=0)
        scheduler.start()
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Scheduler not started: {e}")


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
