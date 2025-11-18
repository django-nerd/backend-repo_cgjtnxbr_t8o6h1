import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

from database import db, create_document, get_documents
from schemas import User, Product, Portfolio, Order, Strategy, AnalysisRequest, AnalysisInsight

app = FastAPI(title="KSA Trading API", description="Trading, mutual funds, and algo-trading backend for the Saudi market")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "KSA Trading Backend Running"}

# --- Health & Schema ---
@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

@app.get("/schema")
def get_schema():
    """Return schemas so the DB viewer can introspect collections"""
    return {
        "user": User.model_json_schema(),
        "product": Product.model_json_schema(),
        "portfolio": Portfolio.model_json_schema(),
        "order": Order.model_json_schema(),
        "strategy": Strategy.model_json_schema(),
        "analysisrequest": AnalysisRequest.model_json_schema(),
        "analysisinsight": AnalysisInsight.model_json_schema(),
    }

# --- Portfolio Endpoints ---
@app.post("/api/portfolio", response_model=dict)
def create_portfolio(payload: Portfolio):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    inserted_id = create_document("portfolio", payload)
    return {"id": inserted_id}

@app.get("/api/portfolio", response_model=List[Dict[str, Any]])
def list_portfolios(limit: int = 20):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    docs = get_documents("portfolio", {}, limit)
    # Convert ObjectId to string if present
    for d in docs:
        if "_id" in d:
            d["_id"] = str(d["_id"])
    return docs

# --- Orders ---
@app.post("/api/orders", response_model=dict)
def place_order(order: Order):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    order_id = create_document("order", order)
    return {"id": order_id, "status": "received"}

@app.get("/api/orders", response_model=List[Dict[str, Any]])
def list_orders(limit: int = 50):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    docs = get_documents("order", {}, limit)
    for d in docs:
        if "_id" in d:
            d["_id"] = str(d["_id"])
    return docs

# --- Strategies ---
@app.post("/api/strategies", response_model=dict)
def create_strategy(strategy: Strategy):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    sid = create_document("strategy", strategy)
    return {"id": sid}

@app.get("/api/strategies", response_model=List[Dict[str, Any]])
def list_strategies(limit: int = 50):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    docs = get_documents("strategy", {}, limit)
    for d in docs:
        if "_id" in d:
            d["_id"] = str(d["_id"])
    return docs

# --- AI Analysis (mocked analytics) ---
# In real usage, you'd integrate with market data & an ML model.
@app.post("/api/analysis", response_model=List[AnalysisInsight])
def analyze(request: AnalysisRequest):
    # Simple, deterministic pseudo-analysis for demo
    insights: List[AnalysisInsight] = []
    for sym in request.symbols:
        # toy calculations
        rsi = (sum(ord(c) for c in sym) % 100) * 0.9
        sma_14 = 50 + (len(sym) * 2)
        signal = "buy" if rsi < 30 else ("sell" if rsi > 70 else "hold")
        if request.language == "ar":
            summary = f"تحليل {sym}: مؤشر القوة النسبية {rsi:.1f}، متوسط متحرك 14 يوم {sma_14:.1f}. التوصية: { 'شراء' if signal=='buy' else ('بيع' if signal=='sell' else 'احتفاظ') }."
        else:
            summary = f"{sym} analysis: RSI {rsi:.1f}, 14-day SMA {sma_14:.1f}. Recommendation: {signal}."
        insights.append(AnalysisInsight(symbol=sym, rsi=rsi, sma_14=sma_14, signal=signal, summary=summary))
    return insights

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
