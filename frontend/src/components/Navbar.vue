<script setup>
import { ref, onMounted, onUnmounted } from "vue";

const libraryInfo = ref({ path: "", total: 0 });
const deviceStatus = ref({ connected: false });
const isScanning = ref(false);
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

const triggerManualScan = async () => {
  if (!deviceStatus.value.connected) return alert("Dispositivo no detectado");
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
  statusInterval = setInterval(fetchData, 5000); // Revisa conexión cada 5 segundos
});

onUnmounted(() => clearInterval(statusInterval));
</script>

<template>
  <header
    class="sticky top-0 z-30 bg-zinc-900/60 backdrop-blur-xl border-b border-zinc-700/50 px-6 py-4 shadow-xl"
  >
    <div
      class="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4"
    >
      <div class="flex items-center gap-4">
        <div
          class="bg-zinc-800/80 p-2 rounded-lg border border-zinc-700/60 relative"
        >
          <!-- Indicador de estado (Semáforo) -->
          <span class="absolute -top-1 -right-1 flex h-3 w-3">
            <span
              :class="deviceStatus.connected ? 'bg-green-500' : 'bg-red-500'"
              class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75"
            ></span>
            <span
              :class="deviceStatus.connected ? 'bg-green-500' : 'bg-red-500'"
              class="relative inline-flex rounded-full h-3 w-3"
            ></span>
          </span>
          <svg
            class="w-6 h-6 text-zinc-300"
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
          <h1 class="text-xl font-bold text-white tracking-wide">
            FLAC Player
          </h1>
          <p class="text-xs text-zinc-400 mt-0.5">
            Estado:
            <span
              :class="
                deviceStatus.connected ? 'text-green-400' : 'text-red-400'
              "
              >{{
                deviceStatus.connected ? "Shanling M0s Montado" : "Desconectado"
              }}</span
            >
            <span class="text-zinc-500 mx-1">•</span>
            {{ libraryInfo.total }} pistas
          </p>
        </div>
      </div>

      <div class="flex items-center gap-3">
        <button
          @click="triggerManualScan"
          :disabled="isScanning || !deviceStatus.connected"
          class="bg-zinc-800 border border-zinc-600 text-zinc-300 hover:text-white hover:bg-zinc-700 disabled:opacity-50 px-3.5 py-1.5 rounded-lg transition text-xs font-medium flex items-center gap-2"
        >
          <span :class="{ 'animate-spin': isScanning }">↻</span>
          <span>{{ isScanning ? "Escaneando..." : "Sincronizar" }}</span>
        </button>
        <div class="h-4 w-[1px] bg-zinc-700 mx-1"></div>
        <nav class="flex items-center gap-1">
          <router-link
            to="/"
            active-class="bg-zinc-800 text-white"
            class="px-3 py-1.5 rounded-lg text-xs font-medium text-zinc-400 hover:text-white transition"
            >Biblioteca</router-link
          >
          <router-link
            to="/about"
            active-class="bg-zinc-800 text-white"
            class="px-3 py-1.5 rounded-lg text-xs font-medium text-zinc-400 hover:text-white transition"
            >Acerca de</router-link
          >
        </nav>
      </div>
    </div>
  </header>
</template>
