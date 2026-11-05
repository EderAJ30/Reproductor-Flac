<script setup>
import { ref, onMounted, watch } from "vue";

const tracks = ref([]);
const totalTracks = ref(0);
const searchQuery = ref("");
const sortBy = ref("recent");
const currentTrack = ref(null);

const isScanning = ref(false);

const triggerManualScan = async () => {
  isScanning.value = true;
  try {
    await fetch("http://localhost:8000/api/scan", { method: "POST" });
    // Recarga la lista de canciones automáticamente después de 3 segundos
    setTimeout(() => {
      fetchTracks();
      isScanning.value = false;
    }, 3000);
  } catch (error) {
    console.error("Error al iniciar escaneo:", error);
    isScanning.value = false;
  }
};

// Carga las canciones con parámetros de búsqueda y orden
const fetchTracks = async () => {
  try {
    const url = new URL("http://localhost:8000/api/tracks");
    url.searchParams.append("limit", 100); // Cargamos 100 a la vez
    if (searchQuery.value) url.searchParams.append("search", searchQuery.value);
    if (sortBy.value) url.searchParams.append("sort", sortBy.value);

    const response = await fetch(url);
    const data = await response.json();
    tracks.value = data.tracks;
    totalTracks.value = data.total_indexados;
  } catch (error) {
    console.error("Error cargando canciones:", error);
  }
};

// Reactividad: si cambia la búsqueda o el orden, recargamos
watch([searchQuery, sortBy], () => {
  fetchTracks();
});

const getCoverUrl = (trackId) => `http://localhost:8000/api/covers/${trackId}`;
const getStreamUrl = (trackId) => `http://localhost:8000/api/stream/${trackId}`;

const playTrack = (track) => {
  currentTrack.value = track;
};

// Formateadores de metadatos
const formatSize = (bytes) =>
  bytes ? (bytes / (1024 * 1024)).toFixed(2) + " MB" : "0 MB";
const formatHz = (hz) => (hz ? (hz / 1000).toFixed(1) + " kHz" : "44.1 kHz");
const formatKbps = (bps) =>
  bps ? Math.round(bps / 1000) + " kb/s" : "--- kb/s";

onMounted(() => {
  fetchTracks();
});
</script>

