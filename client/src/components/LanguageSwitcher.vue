<template>
  <div class="language-switcher" :class="{ collapsed: collapsed }">
    <button
      ref="triggerRef"
      class="language-button"
      :title="collapsed ? localeName : null"
      :aria-label="collapsed ? localeName : null"
      @click="toggleDropdown"
      @blur="handleBlur"
    >
      <svg
        width="20"
        height="20"
        viewBox="0 0 20 20"
        fill="none"
        class="globe-icon"
      >
        <circle cx="10" cy="10" r="7.5" stroke="currentColor" stroke-width="1.5"/>
        <path d="M3 10H17" stroke="currentColor" stroke-width="1.5"/>
        <path d="M10 3C10 3 7.5 5.5 7.5 10C7.5 14.5 10 17 10 17" stroke="currentColor" stroke-width="1.5"/>
        <path d="M10 3C10 3 12.5 5.5 12.5 10C12.5 14.5 10 17 10 17" stroke="currentColor" stroke-width="1.5"/>
      </svg>
      <span v-if="!collapsed" class="language-label">{{ localeName }}</span>
      <svg
        v-if="!collapsed"
        class="chevron"
        :class="{ 'chevron-open': isDropdownOpen }"
        width="16"
        height="16"
        viewBox="0 0 16 16"
        fill="none"
      >
        <path d="M4 6L8 10L12 6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      </svg>
    </button>

    <!--
      Collapsed sidebar rail clips an absolutely-positioned menu via its
      `overflow: hidden`, so escape it to <body> and anchor to the right of
      the rail with measured coordinates. Expanded state keeps the original
      absolute positioning (Teleport disabled -> renders in place).
    -->
    <Teleport to="body" :disabled="!collapsed">
      <div
        v-if="isDropdownOpen"
        class="dropdown-menu"
        :class="placementClass"
        :style="collapsed ? floatingStyle : null"
      >
        <button
          v-for="locale in availableLocales"
          :key="locale"
          class="dropdown-item"
          :class="{ active: currentLocale === locale }"
          @mousedown.prevent="selectLanguage(locale)"
        >
          <span class="language-name">{{ getLanguageName(locale) }}</span>
          <svg
            v-if="currentLocale === locale"
            width="18"
            height="18"
            viewBox="0 0 18 18"
            fill="none"
            class="check-icon"
          >
            <path d="M4 9L7.5 12.5L14 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { useI18n } from '../composables/useI18n'
import { useSidebar } from '../composables/useSidebar'

const props = defineProps({
  placement: {
    type: String,
    default: 'down-right'
  }
})

const { currentLocale, setLocale, availableLocales, localeName } = useI18n()
const { collapsed } = useSidebar()

const isDropdownOpen = ref(false)
const triggerRef = ref(null)
const floatingStyle = ref({})

const placementClass = computed(() => (props.placement === 'up-left' ? 'placement-up-left' : ''))

// Anchor the teleported menu to the right of the collapsed rail, bottom-
// aligned with the trigger button, using the button's live screen position.
const updateFloatingPosition = () => {
  if (!collapsed.value || !triggerRef.value) return
  const rect = triggerRef.value.getBoundingClientRect()
  floatingStyle.value = {
    position: 'fixed',
    top: 'auto',
    right: 'auto',
    left: `${rect.right + 8}px`,
    bottom: `${window.innerHeight - rect.bottom}px`
  }
}

const languageNames = {
  en: 'English',
  ja: '日本語'
}

const getLanguageName = (locale) => {
  return languageNames[locale] || locale
}

const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value
  if (isDropdownOpen.value) {
    nextTick(updateFloatingPosition)
  }
}

const handleBlur = () => {
  // Delay to allow mousedown events on dropdown items to fire first
  setTimeout(() => {
    isDropdownOpen.value = false
  }, 200)
}

const selectLanguage = (locale) => {
  setLocale(locale)
  isDropdownOpen.value = false
}
</script>

<style scoped>
.language-switcher {
  position: relative;
}

.language-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.875rem;
  background: var(--surface-1);
  border: 1px solid var(--border);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: inherit;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.language-button:hover {
  background: var(--surface-2);
  border-color: var(--border-strong);
}

/*
  Collapsed sidebar rail is 76px; the expanded button's space-3 horizontal
  padding plus its border leaves too little room once the label/chevron are
  gone, so drop to space-2 (matching the nav-link's vertical rhythm) and
  centre the icon in the full-width button.
*/
.language-switcher.collapsed .language-button {
  width: 100%;
  justify-content: center;
  padding: var(--space-2);
}

.globe-icon {
  color: var(--text-secondary);
  flex-shrink: 0;
}

.language-label {
  font-weight: 500;
}

.chevron {
  color: var(--text-secondary);
  transition: transform 0.2s ease;
  flex-shrink: 0;
}

.chevron-open {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  min-width: 160px;
}

.dropdown-menu.placement-up-left {
  top: auto;
  right: auto;
  bottom: calc(100% + 0.5rem);
  left: 0;
}

.dropdown-menu {
  background: var(--surface-1);
  border: 1px solid var(--border);
  border-radius: 10px;
  box-shadow: var(--shadow-md);
  z-index: 1000;
  overflow: hidden;
}

.dropdown-item {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: none;
  border: none;
  text-align: left;
  cursor: pointer;
  transition: background 0.15s ease;
  font-family: inherit;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.dropdown-item:hover {
  background: var(--surface-2);
}

.dropdown-item.active {
  background: var(--accent-tint);
  color: var(--accent);
}

.language-name {
  flex: 1;
}

.check-icon {
  color: var(--accent);
  flex-shrink: 0;
}
</style>
