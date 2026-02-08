<template>
  <div class="min-h-screen bg-gray-50 text-gray-900 font-sans selection:bg-indigo-100 selection:text-indigo-700">
    <!-- Navbar -->
    <nav class="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 h-18 flex items-center justify-between">
        <div class="flex items-center gap-3 cursor-pointer group" @click="view = 'list'">
            <div class="bg-gradient-to-br from-indigo-500 to-violet-600 text-white p-2 rounded-xl shadow-lg shadow-indigo-200 group-hover:shadow-indigo-300 transition-all duration-300 transform group-hover:scale-105">
                <BookOpenIcon class="w-6 h-6" />
            </div>
            <span class="text-xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-gray-900 to-gray-600">ChefPrompt</span>
        </div>
        <div class="flex items-center gap-4">
            <button class="p-2 rounded-full hover:bg-gray-100 text-gray-500 transition-colors">
                <span class="sr-only">Settings</span>
                <Cog6ToothIcon class="w-6 h-6" />
            </button>
            <div class="w-10 h-10 rounded-full bg-gradient-to-tr from-indigo-100 to-violet-100 border border-white shadow-sm flex items-center justify-center text-indigo-700 font-bold text-sm ring-2 ring-transparent hover:ring-indigo-100 transition-all cursor-pointer">
                U
            </div>
        </div>
      </div>
    </nav>

    <main class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
        <!-- Notification Toast -->
        <transition
            enter-active-class="transform ease-out duration-300 transition"
            enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2"
            enter-to-class="translate-y-0 opacity-100 sm:translate-x-0"
            leave-active-class="transition ease-in duration-100"
            leave-from-class="opacity-100"
            leave-to-class="opacity-0"
        >
            <div v-if="notification" :class="`fixed bottom-5 right-5 z-50 px-6 py-4 rounded-xl shadow-2xl flex items-center gap-3 border ${notification.type === 'error' ? 'bg-white border-red-100 text-red-700' : 'bg-gray-900 border-gray-800 text-white'}`">
                 <component :is="notification.type === 'error' ? XCircleIcon : CheckCircleIcon" class="w-5 h-5" :class="notification.type === 'error' ? 'text-red-500' : 'text-green-400'" />
                <span class="font-medium text-sm">{{ notification.message }}</span>
            </div>
        </transition>

      <!-- Dashboard View -->
      <section v-if="view === 'list'" class="space-y-8 animate-fade-in">
        <div class="flex flex-col md:flex-row md:items-end justify-between gap-6">
            <div class="space-y-2">
                <h1 class="text-4xl font-extrabold tracking-tight text-gray-900">My Recipes</h1>
                <p class="text-lg text-gray-500 max-w-2xl">Organize your culinary journey. Transcription powered by AI.</p>
            </div>
             <button 
                @click="startNewRecipe"
                class="group relative inline-flex items-center justify-center px-6 py-3 border border-transparent rounded-xl shadow-lg shadow-indigo-200 text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all duration-200 transform hover:-translate-y-0.5"
            >
                <PlusIcon class="-ml-1 mr-2 h-5 w-5 transition-transform group-hover:rotate-90" aria-hidden="true" />
                New Recipe
            </button>
        </div>

        <RecipeList 
            :recipes="recipes" 
            @select="selectRecipe" 
            @create="startNewRecipe"
            @delete="deleteRecipe" 
        />
      </section>

      <!-- Detailed Views (Record/Edit) -->
      <section v-else class="max-w-3xl mx-auto animate-fade-in-up">
        <button 
            @click="view = 'list'"
            class="group mb-8 flex items-center gap-2 text-sm font-medium text-gray-500 hover:text-indigo-600 transition-colors"
        >
            <div class="p-1 rounded-full bg-gray-100 group-hover:bg-indigo-100 transition-colors">
                 <ArrowLeftIcon class="w-4 h-4" />
            </div>
            Back to recipes
        </button>

        <div v-if="view === 'record'" class="bg-white rounded-2xl shadow-xl shadow-gray-100 border border-gray-100 overflow-hidden">
             <div class="p-8 border-b border-gray-50 bg-gradient-to-b from-indigo-50/50 to-white">
                <h2 class="text-2xl font-bold text-gray-900 text-center">Record Recipe</h2>
                <p class="text-gray-500 text-center mt-2">Speak clearly. We'll Transcribe and structure it for you.</p>
            </div>
            <div class="p-8">
                <AudioRecorder @transcribe="handleTranscription" />
            </div>
        </div>
        
        <div v-if="isTranscribing" class="fixed inset-0 bg-white/90 backdrop-blur-sm z-50 flex flex-col items-center justify-center">
            <div class="relative">
                <div class="w-16 h-16 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin"></div>
                <div class="absolute inset-0 flex items-center justify-center">
                    <SparklesIcon class="w-6 h-6 text-indigo-600 animate-pulse" />
                </div>
            </div>
            <h3 class="mt-8 text-xl font-semibold text-gray-900">Transcribing Audio...</h3>
            <p class="text-gray-500 mt-2">Structuring ingredients and steps with AI</p>
        </div>

        <div v-if="view === 'edit' || view === 'transcription_review'">
             <RecipeForm 
                :initial-transcription="currentTranscription"
                :initial-recipe="currentRecipe"
                :mode="view === 'transcription_review' ? 'transcription' : 'edit'"
                @cancel="view = 'list'"
                @structured="handleStructured"
                @save="handleSave"
            />
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { BookOpenIcon, PlusIcon, ArrowLeftIcon, Cog6ToothIcon, CheckCircleIcon, XCircleIcon, SparklesIcon } from '@heroicons/vue/24/solid';
import AudioRecorder from './components/AudioRecorder.vue';
import RecipeList from './components/RecipeList.vue';
import RecipeForm from './components/RecipeForm.vue';
import api from './api';

