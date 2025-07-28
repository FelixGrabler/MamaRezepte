import { createApp } from "vue";
import { createRouter, createWebHistory } from "vue-router";
import App from "./App.vue";
import RecipeList from "./components/RecipeList.vue";
import RecipeDetail from "./components/RecipeDetail.vue";
import "./style.css";

const routes = [
  { path: "/", component: RecipeList },
  { path: "/recipe/:id", component: RecipeDetail, props: true },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

createApp(App).use(router).mount("#app");
