import os,uuid,time,logging
from datetime import datetime,timezone
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI,HTTPException
from sqlalchemy import create_engine,MetaData,Table,Column,String,JSON,Text,Integer,DateTime,select,update
from app.schemas import ForecastRequest
from app.agent import forecast
load_dotenv()
metadata=MetaData()
logs=Table('forecast_logs',metadata,Column('request_id',String(36),primary_key=True),Column('request_payload',JSON,nullable=False),Column('response_payload',JSON),Column('status',String(20),nullable=False),Column('error_message',Text),Column('execution_time_ms',Integer),Column('created_at',DateTime,nullable=False))
@asynccontextmanager
async def lifespan(app):
    engine=create_engine(os.environ['MYSQL_URL'],pool_pre_ping=True)
    metadata.create_all(engine); app.state.engine=engine
    yield
    engine.dispose()
app=FastAPI(title='TCS Financial Forecasting Agent',lifespan=lifespan)
@app.get('/health')
def health():
    with app.state.engine.connect() as c: c.execute(select(1))
    return {'status':'ok'}
@app.post('/api/v1/forecast')
def run(req:ForecastRequest):
    rid=str(uuid.uuid4()); start=time.monotonic(); engine=app.state.engine
    with engine.begin() as c: c.execute(logs.insert().values(request_id=rid,request_payload=req.model_dump(),status='running',created_at=datetime.now(timezone.utc).replace(tzinfo=None)))
    try:
        result={'request_id':rid,'status':'success',**forecast(req)}
    except Exception as e:
        logging.exception('Forecast failed: %s',rid)
        with engine.begin() as c: c.execute(update(logs).where(logs.c.request_id==rid).values(status='failed',error_message=type(e).__name__,execution_time_ms=int((time.monotonic()-start)*1000)))
        raise HTTPException(502,detail={'request_id':rid,'message':'Forecast failed; inspect server logs'}) from e
    with engine.begin() as c: c.execute(update(logs).where(logs.c.request_id==rid).values(status='success',response_payload=result,execution_time_ms=int((time.monotonic()-start)*1000)))
    return result
@app.get('/api/v1/forecasts/{request_id}')
def get_forecast(request_id:str):
    with app.state.engine.connect() as c: row=c.execute(select(logs).where(logs.c.request_id==request_id)).mappings().first()
    if not row: raise HTTPException(404,'Not found')
    return dict(row)