const view = ref('list'); // 'list', 'record', 'transcription_review', 'edit'
const recipes = ref([]);
const currentTranscription = ref('');
const currentRecipe = ref(null);
const isTranscribing = ref(false);
const notification = ref(null);

const showNotification = (message, type = 'success') => {
    notification.value = { message, type };
    setTimeout(() => notification.value = null, 3000);
};

onMounted(async () => {
    await fetchRecipes();
});

const fetchRecipes = async () => {
    try {
        const res = await api.listRecipes();
        recipes.value = res.data;
    } catch (e) {
        console.error("Failed to fetch recipes", e);
        showNotification("Failed to load recipes", "error");
    }
};

const startNewRecipe = () => {
    currentTranscription.value = '';
    currentRecipe.value = null;
    view.value = 'record';
};

const handleTranscription = async (file) => {
    isTranscribing.value = true;
    try {
        const res = await api.transcribe(file);
        currentTranscription.value = res.data.text;
        view.value = 'transcription_review';
    } catch (e) {
        console.error("Transcription failed", e);
        showNotification("Transcription failed", "error");
    } finally {
        isTranscribing.value = false;
    }
};

const handleStructured = (structuredRecipe) => {
    currentRecipe.value = structuredRecipe;
    view.value = 'edit';
};

const handleSave = async (savedRecipe) => {
    await fetchRecipes();
    view.value = 'list';
    showNotification("Recipe saved successfully!");
};

const selectRecipe = (recipe) => {
    currentRecipe.value = recipe;
    currentTranscription.value = recipe.original_transcription || '';
    view.value = 'edit';
};

const deleteRecipe = async (id) => {
    if (!confirm('Are you sure you want to delete this recipe?')) return;
    try {
        await api.deleteRecipe(id);
        await fetchRecipes();
        showNotification("Recipe deleted");
    } catch (e) {
        showNotification("Failed to delete recipe", "error");
    }
};
</script>
