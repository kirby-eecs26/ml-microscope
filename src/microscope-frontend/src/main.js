import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import "./styles.css";
import "./theme.css";
createApp(App).use(router).mount("#app");

const t = localStorage.getItem("app_theme");
if (t === "dark") document.documentElement.classList.add("theme-dark");