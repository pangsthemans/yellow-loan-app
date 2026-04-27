import { createApp } from "vue";
import { Quasar, Notify, Dialog } from "quasar";
import { createPinia } from "pinia";

import "@quasar/extras/material-icons/material-icons.css";
import "quasar/dist/quasar.css";
import "./styles/global.css";

import App from "./App.vue";
import router from "./router";

const app = createApp(App);

app.use(createPinia());
app.use(router);
app.use(Quasar, {
  plugins: { Notify, Dialog },
  config: {
    notify: {
      position: "top",
      timeout: 3000,
    },
  },
});

app.mount("#app");
