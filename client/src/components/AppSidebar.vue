<template>
  <!-- Backdrop for mobile off-canvas mode; clicking it closes the sidebar -->
  <div
    v-if="mobileOpen"
    class="sidebar-backdrop"
    @click="closeMobile"
  ></div>

  <aside
    class="sidebar"
    :class="{ collapsed: collapsed, 'mobile-open': mobileOpen }"
  >
    <div class="sidebar-brand">
      <h1 v-if="!collapsed">{{ t('nav.companyName') }}</h1>
      <h1 v-else class="brand-mark">{{ brandInitial }}</h1>
      <span v-if="!collapsed" class="subtitle">{{ t('nav.subtitle') }}</span>
    </div>

    <nav class="sidebar-nav">
      <router-link
        to="/"
        class="nav-link"
        :aria-current="$route.path === '/' ? 'page' : null"
        :title="collapsed ? t('nav.overview') : null"
        :aria-label="collapsed ? t('nav.overview') : null"
      >
        <AppIcon name="home" :size="20" />
        <span v-if="!collapsed" class="nav-label">{{ t('nav.overview') }}</span>
      </router-link>

      <div class="nav-group">
        <div v-if="!collapsed" class="nav-group-label">{{ t('nav.groups.operations') }}</div>
        <router-link
          v-for="item in operationsLinks"
          :key="item.path"
          :to="item.path"
          class="nav-link"
          :aria-current="$route.path === item.path ? 'page' : null"
          :title="collapsed ? t(item.labelKey) : null"
          :aria-label="collapsed ? t(item.labelKey) : null"
        >
          <AppIcon :name="item.icon" :size="20" />
          <span v-if="!collapsed" class="nav-label">{{ t(item.labelKey) }}</span>
        </router-link>
      </div>

      <div class="nav-group">
        <div v-if="!collapsed" class="nav-group-label">{{ t('nav.groups.insights') }}</div>
        <router-link
          v-for="item in insightsLinks"
          :key="item.path"
          :to="item.path"
          class="nav-link"
          :aria-current="$route.path === item.path ? 'page' : null"
          :title="collapsed ? t(item.labelKey) : null"
          :aria-label="collapsed ? t(item.labelKey) : null"
        >
          <AppIcon :name="item.icon" :size="20" />
          <span v-if="!collapsed" class="nav-label">{{ t(item.labelKey) }}</span>
        </router-link>
      </div>
    </nav>

    <div class="sidebar-footer">
      <LanguageSwitcher placement="up-left" />
      <ProfileMenu
        placement="up-left"
        @show-profile-details="$emit('show-profile-details')"
        @show-tasks="$emit('show-tasks')"
      />

      <button
        class="collapse-toggle"
        type="button"
        :aria-label="collapsed ? t('nav.expandSidebar') : t('nav.collapseSidebar')"
        :title="collapsed ? t('nav.expandSidebar') : t('nav.collapseSidebar')"
        @click="toggleCollapsed"
      >
        <AppIcon name="chevronDoubleLeft" :size="18" class="collapse-icon" :class="{ flipped: collapsed }" />
        <span v-if="!collapsed">{{ t('nav.collapseSidebar') }}</span>
      </button>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from '../composables/useI18n'
import { useSidebar } from '../composables/useSidebar'
import AppIcon from './AppIcon.vue'
import LanguageSwitcher from './LanguageSwitcher.vue'
import ProfileMenu from './ProfileMenu.vue'

defineEmits(['show-profile-details', 'show-tasks'])

const { t } = useI18n()
const { collapsed, toggleCollapsed, mobileOpen, closeMobile } = useSidebar()

const operationsLinks = [
  { path: '/inventory', labelKey: 'nav.inventory', icon: 'archiveBox' },
  { path: '/orders', labelKey: 'nav.orders', icon: 'shoppingCart' },
  { path: '/restocking', labelKey: 'nav.restocking', icon: 'arrowPath' }
]

const insightsLinks = [
  { path: '/demand', labelKey: 'nav.demandForecast', icon: 'chartBar' },
  { path: '/spending', labelKey: 'nav.finance', icon: 'currencyDollar' },
  { path: '/reports', labelKey: 'nav.reports', icon: 'documentChartBar' }
]

const brandInitial = computed(() => (t('nav.companyName') || '').charAt(0))
</script>

<style scoped>
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: 264px;
  background: var(--surface-0);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  z-index: 200;
  transition: width 0.2s ease, transform 0.2s ease;
  overflow: hidden;
}

.sidebar.collapsed {
  width: 76px;
}

.sidebar-brand {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: var(--space-1);
  padding: var(--space-5) var(--space-4);
  border-bottom: 1px solid var(--border);
  min-height: 64px;
  justify-content: center;
}

.sidebar-brand h1 {
  font-size: var(--text-lg);
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.025em;
  white-space: nowrap;
}

.sidebar-brand .brand-mark {
  font-size: var(--text-xl);
  text-align: center;
  width: 100%;
}

.sidebar-brand .subtitle {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  font-weight: 400;
  white-space: nowrap;
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: var(--space-4) var(--space-3);
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.nav-group {
  margin-top: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.nav-group-label {
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-3);
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: 500;
  font-size: var(--text-sm);
  border-radius: var(--radius-sm);
  transition: background 0.15s ease, color 0.15s ease;
  white-space: nowrap;
}

.sidebar.collapsed .nav-link {
  justify-content: center;
}

.nav-link svg {
  flex-shrink: 0;
}

.nav-link:hover {
  color: var(--text-primary);
  background: var(--surface-2);
}

.nav-link:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.nav-link[aria-current='page'] {
  color: var(--accent);
  background: var(--accent-tint);
}

.nav-label {
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-footer {
  border-top: 1px solid var(--border);
  padding: var(--space-3);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.collapse-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  background: none;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-family: inherit;
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--text-secondary);
  transition: background 0.15s ease, color 0.15s ease;
}

.collapse-toggle:hover {
  background: var(--surface-2);
  color: var(--text-primary);
}

.collapse-toggle:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.collapse-icon {
  transition: transform 0.2s ease;
  flex-shrink: 0;
}

.collapse-icon.flipped {
  transform: rotate(180deg);
}

.sidebar-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.4);
  z-index: 190;
  display: none;
}

/* Mobile: off-canvas sidebar, backdrop only shown when open */
@media (max-width: 768px) {
  .sidebar {
    width: 264px;
    transform: translateX(-100%);
  }

  .sidebar.collapsed {
    width: 264px;
  }

  .sidebar.mobile-open {
    transform: translateX(0);
    box-shadow: var(--shadow-md);
  }

  .sidebar-backdrop {
    display: block;
  }
}
</style>
