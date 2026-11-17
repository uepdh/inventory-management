<template>
  <div class="app">
    <AppSidebar
      @show-profile-details="showProfileDetails = true"
      @show-tasks="showTasks = true"
    />

    <div class="app-content" :class="{ collapsed }">
      <header class="top-bar">
        <button
          class="hamburger"
          type="button"
          :aria-label="t('nav.openMenu')"
          @click="toggleMobile"
        >
          <AppIcon name="bars3" :size="22" />
        </button>
        <!-- route.meta is empty on the first render, before the initial navigation resolves -->
        <h2 class="page-title">{{ route.meta.titleKey ? t(route.meta.titleKey) : '' }}</h2>
      </header>

      <FilterBar />

      <main class="main-content">
        <router-view />
      </main>
    </div>

    <ProfileDetailsModal
      :is-open="showProfileDetails"
      @close="showProfileDetails = false"
    />

    <TasksModal
      :is-open="showTasks"
      :tasks="tasks"
      @close="showTasks = false"
      @add-task="addTask"
      @delete-task="deleteTask"
      @toggle-task="toggleTask"
    />
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { api } from './api'
import { useAuth } from './composables/useAuth'
import { useI18n } from './composables/useI18n'
import { useSidebar } from './composables/useSidebar'
import FilterBar from './components/FilterBar.vue'
import AppSidebar from './components/AppSidebar.vue'
import AppIcon from './components/AppIcon.vue'
import ProfileDetailsModal from './components/ProfileDetailsModal.vue'
import TasksModal from './components/TasksModal.vue'

export default {
  name: 'App',
  components: {
    FilterBar,
    AppSidebar,
    AppIcon,
    ProfileDetailsModal,
    TasksModal
  },
  setup() {
    const { currentUser } = useAuth()
    const { t } = useI18n()
    const route = useRoute()
    const { collapsed, mobileOpen, toggleMobile, closeMobile } = useSidebar()
    const showProfileDetails = ref(false)
    const showTasks = ref(false)
    const apiTasks = ref([])

    // Merge mock tasks from currentUser with API tasks
    const tasks = computed(() => {
      return [...currentUser.value.tasks, ...apiTasks.value]
    })

    const loadTasks = async () => {
      try {
        apiTasks.value = await api.getTasks()
      } catch (err) {
        console.error('Failed to load tasks:', err)
      }
    }

    const addTask = async (taskData) => {
      try {
        const newTask = await api.createTask(taskData)
        // Add new task to the beginning of the array
        apiTasks.value.unshift(newTask)
      } catch (err) {
        console.error('Failed to add task:', err)
      }
    }

    const deleteTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const isMockTask = currentUser.value.tasks.some(t => t.id === taskId)

        if (isMockTask) {
          // Remove from mock tasks
          const index = currentUser.value.tasks.findIndex(t => t.id === taskId)
          if (index !== -1) {
            currentUser.value.tasks.splice(index, 1)
          }
        } else {
          // Remove from API tasks
          await api.deleteTask(taskId)
          apiTasks.value = apiTasks.value.filter(t => t.id !== taskId)
        }
      } catch (err) {
        console.error('Failed to delete task:', err)
      }
    }

    const toggleTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const mockTask = currentUser.value.tasks.find(t => t.id === taskId)

        if (mockTask) {
          // Toggle mock task status
          mockTask.status = mockTask.status === 'pending' ? 'completed' : 'pending'
        } else {
          // Toggle API task
          const updatedTask = await api.toggleTask(taskId)
          const index = apiTasks.value.findIndex(t => t.id === taskId)
          if (index !== -1) {
            apiTasks.value[index] = updatedTask
          }
        }
      } catch (err) {
        console.error('Failed to toggle task:', err)
      }
    }

    // Close the off-canvas mobile sidebar on Escape
    const handleKeydown = (event) => {
      if (event.key === 'Escape' && mobileOpen.value) {
        closeMobile()
      }
    }

    // Close the off-canvas mobile sidebar automatically after navigating,
    // otherwise the drawer stays open over the new page's content
    watch(() => route.path, () => {
      closeMobile()
    })

    onMounted(() => {
      loadTasks()
      window.addEventListener('keydown', handleKeydown)
    })

    onUnmounted(() => {
      window.removeEventListener('keydown', handleKeydown)
    })

    return {
      t,
      route,
      collapsed,
      mobileOpen,
      toggleMobile,
      showProfileDetails,
      showTasks,
      tasks,
      addTask,
      deleteTask,
      toggleTask
    }
  }
}
</script>

