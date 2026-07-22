import { ref } from 'vue'

// Shared submitted-orders state (singleton pattern, same as useFilters).
// Frontend-only: persists across route navigation, cleared on full page reload.
const submittedOrders = ref([])

// Fixed delivery lead time (days) for restocking orders.
export const RESTOCK_LEAD_TIME_DAYS = 14

export function useSubmittedOrders() {
  // Add a submitted restocking order. The order object is shaped like an
  // entry from orders.json so the Orders view can render it with the same
  // helpers (order_number, customer, items, status, dates, total_value).
  const addSubmittedOrder = (order) => {
    submittedOrders.value.push(order)
  }

  return {
    submittedOrders,
    addSubmittedOrder,
    RESTOCK_LEAD_TIME_DAYS
  }
}
