<script setup>
import { ref, onMounted, onUnmounted } from "vue";

const libraryInfo = ref({ path: "", total: 0 });
const deviceStatus = ref({ connected: false });
const isScanning = ref(false);
const showModal = ref(false);

// Variables del explorador de archivos
const currentExplorePath = ref("/Volumes");
const directories = ref([]);
let statusInterval = null;

const fetchData = async () => {
  try {
    const [infoRes, statusRes] = await Promise.all([
      fetch("http://localhost:8000/api/info"),
      fetch("http://localhost:8000/api/status"),
    ]);
    const info = await infoRes.json();
    const status = await statusRes.json();
    libraryInfo.value = { path: info.library_path, total: info.total_tracks };
    deviceStatus.value = status;
  } catch (error) {
    deviceStatus.value.connected = false;
  }
};

// Navegar carpetas desde el backend
const exploreDirectory = async (path) => {
  try {
    const res = await fetch(
      `http://localhost:8000/api/directories?path=${encodeURIComponent(path)}`,
    );
    const data = await res.json();
    directories.value = data.directories;
    currentExplorePath.value = data.current_path;
  } catch (error) {
    console.error("Error leyendo directorios");
  }
};

const goUp = () => {
  const parts = currentExplorePath.value.split("/").filter(Boolean);
  parts.pop();
  const parent = "/" + parts.join("/");
  exploreDirectory(parent || "/");
};

const openModal = () => {
  showModal.value = true;
  exploreDirectory(libraryInfo.value.path || "/Volumes");
};

const savePath = async () => {
  try {
    await fetch("http://localhost:8000/api/settings/path", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path: currentExplorePath.value }),
    });
    showModal.value = false;
    fetchData();
  } catch (error) {
    console.error("Error guardando ruta");
  }
};

const triggerManualScan = async () => {
  if (!deviceStatus.value.connected) return;
  isScanning.value = true;
  try {
    await fetch("http://localhost:8000/api/scan", { method: "POST" });
    setTimeout(() => {
      fetchData();
      isScanning.value = false;
    }, 3000);
  } catch (error) {
    isScanning.value = false;
  }
};

onMounted(() => {
  fetchData();
  statusInterval = setInterval(fetchData, 3000);
});

onUnmounted(() => clearInterval(statusInterval));
</script>

<template>
  <header class="sticky top-0 z-30 bg-black border-b border-zinc-800 px-6 py-4">
    <div class="max-w-[1600px] mx-auto flex items-center justify-between">
      <!-- Info Izquierda -->
      <div class="flex items-center gap-4">
        <div class="bg-zinc-800 p-2 rounded-full relative shadow-lg">
          <span class="absolute top-0 right-0 flex h-3 w-3">
            <span
              :class="deviceStatus.connected ? 'bg-green-500' : 'bg-red-500'"
              class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75"
            ></span>
            <span
              :class="deviceStatus.connected ? 'bg-green-500' : 'bg-red-500'"
              class="relative inline-flex rounded-full h-3 w-3 border border-black"
            ></span>
          </span>
          <svg
            class="w-5 h-5 text-white"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12 0c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"
            />
          </svg>
        </div>
        <div>
          <h1
            class="text-xl font-bold text-white tracking-wide leading-none mb-1"
          >
            FLAC Player
          </h1>
          <p class="text-[11px] text-zinc-400 font-medium">
            <span
              :class="
                deviceStatus.connected ? 'text-green-400' : 'text-red-400'
              "
              >{{
                deviceStatus.connected
                  ? "Dispositivo Montado"
                  : "Buscando origen..."
              }}</span
            >
            <span class="mx-1.5">•</span>{{ libraryInfo.total }} pistas
            indexadas
          </p>
        </div>
      </div>

      <!-- Botones Derecha -->
      <div class="flex items-center gap-4">
        <button
          @click="triggerManualScan"
          :disabled="isScanning || !deviceStatus.connected"
          class="flex items-center gap-2 text-sm font-bold text-white bg-zinc-800 hover:bg-zinc-700 hover:scale-105 transition rounded-full px-4 py-2 disabled:opacity-50 disabled:hover:scale-100"
        >
          <span :class="{ 'animate-spin': isScanning }">↻</span> Sincronizar
        </button>

        <button
          @click="openModal"
          class="w-9 h-9 rounded-full bg-zinc-800 hover:bg-zinc-700 flex items-center justify-center text-zinc-300 transition hover:scale-105"
        >
          <svg
            class="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
            />
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
            />
          </svg>
        </button>
      </div>
    </div>

    <!-- Modal Explorador de Archivos -->
    <div
      v-if="showModal"
      class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
    >
      <div
        class="bg-zinc-900 border border-zinc-800 rounded-xl w-full max-w-lg shadow-2xl flex flex-col overflow-hidden max-h-[80vh]"
      >
        <div class="p-6 border-b border-zinc-800">
          <h2 class="text-xl font-bold text-white mb-1">Seleccionar Carpeta</h2>
          <p class="text-sm text-zinc-400">
            Navega y selecciona la raíz donde está tu música.
          </p>
        </div>

        <!-- Navegador -->
        <div
          class="p-4 bg-zinc-800/30 border-b border-zinc-800 flex items-center gap-3"
        >
          <button
            @click="goUp"
            :disabled="currentExplorePath === '/'"
            class="p-2 rounded bg-zinc-800 text-zinc-300 hover:text-white disabled:opacity-50 transition"
          >
            <svg
              class="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M5 10l7-7m0 0l7 7m-7-7v18"
              />
            </svg>
          </button>
          <div
            class="flex-1 px-3 py-2 bg-zinc-900 border border-zinc-700 rounded text-zinc-300 font-mono text-sm truncate"
          >
            {{ currentExplorePath }}
          </div>
        </div>

        <!-- Lista de Carpetas -->
        <div class="flex-1 overflow-y-auto p-2 min-h-[250px]">
          <div
            v-if="directories.length === 0"
            class="text-center text-zinc-500 mt-10"
          >
            No hay subcarpetas aquí.
          </div>
          <div
            v-for="dir in directories"
            :key="dir"
            @click="
              exploreDirectory(
                currentExplorePath === '/'
                  ? '/' + dir
                  : currentExplorePath + '/' + dir,
              )
            "
            class="flex items-center gap-3 p-3 rounded-lg hover:bg-zinc-800 cursor-pointer transition group"
          >
            <svg
              class="w-6 h-6 text-zinc-500 group-hover:text-white transition"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                d="M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z"
              />
            </svg>
            <span class="text-zinc-300 group-hover:text-white font-medium">{{
              dir
            }}</span>
          </div>
        </div>

        <div
          class="p-4 border-t border-zinc-800 flex justify-end gap-3 bg-zinc-900"
        >
          <button
            @click="showModal = false"
            class="px-5 py-2 rounded-full font-bold text-white hover:bg-zinc-800 transition"
          >
            Cancelar
          </button>
          <button
            @click="savePath"
            class="px-5 py-2 rounded-full font-bold text-black bg-white hover:scale-105 transition"
          >
            Seleccionar esta carpeta
          </button>
        </div>
      </div>
    </div>
  </header>
</template>
