import {
  BarChart3,
  Bot,
  BookOpen,
  Briefcase,
  LayoutDashboard,
  type LucideIcon,
  Siren,
  Users,
  Workflow,
} from 'lucide-react'

export interface NavItem {
  label: string
  to: string
  icon: LucideIcon
}

export const primaryNav: NavItem[] = [
  { label: 'Overview', to: '/', icon: LayoutDashboard },
  { label: 'Incidents', to: '/incidents', icon: Siren },
  { label: 'My Work', to: '/my-work', icon: Briefcase },
  { label: 'Teams', to: '/teams', icon: Users },
  { label: 'Workflows', to: '/workflows', icon: Workflow },
  { label: 'Knowledge Base', to: '/knowledge', icon: BookOpen },
  { label: 'AI Assistant', to: '/assistant', icon: Bot },
  { label: 'Reports', to: '/reports', icon: BarChart3 },
]
