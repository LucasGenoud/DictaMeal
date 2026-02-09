import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
    baseURL: API_URL,
});

export default {
    transcribe(file) {
        const formData = new FormData();
        formData.append('file', file);
        return api.post('/transcribe', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            },
            timeout: 300000 // 5 minutes
        });
    },
    structure(text, useSearch = false) {
        return api.post('/structure', { text, use_search: useSearch });
    },
    createRecipe(recipe) {
        return api.post('/recipes', recipe);
    },
    listRecipes() {
        return api.get('/recipes');
    },
    getRecipe(id) {
        return api.get(`/recipes/${id}`);
    },
    updateRecipe(id, recipe) {
        return api.put(`/recipes/${id}`, recipe);
    },
    deleteRecipe(id) {
        return api.delete(`/recipes/${id}`);
    },
    getRecipePdfUrl(id) {
        return `${API_URL}/recipes/${id}/pdf`;
    },
    updateRecipeWithInstruction(recipe, instruction) {
        return api.post('/structure/edit_instruction', { recipe, instruction });
    }
};