<style>
:root {
  color-scheme: dark;

  /* Surfaces - dark navy, darkest at the page level */
  --surface-0: #0b1220;
  --surface-1: #111a2e;
  --surface-2: #1a2540;
  --border: #243352;
  --border-strong: #35476e;

  /* Ink - every value clears 4.5:1 on all three surfaces */
  --text-primary: #e8edf7;
  --text-secondary: #9aa8c4;
  --text-tertiary: #8593b2;

  /* Accent - orange. NOTE: accent-contrast is navy, not white.
     White on #f97316 is only 2.80:1 and fails; navy is 6.68:1. */
  --accent: #f97316;
  --accent-hover: #fb923c;
  --accent-tint: #2a1a0e;
  --accent-contrast: #0b1220;

  /* Status inks - for badge text, status labels, trend indicators */
  --success: #34d399;
  --warning: #fbbf24;
  --danger: #f87171;
  --info: #60a5fa;

  /* Status tints - badge backgrounds; pair each with its ink above */
  --success-tint: #0c2a22;
  --warning-tint: #2e2205;
  --danger-tint: #2f1416;
  --info-tint: #0f2038;

  /* Chart series - fixed order, never cycled. Validated for
     colourblind separation against the card surface. */
  --series-1: #0d9488;
  --series-2: #3b82f6;
  --series-3: #7c3aed;
  --series-4: #e11d48;

  /* Shadows - opaque black on dark surfaces; the old slate-tinted
     shadows are invisible against navy */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.4);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.5);

  /* Type */
  --font-display: 'Space Grotesk', 'Segoe UI', system-ui, sans-serif;
  --font-body: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;

  --space-1: 4px; --space-2: 8px; --space-3: 12px; --space-4: 16px;
  --space-5: 24px; --space-6: 32px; --space-8: 48px; --space-10: 64px;
  --radius-sm: 6px; --radius-md: 10px; --radius-lg: 16px;
  --text-xs: 12px; --text-sm: 13px; --text-base: 15px;
  --text-lg: 18px; --text-xl: 24px; --text-2xl: 30px;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-body);
  background: var(--surface-0);
  color: var(--text-primary);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

h1, h2, h3, h4 {
  font-family: var(--font-display);
}

.app {
  min-height: 100vh;
}

.app-content {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  margin-left: 264px;
  transition: margin-left 0.2s ease;
}

.app-content.collapsed {
  margin-left: 76px;
}

.top-bar {
  height: 64px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: 0 var(--space-6);
  background: var(--surface-1);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 90;
}

.page-title {
  font-size: var(--text-lg);
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.025em;
}

.hamburger {
  display: none;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: none;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  cursor: pointer;
}

.hamburger:hover {
  background: var(--surface-2);
  color: var(--text-primary);
}

.hamburger:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.main-content {
  flex: 1;
  width: 100%;
  padding: var(--space-5) var(--space-6);
}

@media (max-width: 768px) {
  .app-content,
  .app-content.collapsed {
    margin-left: 0;
  }

  .hamburger {
    display: flex;
  }
}

.page-header {
  margin-bottom: 1.5rem;
}

.page-header h2 {
  font-size: 1.875rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.375rem;
  letter-spacing: -0.025em;
}

.page-header p {
  color: var(--text-secondary);
  font-size: 0.938rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-4);
  margin-bottom: var(--space-5);
}

.stat-card {
  background: var(--surface-1);
  padding: var(--space-5);
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
  transition: border-color 0.2s ease;
}

.stat-card:hover {
  border-color: var(--border-strong);
}

.stat-label {
  color: var(--text-tertiary);
  font-size: var(--text-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: var(--space-2);
}

.stat-value {
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.025em;
  line-height: 1.1;
}

.stat-sub {
  margin-top: var(--space-2);
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.stat-sub.positive {
  color: var(--success);
}

.stat-sub.negative {
  color: var(--danger);
}

.stat-card.warning .stat-value {
  color: var(--warning);
}

.stat-card.success .stat-value {
  color: var(--success);
}

.stat-card.danger .stat-value {
  color: var(--danger);
}

.stat-card.info .stat-value {
  color: var(--accent);
}

.card {
  background: var(--surface-1);
  border-radius: var(--radius-md);
  padding: var(--space-5);
  border: 1px solid var(--border);
  margin-bottom: var(--space-5);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-3);
  border-bottom: 1px solid var(--border);
}

.card-title {
  font-family: var(--font-display);
  font-size: var(--text-lg);
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.025em;
}

.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: var(--surface-2);
  border-top: 1px solid var(--border-strong);
  border-bottom: 1px solid var(--border-strong);
}

th {
  text-align: left;
  padding: var(--space-3);
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
}

td {
  padding: var(--space-3);
  border-top: 1px solid var(--border);
  color: var(--text-primary);
  font-size: 0.875rem;
}

.nowrap {
  white-space: nowrap;
}

tbody tr {
  transition: background-color 0.15s ease;
}

tbody tr:hover {
  background: var(--surface-2);
}

.badge {
  display: inline-block;
  padding: 0.313rem 0.75rem;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  white-space: nowrap;
}

.badge.success {
  background: var(--success-tint);
  color: var(--success);
}

.badge.warning {
  background: var(--warning-tint);
  color: var(--warning);
}

.badge.danger {
  background: var(--danger-tint);
  color: var(--danger);
}

.badge.info {
  background: var(--info-tint);
  color: var(--info);
}

.badge.increasing {
  background: var(--success-tint);
  color: var(--success);
}

.badge.decreasing {
  background: var(--danger-tint);
  color: var(--danger);
}

.badge.stable {
  /* No neutral/indigo token exists in the new palette; info is the
     closest hue family and still reads as "steady state" rather
     than a positive/negative trend. */
  background: var(--info-tint);
  color: var(--info);
}

.badge.high {
  background: var(--danger-tint);
  color: var(--danger);
}

.badge.medium {
  background: var(--warning-tint);
  color: var(--warning);
}

.badge.low {
  background: var(--info-tint);
  color: var(--info);
}

.loading {
  text-align: center;
  padding: 3rem;
  color: var(--text-secondary);
  font-size: 0.938rem;
}

.error {
  background: var(--danger-tint);
  border: 1px solid var(--danger);
  color: var(--danger);
  padding: 1rem;
  border-radius: 8px;
  margin: 1rem 0;
  font-size: 0.938rem;
}

@media (max-width: 768px) {
  .card,
  .stat-card {
    padding: var(--space-4);
  }

  .stats-grid {
    gap: var(--space-3);
  }
}
</style>
