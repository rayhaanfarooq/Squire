import { RouteConfig } from '../types/router'
import Dashboard from '../pages/Dashboard'
import Interns from '../pages/Interns'
import NotFound from '../pages/NotFound'

export const router: RouteConfig[] = [
  {
    path: '/',
    component: Dashboard,
  },
  {
    path: '/interns',
    component: Interns,
  },
  {
    path: '*',
    component: NotFound,
  },
]

