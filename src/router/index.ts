import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/songs',
  },
  {
    path: '/songs',
    name: 'songs',
    component: () => import('@/pages/SongsPage.vue'),
  },
  {
    path: '/formation',
    name: 'formation',
    component: () => import('@/pages/FormationPage.vue'),
  },
  {
    path: '/members',
    name: 'members',
    component: () => import('@/pages/MembersPage.vue'),
  },
  {
    path: '/substitute',
    name: 'substitute',
    component: () => import('@/pages/SubstitutePage.vue'),
  },
  {
    path: '/performances',
    name: 'performances',
    component: () => import('@/pages/PerformancesPage.vue'),
  },
  {
    path: '/performances/:id',
    name: 'performance-detail',
    component: () => import('@/pages/PerformanceDetailPage.vue'),
  },
  {
    path: '/pre-check',
    name: 'pre-check',
    component: () => import('@/pages/PreCheckPage.vue'),
  },
  {
    path: '/statistics',
    name: 'statistics',
    component: () => import('@/pages/StatisticsPage.vue'),
  },
  {
    path: '/safety-check',
    name: 'safety-check',
    component: () => import('@/pages/SafetyCheckPage.vue'),
  },
  {
    path: '/emergency',
    name: 'emergency',
    component: () => import('@/pages/EmergencyPage.vue'),
  },
  {
    path: '/risk-members',
    name: 'risk-members',
    component: () => import('@/pages/RiskMembersPage.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
