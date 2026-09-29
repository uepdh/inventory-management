import { ref } from 'vue'

// Shared sidebar state (singleton pattern, matches useFilters.js/useI18n.js)
const STORAGE_KEY = 'sidebar-collapsed'

// Load persisted collapsed state, default to expanded (false) if unset
const savedCollapsed = localStorage.getItem(STORAGE_KEY)
const collapsed = ref(savedCollapsed === 'true')

// Off-canvas mobile state - not persisted, always starts closed
const mobileOpen = ref(false)

export function useSidebar() {
  const toggleCollapsed = () => {
    collapsed.value = !collapsed.value
    localStorage.setItem(STORAGE_KEY, String(collapsed.value))
  }

  const openMobile = () => {
    mobileOpen.value = true
  }

  const closeMobile = () => {
    mobileOpen.value = false
  }

  const toggleMobile = () => {
    mobileOpen.value = !mobileOpen.value
  }

  return {
    collapsed,
    toggleCollapsed,
    mobileOpen,
    openMobile,
    closeMobile,
    toggleMobile
  }
}