<template>
  <!-- Fondo neutro oscuro -->
  <div class="min-h-screen bg-zinc-900 text-zinc-200 pb-32">
    <!-- Header tipo Glassmorphism pegajoso -->
    <header
      class="sticky top-0 z-10 bg-zinc-900/60 backdrop-blur-xl border-b border-zinc-700/50 p-6 shadow-xl"
    >
      <div
        class="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4"
      >
        <div>
          <h1 class="text-2xl font-semibold text-white tracking-wide">
            FLAC Player
          </h1>
          <p class="text-zinc-400 text-sm mt-1">
            Canciones indexadas: {{ totalTracks }}
          </p>
        </div>

        <!-- Controles de Búsqueda, Ordenamiento y Sincronización -->
        <div class="flex gap-3 w-full md:w-auto items-center">
          <!-- Botón de Sincronizar -->
          <button
            @click="triggerManualScan"
            :disabled="isScanning"
            class="bg-zinc-800 border border-zinc-600 text-zinc-300 hover:text-white hover:bg-zinc-700 disabled:opacity-50 px-4 py-2 rounded-lg transition text-sm font-medium flex items-center gap-2 shadow-sm"
          >
            <span v-if="isScanning" class="animate-spin">⟳</span>
            <span v-else>↻</span>
            Sincronizar
          </button>

          <input
            v-model="searchQuery"
            type="text"
            placeholder="Buscar artista, álbum, canción..."
            class="bg-zinc-800/50 border border-zinc-700 text-zinc-200 rounded-lg px-4 py-2 w-full md:w-64 focus:outline-none focus:border-zinc-500 transition placeholder-zinc-500"
          />
          <select
            v-model="sortBy"
            class="bg-zinc-800/50 border border-zinc-700 text-zinc-200 rounded-lg px-4 py-2 focus:outline-none focus:border-zinc-500 transition cursor-pointer"
          >
            <option value="recent">Últimos añadidos</option>
            <option value="size_desc">Mayor peso</option>
            <option value="size_asc">Menor peso</option>
          </select>
        </div>
      </div>
    </header>

    <!-- Grid de Canciones -->
    <main class="max-w-7xl mx-auto p-6">
      <div
        class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
      >
        <!-- Tarjeta tipo Glassmorphism -->
        <div
          v-for="track in tracks"
          :key="track.id"
          @click="playTrack(track)"
          class="group bg-zinc-800/30 backdrop-blur-md border border-zinc-700/40 rounded-xl p-4 hover:bg-zinc-700/40 transition cursor-pointer shadow-lg hover:shadow-xl hover:-translate-y-1"
        >
          <div class="flex gap-4 items-center mb-3">
            <div
              class="w-16 h-16 shrink-0 bg-zinc-800 rounded-md overflow-hidden shadow-inner relative"
            >
              <img
                :src="getCoverUrl(track.id)"
                alt="Portada"
                class="object-cover w-full h-full"
                @error="$event.target.style.display = 'none'"
              />
              <!-- Icono de Play hover -->
              <div
                class="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition"
              >
                <svg
                  class="w-8 h-8 text-white pl-1"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M8 5v14l11-7z" />
                </svg>
              </div>
            </div>
            <div class="min-w-0">
              <h2
                class="font-semibold text-zinc-100 text-base truncate"
                :title="track.title"
              >
                {{ track.title }}
              </h2>
              <p class="text-sm text-zinc-400 truncate" :title="track.artist">
                {{ track.artist }}
              </p>
              <p class="text-xs text-zinc-500 truncate" :title="track.album">
                {{ track.album }}
              </p>
            </div>
          </div>

          <!-- Metadatos Técnicos FLAC -->
          <div
            class="pt-3 border-t border-zinc-700/50 flex flex-wrap gap-2 text-[10px] uppercase font-mono text-zinc-400"
          >
            <span class="bg-zinc-800 px-2 py-1 rounded">FLAC</span>
            <span class="bg-zinc-800 px-2 py-1 rounded"
              >{{ track.bit_depth }} bit</span
            >
            <span class="bg-zinc-800 px-2 py-1 rounded">{{
              formatHz(track.sample_rate)
            }}</span>
            <span class="bg-zinc-800 px-2 py-1 rounded">{{
              formatKbps(track.bitrate)
            }}</span>
            <span class="bg-zinc-800 px-2 py-1 rounded text-zinc-300">{{
              formatSize(track.file_size)
            }}</span>
          </div>
        </div>
      </div>
    </main>

    <!-- Reproductor Bottom (Sticky Glassmorphism) -->
    <div
      v-if="currentTrack"
      class="fixed bottom-0 left-0 right-0 bg-zinc-900/80 backdrop-blur-2xl border-t border-zinc-700/60 p-4 shadow-[0_-10px_40px_rgba(0,0,0,0.3)] z-50 transition-transform duration-300"
    >
      <div
        class="max-w-7xl mx-auto flex flex-col md:flex-row items-center gap-6"
      >
        <!-- Info del track actual -->
        <div class="flex items-center gap-4 w-full md:w-1/3">
          <img
            :src="getCoverUrl(currentTrack.id)"
            class="w-12 h-12 rounded object-cover shadow-md"
            @error="$event.target.style.display = 'none'"
          />
          <div class="min-w-0">
            <p class="text-white font-semibold truncate">
              {{ currentTrack.title }}
            </p>
            <p class="text-zinc-400 text-sm truncate">
              {{ currentTrack.artist }}
            </p>
          </div>
        </div>

        <!-- Controles nativos de audio -->
        <div class="w-full md:w-2/3">
          <audio
            :src="getStreamUrl(currentTrack.id)"
            autoplay
            controls
            class="w-full h-10 custom-audio"
          ></audio>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
/* Pequeño ajuste para que el reproductor nativo encaje con los colores oscuros */
.custom-audio::-webkit-media-controls-panel {
  background-color: #27272a; /* zinc-800 */
}
.custom-audio::-webkit-media-controls-current-time-display,
.custom-audio::-webkit-media-controls-time-remaining-display {
  color: #e4e4e7;
}
</style>
