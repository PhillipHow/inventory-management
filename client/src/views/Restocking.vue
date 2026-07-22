<template>
  <div class="restocking">
    <div class="page-header">
      <h2>{{ t('restocking.title') }}</h2>
      <p>{{ t('restocking.description') }}</p>
    </div>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <div v-if="successMessage" class="success-banner">{{ successMessage }}</div>

      <div class="card">
        <div class="budget-label">{{ t('restocking.budgetLabel') }}</div>
        <input
          type="range"
          class="budget-slider"
          min="0"
          max="500000"
          step="5000"
          v-model.number="budget"
        >
        <div class="budget-value">{{ currencySymbol }}{{ budget.toLocaleString() }}</div>
      </div>

      <div class="stats-grid">
        <div class="stat-card info">
          <div class="stat-label">{{ t('restocking.recommendedItems') }}</div>
          <div class="stat-value">{{ recommendations.length }}</div>
        </div>
        <div class="stat-card success">
          <div class="stat-label">{{ t('restocking.totalCost') }}</div>
          <div class="stat-value">{{ currencySymbol }}{{ totalCost.toLocaleString() }}</div>
        </div>
        <div class="stat-card info">
          <div class="stat-label">{{ t('restocking.budgetRemaining') }}</div>
          <div class="stat-value">{{ currencySymbol }}{{ budgetRemaining.toLocaleString() }}</div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.recommendations') }}</h3>
          <button
            class="btn-primary"
            :disabled="recommendations.length === 0"
            @click="placeOrder"
          >
            {{ t('restocking.placeOrder') }}
          </button>
        </div>
        <div v-if="candidates.length === 0" class="loading">{{ t('restocking.noItems') }}</div>
        <div v-else-if="recommendations.length === 0" class="loading">{{ t('restocking.noRecommendations') }}</div>
        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t('restocking.table.sku') }}</th>
                <th>{{ t('restocking.table.itemName') }}</th>
                <th>{{ t('restocking.table.restockQty') }}</th>
                <th>{{ t('restocking.table.unitCost') }}</th>
                <th>{{ t('restocking.table.lineTotal') }}</th>
                <th>{{ t('restocking.table.trend') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="rec in recommendations" :key="rec.sku">
                <td><strong>{{ rec.sku }}</strong></td>
                <td>{{ translateProductName(rec.name) }}</td>
                <td>{{ rec.restockQty }}</td>
                <td>{{ currencySymbol }}{{ rec.unit_cost.toFixed(2) }}</td>
                <td><strong>{{ currencySymbol }}{{ rec.lineTotal.toLocaleString() }}</strong></td>
                <td>
                  <span :class="['badge', rec.trend]">{{ t('trends.' + rec.trend) }}</span>
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
import { ref, computed, onMounted, watch } from 'vue'
import { api } from '../api'
import { useFilters } from '../composables/useFilters'
import { useI18n } from '../composables/useI18n'
import { useSubmittedOrders } from '../composables/useSubmittedOrders'

export default {
  name: 'Restocking',
  setup() {
    const { t, currentCurrency, translateProductName } = useI18n()
    const { addSubmittedOrder, RESTOCK_LEAD_TIME_DAYS } = useSubmittedOrders()
    const { selectedLocation, selectedCategory, getCurrentFilters } = useFilters()

    const currencySymbol = computed(() => {
      return currentCurrency.value === 'JPY' ? '¥' : '$'
    })

    const loading = ref(true)
    const error = ref(null)
    const allForecasts = ref([])
    const inventoryItems = ref([])
    const budget = ref(100000)
    const successMessage = ref(null)

    const loadData = async () => {
      try {
        loading.value = true
        const filters = getCurrentFilters()
        const [forecastsData, inventoryData] = await Promise.all([
          api.getDemandForecasts(),
          api.getInventory({
            warehouse: filters.warehouse,
            category: filters.category
          })
        ])
        allForecasts.value = forecastsData
        inventoryItems.value = inventoryData
      } catch (err) {
        error.value = 'Failed to load restocking data: ' + err.message
      } finally {
        loading.value = false
      }
    }

    watch([selectedLocation, selectedCategory], () => {
      loadData()
    })

    const candidates = computed(() => {
      const result = []
      for (const item of inventoryItems.value) {
        const forecast = allForecasts.value.find(f => f.item_sku === item.sku)
        if (!forecast) continue
        result.push({
          sku: item.sku,
          name: item.name,
          unit_cost: item.unit_cost,
          quantity_on_hand: item.quantity_on_hand,
          reorder_point: item.reorder_point,
          category: item.category,
          warehouse: item.warehouse,
          current_demand: forecast.current_demand,
          forecasted_demand: forecast.forecasted_demand,
          trend: forecast.trend
        })
      }
      return result
    })

    const recommendations = computed(() => {
      const scored = candidates.value
        .map(c => {
          const restockQty = Math.max(
            c.forecasted_demand - c.current_demand,
            c.reorder_point - c.quantity_on_hand,
            0
          )
          const lineTotal = restockQty * c.unit_cost
          const growth = (c.forecasted_demand - c.current_demand) / Math.max(c.current_demand, 1)
          const urgency = Math.max((c.reorder_point - c.quantity_on_hand) / Math.max(c.reorder_point, 1), 0)
          const score = growth + urgency
          return { ...c, restockQty, lineTotal, score }
        })
        .filter(c => c.restockQty > 0)
        .slice()
        .sort((a, b) => b.score - a.score)

      const included = []
      let runningCostSoFar = 0
      for (const item of scored) {
        if (runningCostSoFar + item.lineTotal <= budget.value) {
          included.push({
            sku: item.sku,
            name: item.name,
            restockQty: item.restockQty,
            unit_cost: item.unit_cost,
            lineTotal: item.lineTotal,
            trend: item.trend,
            category: item.category,
            warehouse: item.warehouse
          })
          runningCostSoFar += item.lineTotal
        }
      }
      return included
    })

    const totalCost = computed(() => recommendations.value.reduce((sum, r) => sum + r.lineTotal, 0))
    const budgetRemaining = computed(() => budget.value - totalCost.value)

    const placeOrder = () => {
      if (recommendations.value.length === 0) return

      const order = {
        id: 'RST-' + Date.now(),
        order_number: 'RST-' + Date.now(),
        customer: 'Internal Restock',
        items: recommendations.value.map(r => ({
          sku: r.sku,
          name: r.name,
          quantity: r.restockQty,
          unit_price: r.unit_cost
        })),
        status: 'Submitted',
        order_date: new Date().toISOString(),
        expected_delivery: new Date(Date.now() + RESTOCK_LEAD_TIME_DAYS * 24 * 60 * 60 * 1000).toISOString(),
        total_value: totalCost.value,
        warehouse: selectedLocation.value !== 'all' ? selectedLocation.value : 'All',
        category: selectedCategory.value !== 'all' ? selectedCategory.value : 'All',
        lead_time_days: RESTOCK_LEAD_TIME_DAYS
      }

      addSubmittedOrder(order)

      successMessage.value = t('restocking.orderPlaced')
      setTimeout(() => {
        successMessage.value = null
      }, 4000)
    }

    onMounted(loadData)

    return {
      t,
      loading,
      error,
      budget,
      candidates,
      recommendations,
      totalCost,
      budgetRemaining,
      currencySymbol,
      translateProductName,
      placeOrder,
      successMessage
    }
  }
}
</script>

<style scoped>
.budget-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.75rem;
}

.budget-slider {
  width: 100%;
  height: 8px;
  border-radius: 4px;
  accent-color: #2563eb;
  cursor: pointer;
  margin-bottom: 0.75rem;
}

.budget-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: #0f172a;
}

.success-banner {
  background: #d1fae5;
  color: #065f46;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  font-weight: 500;
}

.btn-primary {
  background: #2563eb;
  color: white;
  border: none;
  padding: 0.5rem 1.25rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background: #1d4ed8;
}

.btn-primary:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
}
</style>
