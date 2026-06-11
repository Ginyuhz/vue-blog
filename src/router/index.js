import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/article/:id',
    name: 'Article',
    component: () => import('../views/Article.vue')
  },
  {
    path: '/search',
    name: 'Search',
    component: () => import('../views/Search.vue')
  },
  {
    path: '/category',
    name: 'Category',
    component: () => import('../views/Category.vue')
  },
  {
    path: '/tag',
    name: 'Tag',
    component: () => import('../views/Tag.vue')
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('../views/About.vue')
  },
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: () => import('../views/admin/Login.vue')
  },
  {
    path: '/admin/article',
    name: 'AdminArticle',
    component: () => import('../views/admin/Article.vue')
  },
  {
    path: '/admin/article/edit',
    name: 'AdminArticleEdit',
    component: () => import('../views/admin/ArticleEdit.vue')
  },
  {
    path: '/admin/category',
    name: 'AdminCategory',
    component: () => import('../views/admin/Category.vue')
  },
  {
    path: '/admin/tag',
    name: 'AdminTag',
    component: () => import('../views/admin/Tag.vue')
  },
  {
    path: '/admin/profile',
    name: 'AdminProfile',
    component: () => import('../views/admin/Profile.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 56 }
    }
  }
})

export default router
