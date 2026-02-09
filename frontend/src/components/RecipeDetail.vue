<template>
  <div class="max-w-4xl mx-auto bg-white rounded-2xl shadow-xl shadow-gray-100 border border-gray-100 overflow-hidden" itemscope itemtype="https://schema.org/Recipe">
    
    <!-- Hero Section -->
    <div class="relative h-64 md:h-80 bg-gray-100">
      <img 
        v-if="recipe.image_data" 
        :src="recipe.image_data" 
        :alt="recipe.title" 
        itemprop="image"
        class="w-full h-full object-cover"
      />
      <div v-else class="w-full h-full flex flex-col items-center justify-center bg-gradient-to-br from-indigo-50 to-purple-50 text-indigo-200">
         <PhotoIcon class="w-24 h-24 opacity-50 mb-2" />
         <span class="text-sm font-medium uppercase tracking-wider text-indigo-300">No Image</span>
      </div>
      <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
      
      <div class="absolute bottom-0 left-0 right-0 p-8 text-white">
        <h1 class="text-4xl font-extrabold tracking-tight mb-2 text-shadow-sm" itemprop="name">{{ recipe.title }}</h1>
        <div class="flex items-center gap-4 text-sm font-medium">
             <div class="flex items-center gap-1.5 bg-white/20 backdrop-blur-md px-3 py-1 rounded-full border border-white/10">
                <ClockIcon class="w-4 h-4" />
                <span itemprop="cookTime">{{ recipe.duration || 'N/A' }}</span>
             </div>
             <div class="flex items-center gap-1.5 bg-white/20 backdrop-blur-md px-3 py-1 rounded-full border border-white/10">
                <GlobeAltIcon class="w-4 h-4" />
                <span itemprop="recipeCuisine">{{ recipe.origin || 'Unknown' }}</span>
             </div>
             <div class="flex items-center gap-1.5 bg-white/20 backdrop-blur-md px-3 py-1 rounded-full border border-white/10">
                <TagIcon class="w-4 h-4" />
                <span itemprop="recipeCategory">{{ recipe.meal_type || 'General' }}</span>
             </div>
        </div>
      </div>
    </div>

    <!-- Toolbar -->
    <div class="p-6 border-b border-gray-50 flex items-center justify-between bg-white sticky top-0 z-10 shadow-sm">
        <button 
            @click="$emit('back')"
            class="group flex items-center gap-2 text-sm font-medium text-gray-500 hover:text-indigo-600 transition-colors"
        >
            <div class="p-1 rounded-full bg-gray-100 group-hover:bg-indigo-100 transition-colors">
                 <ArrowLeftIcon class="w-4 h-4" />
            </div>
            Back
        </button>

        <div class="flex items-center gap-3">
             <button 
                @click="showDictateModal = true"
                class="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl font-bold hover:shadow-lg hover:shadow-indigo-200 transition-all transform active:scale-95 text-sm"
            >
                <MicrophoneIcon class="w-4 h-4" />
                Dictate Changes
            </button>
            <button 
                @click="$emit('edit', recipe)"
                class="flex items-center gap-2 px-4 py-2 border border-gray-200 rounded-xl text-gray-700 font-medium hover:bg-gray-50 hover:text-indigo-600 transition-all text-sm"
            >
                <PencilSquareIcon class="w-4 h-4" />
                Manual Edit
            </button>
        </div>
    </div>

    <!-- Content -->
    <div class="p-8 grid grid-cols-1 md:grid-cols-3 gap-12">
        
        <!-- Description & Ingredients -->
        <div class="md:col-span-1 space-y-8">
            <div v-if="recipe.description" class="prose prose-sm text-gray-500">
                <p itemprop="description">{{ recipe.description }}</p>
            </div>

            <div class="bg-indigo-50/50 rounded-2xl p-6 border border-indigo-100">
                <h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                    <span class="bg-indigo-100 text-indigo-600 p-1 rounded-md"><ShoppingBagIcon class="w-4 h-4" /></span>
                    Ingredients
                </h3>
                <ul class="space-y-3">
                    <li v-for="(ingredient, idx) in recipe.ingredients" :key="idx" class="flex items-start gap-3 text-sm text-gray-700" itemprop="recipeIngredient">
                        <span class="w-1.5 h-1.5 rounded-full bg-indigo-400 mt-2 flex-shrink-0"></span>
                        <span class="leading-relaxed">{{ ingredient }}</span>
                    </li>
                </ul>
            </div>
        </div>

        <!-- Steps -->
        <div class="md:col-span-2 space-y-8">
            <h3 class="text-2xl font-bold text-gray-900 border-b border-gray-100 pb-4">Instructions</h3>
            
            <div class="space-y-6">
                <div v-for="(step, idx) in recipe.steps" :key="idx" class="flex gap-4 group" itemprop="recipeInstructions" itemscope itemtype="https://schema.org/HowToStep">
                    <div class="flex-shrink-0">
                        <span class="w-8 h-8 rounded-full bg-gray-100 text-gray-500 font-bold flex items-center justify-center text-sm group-hover:bg-indigo-600 group-hover:text-white transition-colors">
                            {{ idx + 1 }}
                        </span>
                    </div>
                    <div class="flex-1 pt-1.5">
                        <p class="text-gray-700 leading-relaxed text-lg" itemprop="text">{{ step }}</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Dictate Modal -->
    <transition
        enter-active-class="transition ease-out duration-200"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition ease-in duration-150"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
    >
        <div v-if="showDictateModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-900/50 backdrop-blur-sm">
            <div class="bg-white rounded-2xl shadow-2xl max-w-lg w-full p-8 relative overflow-hidden">
                 <button @click="closeDictateModal" class="absolute top-4 right-4 text-gray-400 hover:text-gray-600">
                    <XMarkIcon class="w-6 h-6" />
                </button>

                <div class="text-center mb-6">
                    <div class="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-4 text-indigo-600">
                        <SparklesIcon class="w-6 h-6" />
                    </div>
                    <h3 class="text-xl font-bold text-gray-900">AI Recipe Editor</h3>
                    <p class="text-sm text-gray-500 mt-2">Speak or type how you want to change this recipe.</p>
                </div>

                <!-- Input Methods -->
                <div class="space-y-6">
                    <div v-if="!inputMode" class="flex justify-center">
                         <button 
                            @click="toggleRecording"
                            :class="[
                                'w-20 h-20 rounded-full flex items-center justify-center transition-all shadow-lg',
                                isRecording ? 'bg-red-500 animate-pulse' : 'bg-indigo-600 hover:bg-indigo-700'
                            ]"
                        >
                            <MicrophoneIcon v-if="!isRecording" class="w-8 h-8 text-white" />
                            <StopIcon v-else class="w-8 h-8 text-white" />
                        </button>
                    </div>

                    <div v-if="isProcessingAudio" class="text-center text-sm text-indigo-600 font-medium animate-pulse">
                        Transcribing audio...
                    </div>

                    <div v-else>
                         <textarea 
                            v-model="instruction"
                            rows="4"
                            class="w-full p-4 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm resize-none"
                            placeholder="e.g. 'Double the sugar amount' or 'Make it vegan'..."
                        ></textarea>
                    </div>

                     <div class="flex gap-3">
                        <button 
                            @click="closeDictateModal"
                            class="flex-1 py-2.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-xl font-medium transition-colors"
                        >
                            Cancel
                        </button>
                        <button 
                            @click="submitInstruction" 
                            :disabled="!instruction || isUpdating"
                            class="flex-1 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-medium shadow-lg shadow-indigo-200 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                        >
                            <span v-if="isUpdating">Updating...</span>
                            <span v-else>Apply Changes</span>
                            <ArrowRightIcon v-if="!isUpdating" class="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </transition>

  </div>
