
import sys
import asyncio
import json
from unittest.mock import MagicMock

# MOCK EVERYTHING before importing services
sys.modules["faster_whisper"] = MagicMock()
sys.modules["fpdf"] = MagicMock()
sys.modules["duckduckgo_search"] = MagicMock()
sys.modules["sqlalchemy"] = MagicMock()
sys.modules["sqlalchemy.orm"] = MagicMock()
sys.modules["sqlalchemy.ext.declarative"] = MagicMock()
sys.modules["fastapi"] = MagicMock()
sys.modules["pydantic"] = MagicMock()

# Mock models.py effectively
models_mock = MagicMock()
sys.modules["models"] = models_mock

# Now we can import things from services
# We need to make sure OllamaService is importable
# services.py imports: json, requests, asyncio, ... faster_whisper, models, fpdf, duckduckgo_search

import services
from services import OllamaService

async def run_test():
    print("Setting up test...")
    service = OllamaService()
    
    # Mock internal methods
    service._get_model_name = MagicMock()
    f = asyncio.Future()
    f.set_result("mock-model")
    service._get_model_name.return_value = f
    
    # Mock requests
    services.requests = MagicMock()
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"response": "{}"}
    mock_resp.raise_for_status = MagicMock()
    services.requests.post.return_value = mock_resp
    
    # Test Data
    large_image_data = "data:image/jpeg;base64," + "X" * 50000
    recipe = {
        "title": "Test Recipe",
        "description": "Desc",
        "ingredients": ["1"],
        "steps": ["2"],
        "image_data": large_image_data
    }
    
    print("Calling edit_recipe_with_instruction...")
    result = await service.edit_recipe_with_instruction(recipe, "make it better")
    
    # Verify
    args, kwargs = services.requests.post.call_args
    payload = kwargs.get("json", {})
    prompt = payload.get("prompt", "")
    
    print(f"Prompt length: {len(prompt)}")
    
    if "X" * 50000 in prompt:
        print("❌ FAIL: Image data detected in prompt!")
    else:
        print("✅ PASS: Image data NOT found in prompt.")

    # Check result preservation
    if result.get("image_data") == large_image_data:
        print("✅ PASS: Image data preserved in result.")
    else:
        print("❌ FAIL: Image data LOST in result!")

if __name__ == "__main__":
    asyncio.run(run_test())
