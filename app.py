"""
1688 Sourcing Tool — Web Application & API Entry Point.
Built with FastAPI to deliver a browser interface and REST API.
"""

import json
import uvicorn
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import config
from search_engine import SourcingSearchEngine
from exporter import SourcingDataExporter
from adapters import get_adapter

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="1688 Sourcing Tool",
    description="Alibaba/1688 supplier sourcing tool to find factories and evaluate multi-product coverage.",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

search_engine = SourcingSearchEngine()


class SingleSearchRequest(BaseModel):
    product: str
    factory_only: bool = False


class MultiSearchRequest(BaseModel):
    products: Optional[List[str]] = []
    products_text: Optional[str] = None


class ToggleModeRequest(BaseModel):
    demo_mode: bool


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Frontend index.html not found.")
    with open(index_file, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/api/status")
async def get_status():
    config.reload()
    return config.get_public_status()


@app.post("/api/config/reload")
async def reload_configuration():
    config.reload()
    return {
        "status": "reloaded",
        "config": config.get_public_status()
    }


@app.post("/api/config/toggle-mode", response_class=HTMLResponse)
async def toggle_demo_mode(payload: ToggleModeRequest):
    config.set_demo_mode(payload.demo_mode)
    return {
        "status": "updated",
        "config": config.get_public_status()
    }


@app.post("/api/provider/test")
async def test_provider_connection():
    config.reload()
    adapter = get_adapter()
    return adapter.test_connection()


@app.post("/api/search/single")
async def search_single(payload: SingleSearchRequest):
    product = payload.product.strip()
    if not product:
        raise HTTPException(status_code=400, detail="Product name is required.")
    
    try:
        return search_engine.search_single_product(product, factory_only=payload.factory_only)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.post("/api/search/multi")
async def search_multi(payload: MultiSearchRequest):
    products_list = payload.products or []
    if payload.products_text:
        lines = [line.strip() for line in payload.products_text.splitlines() if line.strip()]
        products_list.extend(lines)

    if not products_list:
        raise HTTPException(status_code=400, detail="At least one product is required.")

    try:
        return search_engine.search_multi_products(products_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multi-product search failed: {str(e)}")


def _extract_export_data(data_str: Optional[str], json_body: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if data_str:
        try:
            return json.loads(data_str)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON data provided in form.")
    if json_body:
        return json_body
    raise HTTPException(status_code=400, detail="No export payload provided.")


@app.post("/api/export/single/excel")
async def export_single_excel(request: Request, data: Optional[str] = Form(None)):
    json_body = None
    if not data:
        try:
            json_body = await request.json()
        except Exception:
            pass
    
    payload = _extract_export_data(data, json_body)
    query_slug = payload.get("query", "results").replace(" ", "_")[:30]
    excel_stream = SourcingDataExporter.export_single_to_excel(payload)
    
    return Response(
        content=excel_stream.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="1688_Sourcing_{query_slug}.xlsx"'}
    )


@app.post("/api/export/single/csv")
async def export_single_csv(request: Request, data: Optional[str] = Form(None)):
    json_body = None
    if not data:
        try:
            json_body = await request.json()
        except Exception:
            pass
    
    payload = _extract_export_data(data, json_body)
    query_slug = payload.get("query", "results").replace(" ", "_")[:30]
    csv_stream = SourcingDataExporter.export_single_to_csv(payload)
    
    return Response(
        content=csv_stream.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="1688_Sourcing_{query_slug}.csv"'}
    )


@app.post("/api/export/multi/excel")
async def export_multi_excel(request: Request, data: Optional[str] = Form(None)):
    json_body = None
    if not data:
        try:
            json_body = await request.json()
        except Exception:
            pass
    
    payload = _extract_export_data(data, json_body)
    excel_stream = SourcingDataExporter.export_multi_to_excel(payload)
    
    return Response(
        content=excel_stream.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="1688_Multi_Product_Coverage.xlsx"'}
    )


@app.post("/api/export/multi/csv")
async def export_multi_csv(request: Request, data: Optional[str] = Form(None)):
    json_body = None
    if not data:
        try:
            json_body = await request.json()
        except Exception:
            pass
    
    payload = _extract_export_data(data, json_body)
    csv_stream = SourcingDataExporter.export_multi_to_csv(payload)
    
    return Response(
        content=csv_stream.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="1688_Multi_Product_Coverage.csv"'}
    )


if __name__ == "__main__":
    print(f"Starting 1688 Sourcing Tool on http://{config.host}:{config.port}")
    uvicorn.run("app:app", host=config.host, port=config.port, reload=False)