</template>

<script setup>
import { ref } from 'vue';
import { 
    PhotoIcon, ClockIcon, GlobeAltIcon, TagIcon, ArrowLeftIcon, 
    PencilSquareIcon, MicrophoneIcon, ShoppingBagIcon, SparklesIcon,
    XMarkIcon, StopIcon, ArrowRightIcon
} from '@heroicons/vue/24/solid';
import api from '../api';

const props = defineProps({
    recipe: {
        type: Object,
        required: true
    }
});

const emit = defineEmits(['back', 'edit', 'update']);

const showDictateModal = ref(false);
const instruction = ref('');
const isRecording = ref(false);
const mediaRecorder = ref(null);
const isProcessingAudio = ref(false);
const isUpdating = ref(false);
const inputMode = ref(false); // false = voice, true = text (could toggle)

// Recording Logic (Simplified reuse of AudioRecorder logic)
const toggleRecording = async () => {
    if (isRecording.value) {
        stopRecording();
    } else {
        await startRecording();
    }
};

const startRecording = async () => {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder.value = new MediaRecorder(stream);
        const chunks = [];
        
        mediaRecorder.value.addEventListener("dataavailable", e => chunks.push(e.data));
        mediaRecorder.value.addEventListener("stop", async () => {
            const blob = new Blob(chunks, { type: 'audio/wav' });
            await transcribeAudio(blob);
        });

        mediaRecorder.value.start();
        isRecording.value = true;
    } catch (err) {
        alert("Microphone access denied.");
    }
};

const stopRecording = () => {
    if (mediaRecorder.value && isRecording.value) {
        mediaRecorder.value.stop();
        mediaRecorder.value.stream.getTracks().forEach(track => track.stop());
        isRecording.value = false;
    }
};

const transcribeAudio = async (blob) => {
    isProcessingAudio.value = true;
    try {
        const file = new File([blob], "instruction.wav", { type: 'audio/wav' });
        const res = await api.transcribe(file);
        instruction.value = res.data.text;
    } catch (e) {
        alert("Transcription failed.");
    } finally {
        isProcessingAudio.value = false;
    }
};

const closeDictateModal = () => {
    showDictateModal.value = false;
    instruction.value = '';
    isRecording.value = false;
};

const submitInstruction = async () => {
    if (!instruction.value) return;
    isUpdating.value = true;
    try {
        const res = await api.updateRecipeWithInstruction(props.recipe, instruction.value);
        emit('update', res.data);
        closeDictateModal();
    } catch (e) {
        console.error(e);
        alert("Failed to update recipe. Please try again.");
    } finally {
        isUpdating.value = false;
    }
};
</script>
