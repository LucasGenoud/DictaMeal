import { ref } from 'vue';
import api from '../api';

/**
 * Composable for audio recording functionality.
 * Shared between AudioRecorder and RecipeDetail components.
 */
export function useAudioRecording() {
    const isRecording = ref(false);
    const mediaRecorder = ref(null);
    const audioChunks = ref([]);
    const audioBlob = ref(null);
    const audioUrl = ref(null);
    const isProcessingAudio = ref(false);

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder.value = new MediaRecorder(stream);
            audioChunks.value = [];

            mediaRecorder.value.addEventListener("dataavailable", event => {
                audioChunks.value.push(event.data);
            });

            mediaRecorder.value.addEventListener("stop", () => {
                audioBlob.value = new Blob(audioChunks.value, { type: 'audio/wav' });
                audioUrl.value = URL.createObjectURL(audioBlob.value);
            });

            mediaRecorder.value.start();
            isRecording.value = true;
            return true;
        } catch (err) {
            console.error("Error accessing microphone:", err);
            return false;
        }
    };

    const stopRecording = () => {
        if (mediaRecorder.value && isRecording.value) {
            mediaRecorder.value.stop();
            mediaRecorder.value.stream.getTracks().forEach(track => track.stop());
            isRecording.value = false;
        }
    };

    const toggleRecording = async () => {
        if (isRecording.value) {
            stopRecording();
        } else {
            return await startRecording();
        }
    };

    const resetRecording = () => {
        audioBlob.value = null;
        audioUrl.value = null;
        audioChunks.value = [];
    };

    const transcribeAudio = async (blob = audioBlob.value) => {
        if (!blob) return null;
        isProcessingAudio.value = true;
        try {
            const file = new File([blob], "recording.wav", { type: 'audio/wav' });
            const res = await api.transcribe(file);
            return res.data.text;
        } catch (e) {
            console.error("Transcription failed:", e);
            return null;
        } finally {
            isProcessingAudio.value = false;
        }
    };

    return {
        isRecording,
        audioBlob,
        audioUrl,
        isProcessingAudio,
        startRecording,
        stopRecording,
        toggleRecording,
        resetRecording,
        transcribeAudio
    };
}
