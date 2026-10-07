import { createApp } from "vue";
import { createRouter, createWebHistory } from "vue-router";
import App from "./App.vue";
import RecipeList from "./components/RecipeList.vue";
import RecipeDetail from "./components/RecipeDetail.vue";
import "./style.css";
import Login from "./components/Login.vue";
import RecipeEditor from "./components/RecipeEditor.vue";

import Register from "./components/Register.vue";

const routes = [
  { path: "/register", component: Register },
  { path: "/", component: RecipeList },
  { path: "/favourites", component: RecipeList, props: { favourites: true } },
  { path: "/login", component: Login },
  { path: "/new", component: RecipeEditor },
  { path: "/recipe/:id/edit", component: RecipeEditor, props: true },
  { path: "/recipe/:id", component: RecipeDetail, props: true },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

createApp(App).use(router).mount("#app");
