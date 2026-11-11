<script setup>
import { ref, onMounted, onUnmounted, watch } from "vue";
import { playerStore } from "../store.js";

const audioRef = ref(null);
const currentTime = ref(0);
const duration = ref(0);

const getCoverUrl = (id) => `http://localhost:8000/api/covers/${id}`;
const getStreamUrl = (id) => `http://localhost:8000/api/stream/${id}`;

const formatTime = (time) => {
  if (isNaN(time)) return "0:00";
  const minutes = Math.floor(time / 60);
  const seconds = Math.floor(time % 60);
  return `${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;
};

const togglePlay = () => {
  if (!audioRef.value) return;
  if (playerStore.isPlaying) {
    audioRef.value.pause();
    playerStore.isPlaying = false;
  } else {
    audioRef.value.play();
    playerStore.isPlaying = true;
  }
};

const onTimeUpdate = () => {
  if (audioRef.value) currentTime.value = audioRef.value.currentTime;
};

const onLoadedMetadata = () => {
  if (audioRef.value) duration.value = audioRef.value.duration;
};

const onSeek = (e) => {
  if (audioRef.value) {
    const time = (e.target.value / 100) * duration.value;
    audioRef.value.currentTime = time;
  }
};

const onEnded = () => {
  playerStore.playNext();
};

// Escuchar cambios globales en el estado (si el usuario cambia de canción arriba)
watch(
  () => playerStore.currentTrack,
  () => {
    if (audioRef.value) {
      playerStore.isPlaying = true;
    }
  },
);
</script>

<template>
  <div
    class="h-[90px] w-full bg-black border-t border-zinc-800 flex items-center px-4 z-50"
  >
    <div
      class="w-full flex items-center justify-between gap-4"
      v-if="playerStore.currentTrack"
    >
      <!-- Info Canción Izquierda -->
      <div class="flex items-center gap-4 w-1/3 min-w-0">
        <img
          :src="getCoverUrl(playerStore.currentTrack.id)"
          class="w-14 h-14 rounded object-cover shadow-md bg-zinc-800"
          @error="$event.target.style.display = 'none'"
        />
        <div class="truncate">
          <p class="text-white text-sm font-semibold truncate">
            {{ playerStore.currentTrack.title }}
          </p>
          <p class="text-zinc-400 text-xs truncate">
            {{ playerStore.currentTrack.artist }}
          </p>
        </div>
      </div>

      <!-- Controles Centrales -->
      <div class="w-1/3 flex flex-col items-center justify-center max-w-lg">
        <div class="flex items-center gap-6 mb-2">
          <!-- Botón Anterior -->
          <button
            @click="playerStore.playPrev()"
            class="text-zinc-400 hover:text-white transition"
          >
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M6 6h2v12H6zm3.5 6l8.5 6V6z" />
            </svg>
          </button>

          <!-- Botón Play/Pause (Blanco neutro) -->
          <button
            @click="togglePlay"
            class="w-8 h-8 flex items-center justify-center bg-white rounded-full text-black hover:scale-105 transition shadow-lg"
          >
            <svg
              v-if="!playerStore.isPlaying"
              class="w-5 h-5 pl-0.5"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M8 5v14l11-7z" />
            </svg>
            <svg v-else class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z" />
            </svg>
          </button>

          <!-- Botón Siguiente -->
          <button
            @click="playerStore.playNext()"
            class="text-zinc-400 hover:text-white transition"
          >
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z" />
            </svg>
          </button>
        </div>

        <!-- Barra de Progreso -->
        <div
          class="flex items-center gap-2 w-full text-xs text-zinc-400 font-mono"
        >
          <span>{{ formatTime(currentTime) }}</span>
          <input
            type="range"
            min="0"
            max="100"
            :value="duration ? (currentTime / duration) * 100 : 0"
            @input="onSeek"
            class="flex-1 h-1 bg-zinc-600 rounded-lg appearance-none cursor-pointer hover:bg-zinc-500 custom-slider"
          />
          <span>{{ formatTime(duration) }}</span>
        </div>
      </div>

      <!-- Extras Derecha -->
      <div class="w-1/3 flex justify-end items-center gap-4">
        <span
          class="text-[10px] font-mono bg-zinc-800 text-zinc-300 px-2 py-1 rounded"
          >FLAC</span
        >
      </div>

      <!-- Audio Element Oculto -->
      <audio
        ref="audioRef"
        :src="getStreamUrl(playerStore.currentTrack.id)"
        autoplay
        @timeupdate="onTimeUpdate"
        @loadedmetadata="onLoadedMetadata"
        @ended="onEnded"
        class="hidden"
      ></audio>
    </div>
  </div>
</template>

<style>
/* Estilo minimalista para la barra de progreso */
.custom-slider::-webkit-slider-thumb {
  appearance: none;
  width: 10px;
  height: 10px;
  background: white;
  border-radius: 50%;
  cursor: pointer;
  transition: transform 0.1s;
}
.custom-slider:hover::-webkit-slider-thumb {
  transform: scale(1.2);
}
</style>
