import { createRouter, createWebHistory } from "vue-router";
import ApplicationForm from "../pages/ApplicationForm.vue";
import SuccessPage from "../pages/SuccessPage.vue";

const routes = [
  { path: "/", component: ApplicationForm },
  { path: "/success/:id", component: SuccessPage },
];

export default createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
});
