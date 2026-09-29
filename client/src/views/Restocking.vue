<template>
  <div class="restocking">
    <div class="page-header">
      <p>{{ t('restocking.description') }}</p>
    </div>

    <div class="card budget-card">
      <label class="budget-label" for="budget-slider">{{ t('restocking.budgetLabel') }}</label>
      <div class="budget-control">
        <input
          id="budget-slider"
          type="range"
          min="0"
          max="50000"
          step="250"
          v-model.number="budget"
          @input="onBudgetInput"
          @change="onBudgetChange"
          class="budget-slider"
        />
        <span class="budget-value">{{ currencySymbol }}{{ budget.toLocaleString() }}</span>
      </div>
    </div>

    <div v-if="orderSuccessMessage" class="success-banner">{{ orderSuccessMessage }}</div>
    <div v-if="orderErrorMessage" class="error">{{ orderErrorMessage }}</div>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <div class="stats-grid">
        <div class="stat-card info">
          <div class="stat-label">{{ t('restocking.totalCost') }}</div>
          <div class="stat-value">{{ currencySymbol }}{{ totalEstimatedCost.toLocaleString() }}</div>
        </div>
        <div class="stat-card success">
          <div class="stat-label">{{ t('restocking.remainingBudget') }}</div>
          <div class="stat-value">{{ currencySymbol }}{{ remainingBudget.toLocaleString() }}</div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.recommendedItems') }} ({{ items.length }})</h3>
          <button
            class="place-order-btn"
            :disabled="items.length === 0 || placingOrder"
            @click="placeOrder"
          >
            {{ placingOrder ? t('restocking.placingOrder') : t('restocking.placeOrder') }}
          </button>
        </div>

        <div v-if="items.length === 0" class="empty-state">{{ t('restocking.noRecommendations') }}</div>
        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t('restocking.table.sku') }}</th>
                <th>{{ t('restocking.table.itemName') }}</th>
                <th>{{ t('restocking.table.currentDemand') }}</th>
                <th>{{ t('restocking.table.forecastedDemand') }}</th>
                <th>{{ t('restocking.table.trend') }}</th>
                <th>{{ t('restocking.table.unitCost') }}</th>
                <th>{{ t('restocking.table.leadTime') }}</th>
                <th>{{ t('restocking.table.quantity') }}</th>
                <th>{{ t('restocking.table.estimatedCost') }}</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in items" :key="item.item_sku">
                <td><strong>{{ item.item_sku }}</strong></td>
                <td>{{ item.item_name }}</td>
                <td>{{ item.current_demand }}</td>
                <td><strong>{{ item.forecasted_demand }}</strong></td>
                <td>
                  <span :class="['badge', item.trend]">{{ t(`trends.${item.trend}`) }}</span>
                </td>
                <td>{{ currencySymbol }}{{ item.unit_cost.toLocaleString() }}</td>
                <td>{{ t('restocking.leadTimeDays', { days: item.lead_time_days }) }}</td>
                <td>{{ item.recommended_quantity }}</td>
                <td>{{ currencySymbol }}{{ item.estimated_cost.toLocaleString() }}</td>
                <td>
                  <span :class="['badge', item.fully_funded ? 'success' : 'warning']">
                    {{ item.fully_funded ? t('restocking.fullyFunded') : t('restocking.partiallyFunded') }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'

export default {
  name: 'Restocking',
  setup() {
    const { t, currentCurrency } = useI18n()

    const currencySymbol = computed(() => {
      return currentCurrency.value === 'JPY' ? '¥' : '$'
    })

    const budget = ref(5000)
    const loading = ref(true)
    const error = ref(null)
    const items = ref([])
    const totalEstimatedCost = ref(0)
    const remainingBudget = ref(0)

    const placingOrder = ref(false)
    const orderSuccessMessage = ref(null)
    const orderErrorMessage = ref(null)

    const loadRecommendations = async () => {
      try {
        loading.value = true
        error.value = null
        const response = await api.getRestockRecommendations(budget.value)
        items.value = response.items
        totalEstimatedCost.value = response.total_estimated_cost
        remainingBudget.value = response.remaining_budget
      } catch (err) {
        error.value = 'Failed to load restocking recommendations: ' + err.message
      } finally {
        loading.value = false
      }
    }

    // Live-update the displayed number while dragging, but only refetch on release (change event)
    const onBudgetInput = () => {
      // budget already updated via v-model; no fetch here
    }

    const onBudgetChange = () => {
      loadRecommendations()
    }

    const placeOrder = async () => {
      orderSuccessMessage.value = null
      orderErrorMessage.value = null
      placingOrder.value = true
      try {
        const orderData = {
          budget: budget.value,
          items: items.value
            .filter(i => i.recommended_quantity > 0)
            .map(i => ({ item_sku: i.item_sku, quantity: i.recommended_quantity }))
        }
        await api.createRestockingOrder(orderData)
        orderSuccessMessage.value = t('restocking.orderSuccess')
      } catch (err) {
        orderErrorMessage.value = t('restocking.orderError')
        console.error('Failed to submit restock order:', err)
      } finally {
        placingOrder.value = false
      }
    }

    onMounted(loadRecommendations)

    return {
      t,
      currencySymbol,
      budget,
      loading,
      error,
      items,
      totalEstimatedCost,
      remainingBudget,
      placingOrder,
      orderSuccessMessage,
      orderErrorMessage,
      onBudgetInput,
      onBudgetChange,
      placeOrder
    }
  }
}
</script>

<style scoped>
.budget-card {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.budget-label {
  color: #64748b;
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.budget-control {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.budget-slider {
  flex: 1;
  accent-color: #2563eb;
}

.budget-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
  min-width: 120px;
  text-align: right;
}

.place-order-btn {
  background: #2563eb;
  color: white;
  border: none;
  padding: 0.5rem 1.25rem;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: background 0.2s ease;
}

.place-order-btn:hover:not(:disabled) {
  background: #1d4ed8;
}

.place-order-btn:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #64748b;
  font-size: 0.938rem;
}

.success-banner {
  background: #ecfdf5;
  border: 1px solid #a7f3d0;
  color: #065f46;
  padding: 1rem;
  border-radius: 8px;
  margin: 1rem 0;
  font-size: 0.938rem;
}
</style>
