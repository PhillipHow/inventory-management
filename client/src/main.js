import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Dashboard from './views/Dashboard.vue'
import Inventory from './views/Inventory.vue'
import Orders from './views/Orders.vue'
import Demand from './views/Demand.vue'
import Spending from './views/Spending.vue'
import Reports from './views/Reports.vue'
import Restocking from './views/Restocking.vue'
import Login from './views/Login.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Dashboard },
    { path: '/inventory', component: Inventory },
    { path: '/orders', component: Orders },
    { path: '/demand', component: Demand },
    { path: '/restocking', component: Restocking },
    { path: '/spending', component: Spending },
    { path: '/reports', component: Reports },
    { path: '/login', component: Login }
  ]
})

router.beforeEach((to) => {
  const hasToken = !!localStorage.getItem('auth_token')

  if (to.path !== '/login' && !hasToken) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }

  if (to.path === '/login' && hasToken) {
    return { path: '/' }
  }

  return true
})

const app = createApp(App)
app.use(router)
app.mount('#app')
