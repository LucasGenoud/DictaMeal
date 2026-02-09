<template>
  <div class="bg-white rounded-2xl shadow-xl shadow-gray-100 border border-gray-100 overflow-hidden">
    <!-- Transcription View -->
    <div v-if="mode === 'transcription'" class="p-8">
      <div class="flex items-center justify-between mb-6">
          <div>
            <h3 class="text-xl font-bold text-gray-900">Review Transcription</h3>
            <p class="text-sm text-gray-500 mt-1">Edit the raw text before AI structuring if needed.</p>
          </div>
          <div class="bg-indigo-50 text-indigo-700 px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wide">
            Step 1/2
          </div>
      </div>
      
      <div class="relative">
        <textarea 
            v-model="localTranscription" 
            class="w-full h-64 p-5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none text-gray-700 leading-relaxed font-mono text-sm shadow-inner transition-shadow"
            placeholder="Transcription will appear here..."
        ></textarea>
        <div class="absolute bottom-4 right-4 text-xs text-gray-400 pointer-events-none">
            {{ localTranscription.length }} chars
        </div>
      </div>

      <div class="mt-8 flex justify-end gap-4">
        <button 
          @click="$emit('cancel')"
          class="px-6 py-2.5 border border-gray-200 rounded-xl text-gray-600 font-medium hover:bg-gray-50 hover:text-gray-900 transition-colors"
        >
          Discard
        </button>

        <button 
          @click="structureRecipe" 
          :disabled="isStructuring || !localTranscription.trim()"
          class="px-6 py-2.5 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 shadow-lg shadow-indigo-200 hover:shadow-indigo-300 transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed transform active:scale-95"
        >
          <span v-if="isStructuring">Structuring...</span>
          <span v-else>Structure with AI</span>
          <SparklesIcon v-if="!isStructuring" class="w-5 h-5" />
        </button>
      </div>
    </div>

    <!-- Structured Recipe View (Edit Mode) -->
    <div v-else class="p-8">
      <div class="flex justify-between items-center mb-8 pb-6 border-b border-gray-50">
        <div>
            <h3 class="text-2xl font-bold text-gray-900">Recipe Details</h3>
            <p class="text-sm text-gray-500 mt-1">Refine the AI-generated details.</p>
        </div>
        <div class="flex items-center gap-3">
             <button v-if="recipeId" @click="downloadPdf" class="text-gray-600 hover:text-indigo-600 flex items-center gap-2 text-sm font-medium px-4 py-2 rounded-lg hover:bg-indigo-50 transition-colors">
                <ArrowDownTrayIcon class="w-5 h-5" /> 
                <span class="hidden sm:inline">Download PDF</span>
            </button>
        </div>
      </div>

      <div class="space-y-8">
        <div class="grid grid-cols-1 gap-6">
            <div class="space-y-1">
                <label class="block text-sm font-semibold text-gray-700">Title</label>
                <input v-model="recipe.title" type="text" class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-shadow font-medium text-gray-900 placeholder-gray-400" placeholder="e.g. Grandma's Apple Pie" />
            </div>

            <div class="space-y-1">
                <label class="block text-sm font-semibold text-gray-700">Description</label>
                <textarea v-model="recipe.description" rows="3" class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-shadow text-gray-700 placeholder-gray-400" placeholder="A brief summary of the dish..."></textarea>
            </div>

            <div class="space-y-1">
                <label class="block text-sm font-semibold text-gray-700">Image</label>
                <div class="flex items-center gap-4">
                    <div v-if="recipe.image_data" class="relative w-24 h-24 rounded-lg overflow-hidden border border-gray-200 group">
                        <img :src="recipe.image_data" alt="Recipe Image" class="w-full h-full object-cover" />
                        <button @click="recipe.image_data = ''" class="absolute inset-0 bg-black/50 text-white flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                            <XMarkIcon class="w-6 h-6" />
                        </button>
                    </div>
                    <label class="cursor-pointer flex items-center justify-center px-4 py-2 border border-blue-200 rounded-lg text-blue-600 bg-blue-50 hover:bg-blue-100 transition-colors">
                        <CameraIcon class="w-5 h-5 mr-2" />
                        <span>Upload Photo</span>
                        <input type="file" class="hidden" accept="image/*" @change="handleImageUpload" />
                    </label>
                </div>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 p-6 bg-gray-50 rounded-xl border border-gray-100">
          <div class="space-y-1">
            <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider">Duration</label>
            <div class="relative">
                 <ClockIcon class="w-5 h-5 absolute left-3 top-2.5 text-gray-400" />
                <input v-model="recipe.duration" type="text" class="w-full pl-10 pr-4 py-2.5 bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent" placeholder="e.g. 45 mins" />
            </div>
          </div>
          <div class="space-y-1">
            <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider">Origin</label>
            <div class="relative">
                <GlobeAltIcon class="w-5 h-5 absolute left-3 top-2.5 text-gray-400" />
                 <input v-model="recipe.origin" type="text" class="w-full pl-10 pr-4 py-2.5 bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent" placeholder="e.g. Italian" />
            </div>
          </div>
           <div class="space-y-1 md:col-span-2">
            <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider">Meal Type</label>
             <div class="relative">
                <TagIcon class="w-5 h-5 absolute left-3 top-2.5 text-gray-400" />
                <input v-model="recipe.meal_type" type="text" class="w-full pl-10 pr-4 py-2.5 bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent" placeholder="e.g. Dinner, Dessert" />
             </div>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <!-- Ingredients -->
            <div class="space-y-4">
                <div class="flex items-center justify-between">
                    <label class="block text-sm font-bold text-gray-900">Ingredients</label>
                    <span class="text-xs bg-indigo-50 text-indigo-600 px-2 py-1 rounded-md font-medium">{{ recipe.ingredients.length }} items</span>
                </div>
                <div class="space-y-3">
                    <transition-group name="list" tag="div" class="space-y-3">
                        <div v-for="(ing, idx) in recipe.ingredients" :key="idx" class="flex gap-2 group">
                            <div class="flex-1 relative">
                                <span class="absolute left-3 top-3 w-1.5 h-1.5 rounded-full bg-indigo-400"></span>
                                <input v-model="recipe.ingredients[idx]" type="text" class="w-full pl-8 pr-4 py-2 bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all hover:border-gray-300" placeholder="Ingredient..." />
                            </div>
                            <button @click="removeIngredient(idx)" class="w-10 flex items-center justify-center text-gray-300 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors">
                                <XMarkIcon class="w-5 h-5" />
                            </button>
                        </div>
                    </transition-group>
                </div>
                <button @click="addIngredient" class="w-full py-2 border-2 border-dashed border-gray-200 rounded-lg text-sm text-gray-500 hover:border-indigo-300 hover:text-indigo-600 hover:bg-indigo-50 transition-all font-medium flex items-center justify-center gap-2">
                    <PlusIcon class="w-4 h-4" /> Add Ingredient
                </button>
            </div>

            <!-- Steps -->
            <div class="space-y-4">
               <div class="flex items-center justify-between">
                    <label class="block text-sm font-bold text-gray-900">Instructions</label>
                    <span class="text-xs bg-indigo-50 text-indigo-600 px-2 py-1 rounded-md font-medium">{{ recipe.steps.length }} steps</span>
                </div>
                <div class="space-y-3">
                    <transition-group name="list" tag="div" class="space-y-3">
                        <div v-for="(step, idx) in recipe.steps" :key="idx" class="flex gap-3 group items-start">
                            <span class="flex-shrink-0 w-6 h-6 rounded-full bg-indigo-100 text-indigo-600 text-xs font-bold flex items-center justify-center mt-2">{{ idx + 1 }}</span>
                            <textarea v-model="recipe.steps[idx]" rows="2" class="flex-1 p-3 bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all hover:border-gray-300 resize-none" placeholder="Describe this step..."></textarea>
                            <button @click="removeStep(idx)" class="w-8 flex items-center justify-center text-gray-300 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors mt-2">
                                <XMarkIcon class="w-5 h-5" />
                            </button>
                        </div>
                     </transition-group>
                </div>
                <button @click="addStep" class="w-full py-2 border-2 border-dashed border-gray-200 rounded-lg text-sm text-gray-500 hover:border-indigo-300 hover:text-indigo-600 hover:bg-indigo-50 transition-all font-medium flex items-center justify-center gap-2">
                    <PlusIcon class="w-4 h-4" /> Add Step
                </button>
            </div>
        </div>

        <div class="pt-8 mt-8 border-t border-gray-100 flex justify-end gap-4 sticky bottom-0 bg-white/90 backdrop-blur-sm p-4 -mx-4 -mb-4 border-t border-gray-100">
           <button 
            @click="$emit('cancel')"
            class="px-6 py-2.5 border border-gray-200 rounded-xl text-gray-600 font-medium hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button 
            @click="saveRecipe" 
            class="px-8 py-2.5 bg-gradient-to-r from-indigo-600 to-violet-600 text-white rounded-xl font-bold hover:shadow-lg hover:shadow-indigo-200 transition-all flex items-center gap-2 transform active:scale-95"
          >
            <span v-if="recipeId">Update Recipe</span>
            <span v-else>Save Recipe</span>
            <CheckIcon class="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { SparklesIcon, XMarkIcon, PlusIcon, CheckIcon, ArrowDownTrayIcon, ClockIcon, GlobeAltIcon, TagIcon, CameraIcon } from '@heroicons/vue/24/solid';
