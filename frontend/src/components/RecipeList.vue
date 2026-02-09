<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
    <!-- Add New Card -->
    <div 
      @click="$emit('create')"
      class="group bg-white rounded-2xl border-2 border-dashed border-gray-200 flex flex-col items-center justify-center p-8 cursor-pointer hover:border-indigo-400 hover:bg-indigo-50/30 transition-all duration-300 min-h-[300px]"
    >
      <div class="w-16 h-16 rounded-full bg-indigo-50 flex items-center justify-center shadow-sm mb-4 group-hover:scale-110 group-hover:bg-indigo-100 transition-all duration-300">
        <PlusIcon class="w-8 h-8 text-indigo-600" />
      </div>
      <span class="text-lg font-semibold text-gray-900 mb-1">New Recipe</span>
      <span class="text-sm text-gray-500 text-center">Record or manually add</span>
    </div>

    <!-- Recipe Cards -->
    <div 
      v-for="recipe in recipes" 
      :key="recipe.id" 
      class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-xl hover:-translate-y-1 transition-all duration-300 cursor-pointer group flex flex-col"
      @click="$emit('select', recipe)"
    >
      <div class="h-48 bg-gray-100 relative overflow-hidden">
        <img 
          v-if="recipe.image_data" 
          :src="recipe.image_data" 
          alt="Recipe Image" 
          class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
        />
        <div v-else class="w-full h-full flex flex-col items-center justify-center bg-gradient-to-br from-indigo-50 to-purple-50 text-indigo-200">
           <PhotoIcon class="w-16 h-16 opacity-50 mb-2" />
           <span class="text-xs font-medium uppercase tracking-wider text-indigo-300">No Image</span>
        </div>
        
        <!-- Overlay Badges -->
        <div class="absolute top-3 left-3 flex gap-2">
            <span v-if="recipe.meal_type" class="px-2 py-1 bg-white/90 backdrop-blur-sm rounded-lg text-xs font-semibold text-gray-700 shadow-sm border border-gray-100">
                {{ recipe.meal_type }}
            </span>
        </div>

        <div class="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            <button @click.stop="$emit('delete', recipe.id)" class="p-2 bg-white/90 backdrop-blur-sm rounded-full text-red-500 hover:text-red-700 hover:bg-white shadow-sm transition-colors">
                <TrashIcon class="w-4 h-4" />
            </button>
        </div>
      </div>

      <div class="p-5 flex-1 flex flex-col">
        <h3 class="font-bold text-xl text-gray-900 mb-2 line-clamp-1 group-hover:text-indigo-600 transition-colors">{{ recipe.title || 'Untitled Recipe' }}</h3>
        <p class="text-sm text-gray-500 line-clamp-2 mb-4 flex-1 h-10">{{ recipe.description || 'No description provided.' }}</p>
        
        <div class="pt-4 border-t border-gray-50 flex items-center justify-between text-xs font-medium text-gray-500">
          <div class="flex items-center gap-1.5 bg-gray-50 px-2 py-1 rounded-md">
            <ClockIcon class="w-3.5 h-3.5 text-gray-400" />
            <span>{{ recipe.duration || 'N/A' }}</span>
          </div>
          <div class="flex items-center gap-1.5 bg-gray-50 px-2 py-1 rounded-md">
            <GlobeAltIcon class="w-3.5 h-3.5 text-gray-400" />
            <span>{{ recipe.origin || 'Unknown' }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { PhotoIcon, ClockIcon, GlobeAltIcon, PlusIcon, TrashIcon } from '@heroicons/vue/24/outline';

defineProps({
  recipes: {
    type: Array,
    default: () => []
  }
});

defineEmits(['select', 'create', 'delete']);
</script>
