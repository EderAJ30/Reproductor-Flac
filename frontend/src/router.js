import { createRouter, createWebHistory } from "vue-router";
import Library from "./views/Library.vue";
import About from "./views/About.vue";

const routes = [
  { path: "/", component: Library },
  { path: "/about", component: About },
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});
