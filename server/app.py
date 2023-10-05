from fastapi import FastAPI, Query
from pymongo import MongoClient

app = FastAPI()

client = MongoClient("mongodb://root:example@localhost:27017/")
db = client["bdd_gaz"]
collection = db["data_gaz"]

# Récup toutes les données
@app.get("/api/data")
async def get_all_data():
    data = list(collection.find({}, {"_id": 0})) 
    return data

# récup les données mais paginées
@app.get("/api/data/paginated")
async def get_paginated_data(skip: int = Query(default=0, description="Nombre d'enregistrements à sauter"),
                              limit: int = Query(default=10, description="Nombre d'enregistrements à récupérer")):
    data = list(collection.find({}).skip(skip).limit(limit))
    return data

# récup les données mais filtrées (pour graphique modulable)
@app.get("/api/data/filter")
async def filter_data():
    data = list(collection.find())
    
    serialized_data = []
    for item in data:
        serialized_item = {
            "_id": str(item["_id"]),
            "date": item["date"],
            "nom_officiel_departement": item["nom_officiel_departement"],
            "code_officiel_departement": item["code_officiel_departement"],
            "igrm": item["igrm"],
        }
        serialized_data.append(serialized_item)

    return serialized_data