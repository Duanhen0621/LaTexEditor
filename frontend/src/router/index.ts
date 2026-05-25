import { createRouter, createWebHistory } from 'vue-router'
import PagesMain from '../pages/Main.vue'
import HistoryPage from '../pages/HistoryPage.vue'
import AuthPage from '../pages/AuthPage.vue'

const routes = [
  { path: '/', name: 'editor', component: PagesMain },
  { path: '/history', name: 'history', component: HistoryPage },
  { path: '/auth', name: 'auth', component: AuthPage },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
