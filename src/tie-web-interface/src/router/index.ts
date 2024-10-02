import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue')
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue')
    },
    {
      path: '/resources',
      name: 'resources',
      component: () => import('../views/ResourcesView.vue')
    }
  ],
  scrollBehavior: function (to) {
    if (to.hash) {
      // Constant top value not ideal, but it works for now
      return { el: to.hash, top: 120 }
    } else {
      return { top: 0 }
    }
  }
});
router.beforeEach((to, from, next) => {
  const url = new URL(window.location.href);
  const params = url.search;
  // If URL contains query parameters...
  if (params) {
    // ...restructure URL for webhash routing
    const path = url.pathname + (url.pathname.endsWith("/") ? "" : "/");
    const newUrl = `${url.origin}${path}#/${params}`;
    window.location.replace(newUrl);
  } else {
    next();
  }
})

export default router
