<template>
  <div class="flex flex-col items-center justify-center p-10 bg-white rounded-3xl shadow-xl shadow-indigo-100/50 border border-gray-100 relative overflow-hidden">
    <div class="absolute inset-0 bg-gradient-to-b from-indigo-50/50 to-transparent pointer-events-none"></div>
    
    <div class="relative z-10 text-center mb-8">
      <div class="inline-flex items-center justify-center p-3 bg-indigo-50 rounded-2xl mb-4 text-indigo-600">
         <MicrophoneIcon class="w-8 h-8" />
      </div>
      <h3 class="text-2xl font-bold text-gray-900">Record Your Recipe</h3>
      <p class="text-gray-500 mt-2 max-w-sm mx-auto">Tap the microphone and start speaking. Describe ingredients, steps, and details naturally.</p>
    </div>
    
    <button 
      @click="toggleRecording"
      :class="[
        'relative w-24 h-24 rounded-full flex items-center justify-center transition-all duration-500 shadow-xl transform hover:scale-105 focus:outline-none focus:ring-4 focus:ring-offset-4',
        isRecording 
            ? 'bg-red-500 hover:bg-red-600 focus:ring-red-200 shadow-red-200' 
            : 'bg-gradient-to-br from-indigo-600 to-violet-600 hover:shadow-indigo-300 focus:ring-indigo-100'
      ]"
    >
        <!-- Pulse Effect -->
      <span v-if="isRecording" class="absolute inset-0 rounded-full bg-red-500 animate-ping opacity-75"></span>
      
      <MicrophoneIcon v-if="!isRecording" class="w-10 h-10 text-white relative z-10" />
      <StopIcon v-else class="w-10 h-10 text-white relative z-10" />
    </button>

    <div class="h-8 mt-6 flex items-center justify-center">
        <div v-if="isRecording" class="flex items-center gap-2 text-red-500 font-mono font-medium text-lg bg-red-50 px-4 py-1 rounded-full animate-pulse">
            <span class="w-2 h-2 rounded-full bg-red-500"></span>
            {{ formatTime(recordingTime) }}
        </div>
        <div v-else-if="!audioBlob" class="text-gray-400 text-sm font-medium">
            Ready to record
        </div>
    </div>

    <transition
        enter-active-class="transition ease-out duration-300"
        enter-from-class="transform opacity-0 translate-y-4"
        enter-to-class="transform opacity-100 translate-y-0"
        leave-active-class="transition ease-in duration-200"
        leave-from-class="transform opacity-100 translate-y-0"
        leave-to-class="transform opacity-0 translate-y-4"
    >
        <div v-if="audioBlob && !isRecording" class="mt-8 w-full max-w-md space-y-4 bg-gray-50 p-6 rounded-2xl border border-gray-200">
            <div class="flex items-center gap-3 w-full">
                <audio ref="audioPlayer" :src="audioUrl" controls class="w-full h-10 rounded-lg shadow-sm"></audio>
            </div>
            <div class="flex gap-3 pt-2">
                <button 
                @click="resetRecording"
                class="flex-1 py-2.5 px-4 bg-white border border-gray-200 text-gray-700 rounded-xl font-medium hover:bg-gray-50 hover:border-gray-300 hover:text-gray-900 transition-all shadow-sm"
                >
                Discard
                </button>
                <button 
                @click="submitRecording" 
                :disabled="isTranscribing"
                class="flex-1 py-2.5 px-4 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 hover:shadow-lg hover:shadow-indigo-200 transition-all shadow-md flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                <span v-if="isTranscribing">Transcribing...</span>
                <span v-else>Transcribe Audio</span>
                <ArrowRightIcon v-if="!isTranscribing" class="w-4 h-4" />
                </button>
            </div>
        </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue';
import { MicrophoneIcon, StopIcon, ArrowRightIcon } from '@heroicons/vue/24/solid';

const emit = defineEmits(['transcribe']);

const isRecording = ref(false);
const mediaRecorder = ref(null);
const audioChunks = ref([]);
const audioBlob = ref(null);
const audioUrl = ref(null);
const recordingTime = ref(0);
const timerInterval = ref(null);
const isTranscribing = ref(false);

const startTimer = () => {
  recordingTime.value = 0;
  timerInterval.value = setInterval(() => {
    recordingTime.value++;
  }, 1000);
};

const stopTimer = () => {
  clearInterval(timerInterval.value);
};

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

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
    audioChunks.value = [];

    mediaRecorder.value.addEventListener("dataavailable", event => {
      audioChunks.value.push(event.data);
    });

    mediaRecorder.value.addEventListener("stop", () => {
      audioBlob.value = new Blob(audioChunks.value, { type: 'audio/wav' }); // or mp3/webm depending on browser
      audioUrl.value = URL.createObjectURL(audioBlob.value);
    });

    mediaRecorder.value.start();
    isRecording.value = true;
    startTimer();
  } catch (err) {
    console.error("Error accessing microphone:", err);
    alert("Could not access microphone. Please ensure permissions are granted.");
  }
};

const stopRecording = () => {
  if (mediaRecorder.value && isRecording.value) {
    mediaRecorder.value.stop();
    mediaRecorder.value.stream.getTracks().forEach(track => track.stop());
    isRecording.value = false;
    stopTimer();
  }
};

const resetRecording = () => {
  audioBlob.value = null;
  audioUrl.value = null;
  audioChunks.value = [];
  recordingTime.value = 0;
};

const submitRecording = async () => {
  if (!audioBlob.value) return;
  isTranscribing.value = true;
  try {
    // Convert blob to file
    const file = new File([audioBlob.value], "recording.wav", { type: 'audio/wav' });
    emit('transcribe', file);
  } finally {
    isTranscribing.value = false;
  }
};

onUnmounted(() => {
  stopTimer();
  if (isRecording.value) stopRecording();
});
</script>
