<script setup>
defineProps(["currentPage", "totalPages"]);
defineEmits(["changePage"]);
</script>

<template>
  <div class="flex justify-center items-center gap-4 mt-8 mb-4">
    <button
      @click="$emit('changePage', currentPage - 1)"
      :disabled="currentPage === 1"
      class="px-4 py-2 bg-zinc-800 text-white rounded disabled:opacity-50 hover:bg-zinc-700 transition"
    >
      Anterior
    </button>
    <span class="text-zinc-400"
      >Página {{ currentPage }} de {{ totalPages }}</span
    >
    <button
      @click="$emit('changePage', currentPage + 1)"
      :disabled="currentPage === totalPages"
      class="px-4 py-2 bg-zinc-800 text-white rounded disabled:opacity-50 hover:bg-zinc-700 transition"
    >
      Siguiente
    </button>
  </div>
</template>
