from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from fastapi.responses import JSONResponse
from db import *
import uvicorn

app = FastAPI()

class Recipe(BaseModel):
    title: str
    making_time: str
    serves: str
    ingredients: str
    cost: int
    created_at: datetime
    updated_at: datetime

class RecipeUpdate(BaseModel):
    title: Optional[str]
    making_time: Optional[str]
    serves: Optional[str]
    ingredients: Optional[str]
    cost: Optional[int]

@app.post("/recipes")
def insert_data(recipe: Recipe):
    try:
        recipe_id = create_recipe(recipe)
        response = {
            "message": "Recipe successfully created!",
            "recipe": [
                {
                    "id": str(recipe_id),
                    "title": recipe.title,
                    "making_time": recipe.making_time,
                    "serves": recipe.serves,
                    "ingredients": recipe.ingredients,
                    "cost": str(recipe.cost),
                    "created_at": recipe.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at": recipe.updated_at.strftime("%Y-%m-%d %H:%M:%S")
                }
            ]
        }
        return response
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "message": "Recipe creation failed!",
                "required": "title, making_time, serves, ingredients, cost"
            }
        )

@app.get("/recipes")
def get_recipes():
    try:
        recipes = fetch_recipes()
        response = {
            "recipes": [
                {
                    "id": recipe["id"],
                    "title": recipe["title"],
                    "making_time": recipe["making_time"],
                    "serves": recipe["serves"],
                    "ingredients": recipe["ingredients"],
                    "cost": str(recipe["cost"])
                }
                for recipe in recipes
            ]
        }
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

@app.get("/recipes/{id}")
def get_recipe_by_id(id: int):
    try:
        recipe = fetch_recipe_by_id(id)
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        response = {
            "message": "Recipe details by id",
            "recipe": [
                {
                    "id": recipe["id"],
                    "title": recipe["title"],
                    "making_time": recipe["making_time"],
                    "serves": recipe["serves"],
                    "ingredients": recipe["ingredients"],
                    "cost": str(recipe["cost"])
                }
            ]
        }
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

@app.patch("/recipes/{id}")
def update_recipe(id: int, recipe: RecipeUpdate):
    try:
        updated_recipe = update_recipe_in_db(id, recipe)
        response = {
            "message": "Recipe successfully updated!",
            "recipe": [
                {
                    "title": updated_recipe[0],
                    "making_time": updated_recipe[1],
                    "serves": updated_recipe[2],
                    "ingredients": updated_recipe[3],
                    "cost": str(updated_recipe[4])
                }
            ]
        }
        return JSONResponse(content=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")




@app.delete("/recipes/{id}")
def delete_recipe(id):
    try:
        recipe_id = int(id)
        response= delete_recipe_by_id(recipe_id)
        # response = {"message": "Recipe successfully removed!"}
        return JSONResponse(content=response)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")