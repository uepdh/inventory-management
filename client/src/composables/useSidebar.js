import { ref, computed } from 'vue'

// Shared sidebar state (singleton pattern, matches useFilters.js/useI18n.js)
const STORAGE_KEY = 'sidebar-collapsed'

// Load persisted collapsed state, default to expanded (false) if unset.
// This is the user's standing preference and only applies on large screens.
const savedCollapsed = localStorage.getItem(STORAGE_KEY)
const manualCollapsed = ref(savedCollapsed === 'true')

// Medium screens (tablets, narrow laptops) auto-collapse to icons-only so the
// content column keeps its width. Below 768px App.vue switches to the
// off-canvas drawer instead, so the band starts at 769px to match that CSS.
const MEDIUM_SCREEN_QUERY = '(min-width: 769px) and (max-width: 1024px)'
const mediumQuery = window.matchMedia(MEDIUM_SCREEN_QUERY)
const isMediumScreen = ref(mediumQuery.matches)

// A toggle made while in the medium band overrides the auto-collapse for the
// rest of the session (null = follow the auto rule). It is deliberately not
// persisted: the saved preference belongs to large screens, and resizing out
// of the band clears the override so re-entering it starts icons-only again.
const mediumOverride = ref(null)

mediumQuery.addEventListener('change', (event) => {
  isMediumScreen.value = event.matches
  mediumOverride.value = null
})

// Effective state read by App.vue and AppSidebar.vue. Neither component needs
// to know which rule produced it.
const collapsed = computed(() => {
  if (isMediumScreen.value) {
    return mediumOverride.value ?? true
  }
  return manualCollapsed.value
})

// Off-canvas mobile state - not persisted, always starts closed
const mobileOpen = ref(false)

export function useSidebar() {
  const toggleCollapsed = () => {
    if (isMediumScreen.value) {
      mediumOverride.value = !collapsed.value
      return
    }
    manualCollapsed.value = !manualCollapsed.value
    localStorage.setItem(STORAGE_KEY, String(manualCollapsed.value))
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
