from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import os

# 1. Cấu hình kết nối PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://lab05:lab05pass@postgres-db:5432/iotdb")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. Định nghĩa cấu trúc bảng trong Database
class SensorData(Base):
    __tablename__ = "sensor_data"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True)
    temperature = Column(Float)
    humidity = Column(Float)

# Tự động tạo bảng nếu chưa có
Base.metadata.create_all(bind=engine)

app = FastAPI(title="IoT Ingestion API - Team 9")

# 3. Schema nhận dữ liệu từ thiết bị IoT
class SensorReading(BaseModel):
    device_id: str
    temperature: float
    humidity: float

    class Config:
        json_schema_extra = {
            "example": {
                "device_id": "ken-delivery-box-01",
                "temperature": 25.5,
                "humidity": 60.0
            }
        }

# Dependency để lấy database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "iot-api"}

@app.post("/api/v1/sensors/data")
def receive_sensor_data(reading: SensorReading, db: Session = Depends(get_db)):
    try:
        db_data = SensorData(**reading.model_dump())
        db.add(db_data)
        db.commit()
        db.refresh(db_data)
        return {"status": "success", "data": db_data}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))