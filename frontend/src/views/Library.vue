<script setup>
import { ref, onMounted, watch } from "vue";
import { playerStore } from "../store.js";

const tracks = ref([]);
const albums = ref([]);
const page = ref(1);
const totalPages = ref(1);
const search = ref("");
const selectedAlbum = ref("");

const fetchAlbums = async () => {
  const res = await fetch("http://localhost:8000/api/albums");
  const data = await res.json();
  albums.value = data.filter(Boolean);
};

const fetchTracks = async () => {
  const url = new URL("http://localhost:8000/api/tracks");
  url.searchParams.append("page", page.value);
  if (search.value) url.searchParams.append("search", search.value);
  if (selectedAlbum.value) {
    url.searchParams.append("album", selectedAlbum.value);
    url.searchParams.set("limit", 100); // Cargamos el álbum completo de una vez
  }

  const res = await fetch(url);
  const data = await res.json();
  if (page.value === 1 || selectedAlbum.value) {
    tracks.value = data.tracks;
  } else {
    tracks.value = [...tracks.value, ...data.tracks];
  }
  totalPages.value = data.total_pages;
};

const handleScroll = (e) => {
  if (selectedAlbum.value) return; // No infinite scroll dentro de un álbum
  const { scrollTop, clientHeight, scrollHeight } = e.target;
  if (
    scrollTop + clientHeight >= scrollHeight - 20 &&
    page.value < totalPages.value
  ) {
    page.value++;
  }
};

const selectAlbum = (albumName) => {
  selectedAlbum.value = selectedAlbum.value === albumName ? "" : albumName;
  page.value = 1;
};

watch([search, selectedAlbum], () => {
  page.value = 1;
  fetchTracks();
});

onMounted(() => {
  fetchAlbums();
  fetchTracks();
});

