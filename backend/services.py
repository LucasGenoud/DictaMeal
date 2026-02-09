import json
import requests
import asyncio
from typing import List, Optional
from faster_whisper import WhisperModel
import os
from models import SessionLocal, RecipeDB, RecipeCreate, RecipeUpdate, engine, Base
from fpdf import FPDF
from duckduckgo_search import DDGS

# Init DB
def init_db():
    Base.metadata.create_all(bind=engine)

class WhisperService:
    def __init__(self):
        # Use a small model for speed/cpu compatibility by default, can be configured
        self.model_size = "tiny" 
        # In production/docker, might want to download model at build time or volume mount
        self.model = None

    def _get_model(self):
        if not self.model:
            self.model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
        return self.model

    async def transcribe(self, file_obj):
        # Save temp file
        temp_filename = f"temp_{file_obj.filename}"
        with open(temp_filename, "wb") as buffer:
            buffer.write(await file_obj.read())
        
        try:
            model = self._get_model()
            # Run blocking transcription in a thread
            segments, info = await asyncio.to_thread(model.transcribe, temp_filename, beam_size=5)
            text = " ".join([segment.text for segment in segments])
            return text
        finally:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)

class OllamaService:
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")

    async def _get_model_name(self):
        env_model = os.getenv("OLLAMA_MODEL")
        if env_model:
            print(f"Using configured OLLAMA_MODEL: {env_model}")
            return env_model

        try:
            response = requests.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            data = response.json()
            models = [m['name'] for m in data.get('models', [])]
            
            # Preference list
            for preferred in ["llama3.2", "llama3", "mistral", "qwen", "gemma"]:
                for model in models:
                    if preferred in model:
                        return model
            
            # Fallback to first available or default
            return models[0] if models else "llama3"
        except Exception as e:
            print(f"Failed to fetch models: {e}")
            return "llama3"

    def _search_recipe(self, query: str):
        print(f"Searching web for recipe: {query}")
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=3))
                if results:
                    return "\\n\\n".join([f"Title: {r['title']}\\nBody: {r['body']}" for r in results])
        except Exception as e:
            print(f"Search failed: {e}")
        return None

    async def structure_recipe(self, text: str, use_search: bool = False):
        model_name = await self._get_model_name()
        print(f"Using Ollama model: {model_name}")

        search_context = ""
        if use_search:
            print("Web search requested. Searching...")
            # Use the first 50 chars as query if text is long, or the whole text
            query = text[:100].replace("\n", " ") 
            search_results = self._search_recipe(f"recipe for {query}")
            if search_results:
                 print("Found search results.")
                 search_context = f"""
                 I have searched the web and found the following details which you MUST use to construct the recipe:
                 
                 {search_results}
                 """

        prompt = f"""
        You are a smart recipe assistant. Your goal is to extract structured recipe data from the raw text provided below.
        {search_context}
        
        Instructions:
        1. Analyze the text to identify the recipe name, ingredients, instructions, and context.
        2. Return ONLY a raw JSON object. Do NOT use markdown code blocks (```json). Do NOT add any conversational text.
        
        The JSON object must have these exact keys:
        - "title": The name of the recipe.
        - "description": A short summary of the dish, focusing on its origin or backstory.
        - "ingredients": A list of strings, where each string is an ingredient with its quantity. IMPORTANT: Convert ALL units to METRIC (g, kg, ml, l). Do NOT use imperial units (oz, lb, cups).
        - "steps": A list of strings, representing the sequential cooking instructions. Ensure all temperatures are in Celsius.
        - "duration": The estimated cooking time (e.g., "45 minutes"). Infer if not explicitly stated.
        - "origin": The cuisine or country of origin (e.g., "Italian", "Thai"). Infer if not explicitly stated.
        - "meal_type": The category of meal (e.g., "Dinner", "Dessert"). Infer if not explicitly stated.
        
        Raw Text:
        "{text}"
        """
        
        payload = {
            "model": model_name,
            "prompt": prompt,
            "format": "json",
            "stream": False
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/generate", json=payload)
            response.raise_for_status()
            result = response.json()
            print(f"DEBUG: Full Ollama response: {result}")
            
            raw_response = result.get("response", "")
            if not raw_response:
                raw_response = result.get("thinking", "")

            print(f"DEBUG: Ollama raw response: {raw_response}")

            # Clean up potential markdown code blocks and find JSON
            clean_response = raw_response.strip()
            if "```json" in clean_response:
                clean_response = clean_response.split("```json")[1].split("```")[0].strip()
            elif "```" in clean_response:
                 clean_response = clean_response.split("```")[1].split("```")[0].strip()
            
            # Locate the first '{' and last '}'
            start = clean_response.find("{")
            end = clean_response.rfind("}")
            if start != -1 and end != -1:
                clean_response = clean_response[start:end+1]
            
            if not clean_response:
                 raise ValueError("Empty or invalid response from Ollama")

            return json.loads(clean_response)
        except Exception as e:
            print(f"Ollama error: {e}")
            import traceback
            traceback.print_exc()
            try:
                raw_response = locals().get("raw_response", "N/A")
            except:
                raw_response = "N/A"
            # Fallback mock for testing if offline or error
            return {
                "title": "Error/Mock Recipe",
                "description": f"Ollama error: {str(e)}. Raw: {raw_response[:200]}",
                "ingredients": [],
                "steps": [],
                "duration": "N/A",
                "origin": "N/A",
                "meal_type": "N/A"
            }

    async def edit_recipe_with_instruction(self, current_recipe: dict, instruction: str):
        model_name = await self._get_model_name()
        print(f"Using Ollama model: {model_name}")

        # Create a copy of the recipe to modify for the prompt
        recipe_for_prompt = current_recipe.copy()
        # Remove heavy image data from the prompt
        if "image_data" in recipe_for_prompt:
            del recipe_for_prompt["image_data"]

        prompt = f"""
        You are a smart recipe assistant. Your goal is to modify an existing recipe based on the user's instruction.
        
        Instructions:
        1. Read the existing recipe JSON and the user's instruction.
        2. Modify the recipe fields according to the instruction.
        3. Return ONLY the modified raw JSON object. Do NOT use markdown code blocks.
        
        Existing Recipe:
        {json.dumps(recipe_for_prompt, indent=2)}
        
        User Instruction:
        "{instruction}"
        
        The JSON object must keep the exact same structure as the input:
        - "title"
        - "description"
        - "ingredients" (list of strings, use METRIC units)
        - "steps" (list of strings, ensure temperatures are Celsius)
        - "duration"
        - "origin"
        - "meal_type"
        """
        
        # Define the JSON schema for structured output
        recipe_schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "ingredients": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "steps": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "duration": {"type": "string"},
                "origin": {"type": "string"},
                "meal_type": {"type": "string"}
            },
            "required": ["title", "description", "ingredients", "steps", "duration", "origin", "meal_type"]
        }
        
        payload = {
            "model": model_name,
            "prompt": prompt,
            "format": recipe_schema,
            "stream": False
        }

        
        try:
            response = requests.post(f"{self.base_url}/api/generate", json=payload)
            response.raise_for_status()
            result = response.json()
            print(f"DEBUG: Full Ollama response: {result}")
            
            raw_response = result.get("response", "")
            if not raw_response:
                raw_response = result.get("thinking", "")

            print(f"DEBUG: Ollama raw response: {raw_response}")

            # Clean up potential markdown code blocks and find JSON
            clean_response = raw_response.strip()
            if "```json" in clean_response:
                clean_response = clean_response.split("```json")[1].split("```")[0].strip()
            elif "```" in clean_response:
                 clean_response = clean_response.split("```")[1].split("```")[0].strip()
            
            # Locate the first '{' and last '}'
            start = clean_response.find("{")
            end = clean_response.rfind("}")
            if start != -1 and end != -1:
                clean_response = clean_response[start:end+1]
            
            if not clean_response:
                 raise ValueError("Empty or invalid response from Ollama")

            result_recipe = json.loads(clean_response)

            # Validate required fields
            required_fields = ["title", "ingredients", "steps"]
            for field in required_fields:
                if field not in result_recipe:
                    raise ValueError(f"LLM response missing required field: {field}")
            
            # Validate types
            if not isinstance(result_recipe.get("ingredients"), list):
                raise ValueError("LLM response 'ingredients' must be a list")
            if not isinstance(result_recipe.get("steps"), list):
                raise ValueError("LLM response 'steps' must be a list")
            
            # Validate non-empty content
            if len(result_recipe["ingredients"]) == 0:
                raise ValueError("LLM response returned empty ingredients list")
            if len(result_recipe["steps"]) == 0:
                raise ValueError("LLM response returned empty steps list")

            # Restore preserved fields
            if "image_data" in current_recipe:
                result_recipe["image_data"] = current_recipe["image_data"]
            if "id" in current_recipe and "id" not in result_recipe:
                result_recipe["id"] = current_recipe["id"]
            
            return result_recipe
        except Exception as e:
            print(f"Ollama error: {e}")
            import traceback
            traceback.print_exc()
            # Fallback/Error
            raise e

