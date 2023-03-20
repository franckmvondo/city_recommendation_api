#/usr/bin/env python3
# coding: utf-8


from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def Home() -> dict:
    return {"Home": "Hello World"}


@app.get("/cities_recommendation/")
async def cities_recommendation(
    department_code: str, 
    area: float, 
    rent: float) -> dict:
    return {"Home": "Hello World"}