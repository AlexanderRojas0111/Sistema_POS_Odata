# Correcciones para React Hooks

## Problemas identificados y soluciones:

### 1. frontend/src/hooks/usePWA.ts
**Problema**: React Hook useEffect has a missing dependency: 'registerServiceWorker'

**Solución**:
```typescript
useEffect(() => {
  if ('serviceWorker' in navigator) {
    registerServiceWorker();
  }
}, [registerServiceWorker]); // Agregar dependencia
```

### 2. frontend/src/components/UsersManagement.tsx
**Problema**: React Hook useEffect has a missing dependency: 'loadUsers'

**Solución**:
```typescript
useEffect(() => {
  loadUsers();
}, [loadUsers]); // Agregar dependencia
```

### 3. frontend/src/components/SalesModule.tsx
**Problema**: React Hook useEffect has a missing dependency: 'categories'

**Solución**:
```typescript
useEffect(() => {
  loadProducts();
}, [categories]); // Ya está incluido categories, verificar loadProducts
```

### 4. frontend/src/components/ReportsManagementFixed.tsx
**Problema**: React Hook useEffect has a missing dependency: 'generateReport'

**Solución**:
```typescript
useEffect(() => {
  generateReport();
}, [selectedReport, dateRange, generateReport]); // Agregar generateReport
```

### 5. frontend/src/components/ReportsManagement.tsx
**Problema**: React Hook useEffect has a missing dependency: 'generateReport'

**Solución**:
```typescript
useEffect(() => {
  generateReport();
}, [selectedReport, generateReport]); // Agregar generateReport
```

### 6. frontend/src/components/QRPaymentModal.tsx
**Problema**: React Hook useEffect has missing dependencies: 'generatePaymentQR' and 'paymentData'

**Solución**:
```typescript
useEffect(() => {
  if (isOpen && !paymentData) {
    generatePaymentQR();
  }
}, [isOpen, paymentData, generatePaymentQR]); // Agregar todas las dependencias
```

### 7. frontend/src/components/ProductsManagement.tsx
**Problema**: React Hook useEffect has a missing dependency: 'loadProducts'

**Solución**:
```typescript
useEffect(() => {
  loadProducts();
}, [loadProducts]); // Agregar dependencia
```

### 8. frontend/src/components/ProductRecommendations.tsx
**Problema**: React Hook useEffect has a missing dependency: 'loadRecommendations'

**Solución**:
```typescript
useEffect(() => {
  if (productId) {
    loadRecommendations()
  }
}, [productId, limit, loadRecommendations]) // Agregar loadRecommendations
```

### 9. frontend/src/components/MultiPaymentModal.tsx
**Problema**: React Hook useEffect has a missing dependency: 'loadSuggestions'

**Solución**:
```typescript
useEffect(() => {
  if (isOpen) {
    loadPaymentMethods();
    loadSuggestions();
  }
}, [isOpen, totalAmount, availableCash, loadSuggestions]); // Agregar loadSuggestions
```

### 10. frontend/src/components/AdvancedDashboard.tsx
**Problema**: React Hook useEffect has a missing dependency: 'fetchDashboardData'

**Solución**:
```typescript
useEffect(() => {
  fetchDashboardData();
  const interval = setInterval(() => {
    fetchDashboardData();
  }, 5 * 60 * 1000);

  return () => clearInterval(interval);
}, [fetchDashboardData]); // Agregar fetchDashboardData
```

## Recomendaciones generales:

1. **useCallback**: Envuelve las funciones que se usan como dependencias en useCallback para evitar re-renders innecesarios.

2. **useMemo**: Para valores calculados que dependen de otras variables.

3. **Ejemplo de patrón correcto**:
```typescript
const loadData = useCallback(async () => {
  // lógica de carga
}, [/* dependencias de la función */]);

useEffect(() => {
  loadData();
}, [loadData]);
```

4. **ESLint**: Asegúrate de que eslint-plugin-react-hooks esté configurado correctamente.