import api from '../api';

const props = defineProps({
  initialTranscription: String,
  initialRecipe: Object,
  mode: {
    type: String,
    default: 'transcription' // 'transcription' or 'edit'
  }
});

const emit = defineEmits(['save', 'cancel', 'structured']);
const MAX_IMAGE_SIZE = 5 * 1024 * 1024; // 5MB

const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (file.size > MAX_IMAGE_SIZE) {
        alert("Image is too large. Please choose an image under 5MB.");
        return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
        recipe.value.image_data = e.target.result;
    };
    reader.readAsDataURL(file);
};

const localTranscription = ref(props.initialTranscription || '');
const isStructuring = ref(false);
const recipe = ref({
  title: '',
  description: '',
  ingredients: [],
  steps: [],
  duration: '',
  origin: '',
  meal_type: '',
  original_transcription: '',
  image_data: ''
});
const recipeId = ref(null);

onMounted(() => {
  if (props.initialRecipe) {
    recipe.value = JSON.parse(JSON.stringify(props.initialRecipe));
    recipeId.value = props.initialRecipe.id;
  }
  if (props.initialTranscription) {
    localTranscription.value = props.initialTranscription;
  }
});

watch(() => props.initialTranscription, (val) => {
  localTranscription.value = val;
});

watch(() => props.initialRecipe, (val) => {
  if (val) {
    recipe.value = JSON.parse(JSON.stringify(val));
    recipeId.value = val.id;
  }
});

