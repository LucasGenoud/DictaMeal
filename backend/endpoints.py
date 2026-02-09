from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Response
from pydantic import BaseModel
from typing import List, Optional
from services import WhisperService, OllamaService, RecipeService
from models import RecipeCreate, RecipeUpdate, Recipe

router = APIRouter()
whisper_service = WhisperService()
ollama_service = OllamaService()
recipe_service = RecipeService()

@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        text = await whisper_service.transcribe(file)
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class StructureRequest(BaseModel):
    text: str
    use_search: bool = False

@router.post("/structure")
async def structure_recipe(request: StructureRequest):
    try:
        structured_data = await ollama_service.structure_recipe(request.text, request.use_search)
        return structured_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class RecipeInstructionRequest(BaseModel):
    recipe: dict
    instruction: str

@router.post("/structure/edit_instruction")
async def edit_recipe_instruction(request: RecipeInstructionRequest):
    try:
        updated_recipe = await ollama_service.edit_recipe_with_instruction(request.recipe, request.instruction)
        return updated_recipe
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recipes", response_model=Recipe)
def create_recipe(recipe: RecipeCreate):
    return recipe_service.create_recipe(recipe)

@router.get("/recipes", response_model=List[Recipe])
def list_recipes():
    return recipe_service.list_recipes()

@router.get("/recipes/{recipe_id}", response_model=Recipe)
def get_recipe(recipe_id: int):
    recipe = recipe_service.get_recipe(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe

@router.put("/recipes/{recipe_id}", response_model=Recipe)
def update_recipe(recipe_id: int, recipe: RecipeUpdate):
    updated = recipe_service.update_recipe(recipe_id, recipe)
    if not updated:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return updated

@router.delete("/recipes/{recipe_id}")
def delete_recipe(recipe_id: int):
    success = recipe_service.delete_recipe(recipe_id)
    if not success:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return {"status": "deleted"}

@router.get("/recipes/{recipe_id}/pdf")
def get_recipe_pdf(recipe_id: int):
    pdf_content = recipe_service.generate_pdf(recipe_id)
    if not pdf_content:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    return Response(content=pdf_content, media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename=recipe_{recipe_id}.pdf"
    })
