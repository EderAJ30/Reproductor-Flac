<script setup>
import Navbar from "./components/Navbar.vue";
import Player from "./components/Player.vue";
</script>

<template>
  <!-- h-screen evita que la página entera haga scroll. Fondo negro estilo Spotify -->
  <div
    class="h-screen w-full bg-black text-zinc-200 flex flex-col overflow-hidden font-sans"
  >
    <!-- Barra Superior Global (Estado y Sincronización) -->
    <Navbar />

    <!-- Contenedor Principal (Donde van los 3 paneles) -->
    <main class="flex-1 overflow-hidden p-2">
      <router-view></router-view>
    </main>

    <!-- Reproductor Inferior Fijo -->
    <Player />
  </div>
</template>
