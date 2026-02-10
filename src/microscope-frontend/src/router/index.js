import { createRouter, createWebHistory } from "vue-router";
import View from "../window/View.vue";
import Gallery from "../window/Gallery.vue";
import Move from "../window/Move.vue";
import Image from "../window/Image.vue";
<<<<<<< Updated upstream
import About from "../window/About.vue";
import Logging from "../window/Logging.vue";
import Settings from "../window/Settings.vue";
=======
<<<<<<< Updated upstream
=======
<<<<<<< Updated upstream
import About from "../window/About.vue";
import Logging from "../window/Logging.vue";
import Settings from "../window/Settings.vue";
=======
import Video from "../window/Video.vue";
>>>>>>> Stashed changes
>>>>>>> Stashed changes
>>>>>>> Stashed changes

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/view" },
    { path: "/view", component: View },
    { path: "/gallery", component: Gallery },
    { path: "/move", component: Move },
    { path: "/image", component: Image },
<<<<<<< Updated upstream
    { path: "/about", component: About},
    {path: "/logging", component: Logging},
    {path: "/settings", component: Settings},
=======
<<<<<<< Updated upstream
=======
<<<<<<< Updated upstream
    { path: "/about", component: About},
    {path: "/logging", component: Logging},
    {path: "/settings", component: Settings},
=======
    { path: "/video", component: Video },
>>>>>>> Stashed changes
>>>>>>> Stashed changes
>>>>>>> Stashed changes
  ],
});
