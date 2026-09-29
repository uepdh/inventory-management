import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Dashboard from './views/Dashboard.vue'
import Inventory from './views/Inventory.vue'
import Orders from './views/Orders.vue'
import Demand from './views/Demand.vue'
import Restocking from './views/Restocking.vue'
import Spending from './views/Spending.vue'
import Reports from './views/Reports.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Dashboard, meta: { titleKey: 'nav.overview' } },
    { path: '/inventory', component: Inventory, meta: { titleKey: 'nav.inventory' } },
    { path: '/orders', component: Orders, meta: { titleKey: 'nav.orders' } },
    { path: '/demand', component: Demand, meta: { titleKey: 'nav.demandForecast' } },
    { path: '/restocking', component: Restocking, meta: { titleKey: 'nav.restocking' } },
    { path: '/spending', component: Spending, meta: { titleKey: 'nav.finance' } },
    { path: '/reports', component: Reports, meta: { titleKey: 'nav.reports' } }
  ]
})

const app = createApp(App)
app.use(router)
app.mount('#app')