const getCoverUrl = (id) => `http://localhost:8000/api/covers/${id}`;
const formatSize = (b) => (b / 1048576).toFixed(2) + " MB";
const formatHz = (hz) => (hz / 1000).toFixed(1) + " kHz";
const formatKbps = (bps) => Math.round(bps / 1000) + " kb/s";
const formatDuration = (seconds) => {
  if (!seconds) return "0:00";
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s < 10 ? "0" : ""}${s}`;
};
</script>

<template>
  <div class="flex h-full w-full gap-2">
    <!-- PANEL IZQUIERDO -->
    <aside
      class="w-64 bg-zinc-900 rounded-xl flex flex-col overflow-hidden shadow-lg border border-zinc-800/50"
    >
      <div
        class="p-4 font-bold text-white flex items-center gap-3 border-b border-zinc-800"
      >
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <path
            d="M3 3h18v18H3V3zm16 16V5H5v14h14zm-4-4h-8v-2h8v2zm-8-4h6v-2h-6v2z"
          />
        </svg>
        Tu Biblioteca
      </div>
      <div class="flex-1 overflow-y-auto p-2 scrollbar-hide">
        <div
          v-for="al in albums"
          :key="al.name"
          @click="selectAlbum(al.name)"
          :class="
            selectedAlbum === al.name
              ? 'bg-zinc-800 text-white'
              : 'text-zinc-400 hover:bg-zinc-800 hover:text-white'
          "
          class="p-2 rounded-lg cursor-pointer transition flex items-center gap-3 group"
        >
          <!-- CARÁTULA CORREGIDA EN BARRA LATERAL -->
          <img
            :src="getCoverUrl(al.id)"
            class="w-10 h-10 rounded object-cover shadow-sm group-hover:shadow-md bg-zinc-700"
            @error="$event.target.style.display = 'none'"
          />
          <span class="truncate text-sm font-medium">{{ al.name }}</span>
        </div>
      </div>
    </aside>

    <!-- PANEL CENTRAL -->
    <main
      class="flex-1 bg-zinc-900 rounded-xl flex flex-col overflow-hidden shadow-lg border border-zinc-800/50 relative"
    >
      <div
        class="sticky top-0 bg-zinc-900/95 backdrop-blur z-10 p-4 border-b border-zinc-800 flex items-center"
      >
        <div class="relative w-full max-w-md">
          <svg
            class="w-5 h-5 absolute left-3 top-2.5 text-zinc-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          <input
            v-model="search"
            type="text"
            placeholder="Buscar canciones o álbumes..."
            class="w-full bg-zinc-800/80 border border-zinc-700 text-white rounded-full pl-10 pr-4 py-2 focus:outline-none focus:border-zinc-500 focus:bg-zinc-800 transition"
          />
        </div>
      </div>

      <div class="flex-1 overflow-y-auto scrollbar-hide" @scroll="handleScroll">
        <!-- VISTA MODO DESCUBRIR (Cuadrícula general) -->
        <div
          v-if="!selectedAlbum"
          class="p-6 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6"
        >
          <div
            v-for="track in tracks"
            :key="track.id"
            @click="playerStore.play(track, tracks)"
            class="bg-zinc-800/40 p-4 rounded-xl hover:bg-zinc-800 transition cursor-pointer group flex flex-col"
          >
            <div
              class="relative w-full aspect-square mb-4 rounded-lg overflow-hidden bg-zinc-700 shadow-md"
            >
              <img
                :src="getCoverUrl(track.id)"
                class="w-full h-full object-cover"
                @error="$event.target.style.display = 'none'"
              />
              <div
                class="absolute bottom-2 right-2 w-12 h-12 bg-white rounded-full flex items-center justify-center opacity-0 translate-y-2 group-hover:opacity-100 group-hover:translate-y-0 transition-all duration-300 shadow-lg"
              >
                <svg
                  class="w-6 h-6 text-black pl-1"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M8 5v14l11-7z" />
                </svg>
              </div>
            </div>
            <h3 class="font-bold text-white truncate">{{ track.title }}</h3>
            <p class="text-sm text-zinc-400 truncate mt-1">
              {{ track.artist }}
            </p>
          </div>
        </div>

        <!-- VISTA MODO ÁLBUM ESTILO SPOTIFY (Lista de canciones en orden) -->
        <div v-else class="flex flex-col">
          <!-- Cabezal Gigante -->
          <div
            class="flex flex-col md:flex-row items-end gap-6 p-6 bg-gradient-to-b from-zinc-700 to-zinc-900 border-b border-zinc-800/50"
          >
            <img
              :src="getCoverUrl(tracks[0]?.id)"
              class="w-48 h-48 shadow-2xl rounded-sm object-cover bg-zinc-800"
            />
            <div>
              <p
                class="text-sm font-bold text-white uppercase tracking-wider mb-1"
              >
                Álbum
              </p>
              <h1
                class="text-4xl md:text-5xl font-black text-white mt-1 mb-4 leading-tight"
              >
                {{ selectedAlbum }}
              </h1>
              <p
                class="text-zinc-300 text-sm font-medium flex items-center gap-2"
              >
                <span class="text-white font-bold">{{
                  tracks[0]?.artist
                }}</span>
                • {{ tracks.length }} canciones
              </p>
            </div>
          </div>

          <!-- Tabla de Canciones (Orden Real) -->
          <div class="px-6 pb-6 pt-2">
            <div
              class="grid grid-cols-[30px_1fr_60px] gap-4 px-4 py-2 border-b border-zinc-800 text-zinc-400 text-sm mb-2 uppercase font-semibold"
            >
              <div class="text-center">#</div>
              <div>Título</div>
              <div class="text-right">
                <svg
                  class="w-5 h-5 inline"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
            </div>

            <div
              v-for="(track, index) in tracks"
              :key="track.id"
              @click="playerStore.play(track, tracks)"
              class="grid grid-cols-[30px_1fr_60px] gap-4 px-4 py-3 rounded-md hover:bg-zinc-800/50 group cursor-pointer items-center transition"
            >
              <div class="text-zinc-400 text-sm text-center group-hover:hidden">
                {{ track.track_number || index + 1 }}
              </div>
              <div class="hidden group-hover:flex justify-center items-center">
                <svg
                  class="w-4 h-4 text-white"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M8 5v14l11-7z" />
                </svg>
              </div>
              <div class="min-w-0">
                <p
                  :class="
                    playerStore.currentTrack?.id === track.id
                      ? 'text-green-500'
                      : 'text-white'
                  "
                  class="font-semibold truncate text-base"
                >
                  {{ track.title }}
                </p>
                <p class="text-zinc-400 text-sm truncate">{{ track.artist }}</p>
              </div>
              <div class="text-zinc-400 text-sm text-right font-mono">
                {{ formatDuration(track.duration) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- PANEL DERECHO (Sin cambios, reproduciendo actualmente) -->
    <aside
      class="w-72 bg-zinc-900 rounded-xl flex flex-col overflow-hidden shadow-lg border border-zinc-800/50 p-4"
    >
      <h3 class="text-zinc-400 text-sm font-bold mb-4 uppercase tracking-wider">
        Reproduciendo
      </h3>
      <div v-if="playerStore.currentTrack" class="flex-1 flex flex-col">
        <img
          :src="getCoverUrl(playerStore.currentTrack.id)"
          class="w-full aspect-square rounded-xl shadow-2xl mb-6 object-cover bg-zinc-800"
          @error="$event.target.style.display = 'none'"
        />
        <h2 class="text-2xl font-bold text-white leading-tight">
          {{ playerStore.currentTrack.title }}
        </h2>
        <p class="text-zinc-400 mt-1 text-lg">
          {{ playerStore.currentTrack.artist }}
        </p>
        <div
          class="mt-6 bg-zinc-800/50 rounded-lg p-4 border border-zinc-700/50"
        >
          <p class="text-xs font-semibold text-zinc-500 uppercase mb-2">
            Acerca del Archivo
          </p>
          <ul class="space-y-2 text-sm text-zinc-300 font-mono">
            <li class="flex justify-between">
              <span>Formato:</span> <span class="text-white">FLAC</span>
            </li>
            <li class="flex justify-between">
              <span>Resolución:</span>
              <span class="text-white"
                >{{ playerStore.currentTrack.bit_depth }} bit</span
              >
            </li>
            <li class="flex justify-between">
              <span>Frecuencia:</span>
              <span class="text-white">{{
                formatHz(playerStore.currentTrack.sample_rate)
              }}</span>
            </li>
            <li class="flex justify-between">
              <span>Bitrate:</span>
              <span class="text-white">{{
                formatKbps(playerStore.currentTrack.bitrate)
              }}</span>
            </li>
            <li class="flex justify-between">
              <span>Peso:</span>
              <span class="text-white">{{
                formatSize(playerStore.currentTrack.file_size)
              }}</span>
            </li>
          </ul>
        </div>
      </div>
      <div
        v-else
        class="flex-1 flex flex-col items-center justify-center text-zinc-500 text-center px-4"
      >
        <svg
          class="w-16 h-16 mb-4 text-zinc-700"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="1.5"
            d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12 0c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"
          />
        </svg>
        <p>Selecciona una pista para ver sus propiedades</p>
      </div>
    </aside>
  </div>
</template>

<style scoped>
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
