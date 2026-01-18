import { RouteConfig } from '../types/router'
import Dashboard from '../pages/Dashboard'
import Interns from '../pages/Interns'
import TeamMembers from '../pages/TeamMembers'
import Managers from '../pages/Managers'
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
    path: '/team-members',
    component: TeamMembers,
  },
  {
    path: '/managers',
    component: Managers,
  },
  {
    path: '*',
    component: NotFound,
  },
]

