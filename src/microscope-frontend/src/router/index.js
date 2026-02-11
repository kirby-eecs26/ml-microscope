import { createRouter, createWebHistory } from "vue-router";

import View from "../window/View.vue";
import Gallery from "../window/Gallery.vue";
import Move from "../window/Move.vue";
import Image from "../window/Image.vue";
import About from "../window/About.vue";
import Logging from "../window/Logging.vue";
import Settings from "../window/Settings.vue";
import Video from "../window/Video.vue";

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/view" },
    { path: "/view", component: View },
    { path: "/gallery", component: Gallery },
    { path: "/move", component: Move },
    { path: "/image", component: Image },
    { path: "/about", component: About},
    {path: "/logging", component: Logging},
    {path: "/settings", component: Settings},
    { path: "/video", component: Video },
  ],
});
