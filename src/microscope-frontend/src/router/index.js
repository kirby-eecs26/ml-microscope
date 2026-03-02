import { createRouter, createWebHistory } from "vue-router";

import Connect from "../window/Connect.vue";
import View from "../window/View.vue";
import Gallery from "../window/Gallery.vue";
import Move from "../window/Move.vue";
import Capture from "../window/Capture.vue";
import About from "../window/About.vue";
import Logging from "../window/Logging.vue";
import Settings from "../window/Settings.vue";

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/connect" },
    { path: "/connect", component: Connect, meta: { hideSidebar: true }},
    { path: "/view", component: View },
    { path: "/gallery", component: Gallery },
    { path: "/move", component: Move },
    { path: "/capture", component: Capture },
    { path: "/about", component: About},
    { path: "/logging", component: Logging},
    { path: "/settings", component: Settings}
  ],
});