class RecipeService:
    def get_db(self):
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def create_recipe(self, recipe: RecipeCreate):
        db = SessionLocal()
        db_recipe = RecipeDB(
            title=recipe.title,
            description=recipe.description,
            ingredients=json.dumps(recipe.ingredients),
            steps=json.dumps(recipe.steps),
            duration=recipe.duration,
            origin=recipe.origin,
            meal_type=recipe.meal_type,
            original_transcription=recipe.original_transcription,
            image_data=recipe.image_data
        )
        db.add(db_recipe)
        db.commit()
        db.refresh(db_recipe)
        db.close()
        return self._map_to_schema(db_recipe)

    def list_recipes(self):
        db = SessionLocal()
        recipes = db.query(RecipeDB).all()
        db.close()
        return [self._map_to_schema(r) for r in recipes]

    def get_recipe(self, recipe_id: int):
        db = SessionLocal()
        recipe = db.query(RecipeDB).filter(RecipeDB.id == recipe_id).first()
        db.close()
        if recipe:
            return self._map_to_schema(recipe)
        return None

    def update_recipe(self, recipe_id: int, recipe_update: RecipeUpdate):
        db = SessionLocal()
        db_recipe = db.query(RecipeDB).filter(RecipeDB.id == recipe_id).first()
        if db_recipe:
            db_recipe.title = recipe_update.title
            db_recipe.description = recipe_update.description
            db_recipe.ingredients = json.dumps(recipe_update.ingredients)
            db_recipe.steps = json.dumps(recipe_update.steps)
            db_recipe.duration = recipe_update.duration
            db_recipe.origin = recipe_update.origin
            db_recipe.meal_type = recipe_update.meal_type
            db_recipe.original_transcription = recipe_update.original_transcription
            db_recipe.image_data = recipe_update.image_data
            db.commit()
            db.refresh(db_recipe)
            db.close()
            return self._map_to_schema(db_recipe)
        db.close()
        return None

    def delete_recipe(self, recipe_id: int):
        db = SessionLocal()
        db_recipe = db.query(RecipeDB).filter(RecipeDB.id == recipe_id).first()
        if db_recipe:
            db.delete(db_recipe)
            db.commit()
            db.close()
            return True
        db.close()
        return False

    def generate_pdf(self, recipe_id: int):
        recipe = self.get_recipe(recipe_id)
        if not recipe:
            return None
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, recipe["title"], ln=True, align="C")
        
        pdf.set_font("Arial", "", 12)
        if recipe["description"]:
            pdf.multi_cell(0, 10, recipe["description"])
            pdf.ln(5)
            
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Ingredients", ln=True)
        pdf.set_font("Arial", "", 12)
        for ingredient in recipe["ingredients"]:
            pdf.cell(0, 10, f"- {ingredient}", ln=True)
            
        pdf.ln(5)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Steps", ln=True)
        pdf.set_font("Arial", "", 12)
        for i, step in enumerate(recipe["steps"], 1):
             pdf.multi_cell(0, 10, f"{i}. {step}")
             pdf.ln(2)

        pdf_path = f"recipe_{recipe_id}.pdf"
        # In a real app, save to a temp dir or byte stream.
        # For this MVP, we will return the bytes directly if using streaming response, 
        # or save to a known path. let's return the binary content.
        return pdf.output(dest='S').encode('latin-1')

    def _map_to_schema(self, db_recipe):
        return {
            "id": db_recipe.id,
            "title": db_recipe.title,
            "description": db_recipe.description,
            "ingredients": json.loads(db_recipe.ingredients) if db_recipe.ingredients else [],
            "steps": json.loads(db_recipe.steps) if db_recipe.steps else [],
            "duration": db_recipe.duration,
            "origin": db_recipe.origin,
            "meal_type": db_recipe.meal_type,
            "original_transcription": db_recipe.original_transcription,
            "image_data": db_recipe.image_data
        }
