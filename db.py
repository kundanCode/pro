import mysql.connector
from mysql.connector import errorcode
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import os

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')


def get_db_connection():
    try:
        connection = mysql.connector.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        return connection
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)



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

def create_recipe(recipe):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            insert_query = """
            INSERT INTO recipes (title, making_time, serves, ingredients, cost, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                recipe.title, recipe.making_time, recipe.serves,
                recipe.ingredients, recipe.cost,
                recipe.created_at, recipe.updated_at
            ))
            conn.commit()
            return cursor.lastrowid

def fetch_recipes():
    with get_db_connection() as conn:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT id, title, making_time, serves, ingredients, cost FROM recipes")
            return cursor.fetchall()
            


def fetch_recipe_by_id(id):
    with get_db_connection() as conn:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT id, title, making_time, serves, ingredients, cost FROM recipes WHERE id = %s", (id))
            return cursor.fetchone()

def update_recipe_in_db(id, recipe):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            fields = []
            values = []
            if recipe.title is not None:
                fields.append("title = %s")
                values.append(recipe.title)
            if recipe.making_time is not None:
                fields.append("making_time = %s")
                values.append(recipe.making_time)
            if recipe.serves is not None:
                fields.append("serves = %s")
                values.append(recipe.serves)
            if recipe.ingredients is not None:
                fields.append("ingredients = %s")
                values.append(recipe.ingredients)
            if recipe.cost is not None:
                fields.append("cost = %s")
                values.append(recipe.cost)
            if not fields:
                raise HTTPException(status_code=400, detail="No fields provided for update")
            values.append(id)
            update_query = f"UPDATE recipes SET {', '.join(fields)} WHERE id = %s"
            cursor.execute(update_query, tuple(values))
            conn.commit()
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Recipe not found")
            cursor.execute("SELECT title, making_time, serves, ingredients, cost FROM recipes WHERE id = %s", (id))
            return cursor.fetchone()



def delete_recipe_by_id(recipe_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM recipes WHERE id = %s", (recipe_id,))
        if cursor.rowcount == 0:
            response = {"message": "Recipe not found."}
        else:
            response = {"message": "Recipe successfully removed!"}
        connection.commit()
        return response
    finally:
        cursor.close()
        connection.close()