const structureRecipe = async () => {
  isStructuring.value = true;
  try {
    const res = await api.structure(localTranscription.value);
    const structured = res.data;
    recipe.value = {
      ...structured,
      ingredients: structured.ingredients || [],
      steps: structured.steps || [],
      original_transcription: localTranscription.value
    };
    emit('structured', recipe.value);
  } catch (err) {
    console.error(err);
    alert('Failed to structure recipe. Please try again.');
  } finally {
    isStructuring.value = false;
  }
};

const addIngredient = () => recipe.value.ingredients.push('');
const removeIngredient = (idx) => recipe.value.ingredients.splice(idx, 1);
const addStep = () => recipe.value.steps.push('');
const removeStep = (idx) => recipe.value.steps.splice(idx, 1);

const saveRecipe = async () => {
  try {
    let savedRecipe;
    if (recipeId.value) {
        const res = await api.updateRecipe(recipeId.value, recipe.value);
        savedRecipe = res.data;
    } else {
        const res = await api.createRecipe(recipe.value);
        savedRecipe = res.data;
    }
    emit('save', savedRecipe);
  } catch (err) {
    console.error(err);
    alert('Failed to save recipe.');
  }
};

const downloadPdf = async () => {
  if (!recipeId.value) return;
  // In a real app we might redirect or fetch blob
  window.open(api.getRecipePdfUrl(recipeId.value), '_blank');
};
</script>
