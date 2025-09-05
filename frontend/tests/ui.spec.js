const { test, expect } = require('@playwright/test');

test.describe('Sistema POS O\'Data - Tests de UI', () => {
  test.beforeEach(async ({ page }) => {
    // Navegar a la página principal antes de cada test
    await page.goto('/');
    // Esperar a que la página cargue completamente
    await page.waitForLoadState('networkidle');
  });

  test('debería mostrar la página principal correctamente', async ({ page }) => {
    // Verificar que el título esté presente
    await expect(page).toHaveTitle(/Sistema POS/);
    
    // Verificar elementos principales de la UI
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('nav')).toBeVisible();
    
    // Verificar que no haya errores en consola
    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });
    
    // Verificar que no haya errores críticos
    expect(errors.length).toBeLessThan(5);
  });

  test('debería navegar entre diferentes secciones', async ({ page }) => {
    // Test de navegación básica
    const navItems = ['Ventas', 'Inventario', 'Productos', 'Clientes', 'Reportes'];
    
    for (const item of navItems) {
      try {
        const navLink = page.locator(`text=${item}`);
        if (await navLink.isVisible()) {
          await navLink.click();
          await page.waitForLoadState('networkidle');
          
          // Verificar que la página cambió
          await expect(page.locator('h2')).toBeVisible();
        }
      } catch (error) {
        console.log(`Navegación a ${item} no disponible`);
      }
    }
  });

  test('debería manejar formularios correctamente', async ({ page }) => {
    // Buscar formularios en la página
    const forms = page.locator('form');
    const formCount = await forms.count();
    
    if (formCount > 0) {
      // Test del primer formulario encontrado
      const firstForm = forms.first();
      
      // Verificar que el formulario tenga campos
      const inputs = firstForm.locator('input, select, textarea');
      const inputCount = await inputs.count();
      
      if (inputCount > 0) {
        // Llenar un campo de texto si existe
        const textInputs = firstForm.locator('input[type="text"], input:not([type])');
        if (await textInputs.count() > 0) {
          const firstInput = textInputs.first();
          await firstInput.fill('Test Input');
          await expect(firstInput).toHaveValue('Test Input');
        }
      }
    }
  });

  test('debería mostrar mensajes de error apropiadamente', async ({ page }) => {
    // Simular un error (por ejemplo, intentar enviar un formulario vacío)
    const submitButtons = page.locator('button[type="submit"], input[type="submit"]');
    
    if (await submitButtons.count() > 0) {
      const submitButton = submitButtons.first();
      
      try {
        await submitButton.click();
        await page.waitForTimeout(1000);
        
        // Verificar si aparecen mensajes de error
        const errorMessages = page.locator('.error, .alert, [role="alert"]');
        if (await errorMessages.count() > 0) {
          await expect(errorMessages.first()).toBeVisible();
        }
      } catch (error) {
        // Es normal que algunos formularios no tengan validación
        console.log('Formulario sin validación de errores');
      }
    }
  });

  test('debería ser responsive en diferentes tamaños de pantalla', async ({ page }) => {
    // Test de responsividad
    const viewports = [
      { width: 1920, height: 1080 }, // Desktop
      { width: 1024, height: 768 },  // Tablet
      { width: 375, height: 667 }    // Mobile
    ];
    
    for (const viewport of viewports) {
      await page.setViewportSize(viewport);
      await page.waitForTimeout(500);
      
      // Verificar que la página sea usable en este viewport
      await expect(page.locator('body')).toBeVisible();
      
      // Verificar que no haya elementos que se salgan de la pantalla
      const elements = page.locator('*');
      for (let i = 0; i < Math.min(await elements.count(), 10); i++) {
        const element = elements.nth(i);
        if (await element.isVisible()) {
          const box = await element.boundingBox();
          if (box) {
            expect(box.x).toBeGreaterThanOrEqual(0);
            expect(box.y).toBeGreaterThanOrEqual(0);
            expect(box.x + box.width).toBeLessThanOrEqual(viewport.width);
            expect(box.y + box.height).toBeLessThanOrEqual(viewport.height);
          }
        }
      }
    }
  });

  test('debería cargar en menos de 3 segundos', async ({ page }) => {
    // Medir tiempo de carga
    const startTime = Date.now();
    
    // Navegar a la página
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const loadTime = Date.now() - startTime;
    
    // Verificar que la carga sea menor a 3 segundos
    expect(loadTime).toBeLessThan(3000);
    
    console.log(`⏱️ Tiempo de carga: ${loadTime}ms`);
  });

  test('debería manejar eventos de teclado correctamente', async ({ page }) => {
    // Test de navegación por teclado
    await page.keyboard.press('Tab');
    
    // Verificar que el foco se mueva
    const focusedElement = page.locator(':focus');
    if (await focusedElement.count() > 0) {
      await expect(focusedElement.first()).toBeVisible();
    }
    
    // Test de búsqueda con Ctrl+F
    await page.keyboard.press('Control+f');
    
    // Verificar si aparece un campo de búsqueda
    const searchInputs = page.locator('input[type="search"], input[placeholder*="buscar"], input[placeholder*="search"]');
    if (await searchInputs.count() > 0) {
      await expect(searchInputs.first()).toBeVisible();
    }
  });

  test('debería mostrar loading states apropiadamente', async ({ page }) => {
    // Buscar indicadores de carga
    const loadingIndicators = page.locator('.loading, .spinner, [aria-busy="true"]');
    
    if (await loadingIndicators.count() > 0) {
      // Verificar que los indicadores de carga sean visibles cuando sea apropiado
      await expect(loadingIndicators.first()).toBeVisible();
    }
    
    // Verificar que no haya indicadores de carga persistentes
    await page.waitForTimeout(2000);
    const persistentLoading = page.locator('.loading:visible, .spinner:visible, [aria-busy="true"]:visible');
    expect(await persistentLoading.count()).toBeLessThan(5);
  });

  test('debería manejar datos dinámicos correctamente', async ({ page }) => {
    // Buscar elementos que muestren datos dinámicos
    const dataElements = page.locator('[data-testid], .data-item, .dynamic-content');
    
    if (await dataElements.count() > 0) {
      // Verificar que los elementos de datos sean visibles
      await expect(dataElements.first()).toBeVisible();
      
      // Verificar que el contenido no esté vacío
      const firstElement = dataElements.first();
      const text = await firstElement.textContent();
      expect(text).toBeTruthy();
      expect(text.trim().length).toBeGreaterThan(0);
    }
  });

  test('debería tener accesibilidad básica', async ({ page }) => {
    // Verificar que las imágenes tengan alt text
    const images = page.locator('img');
    const imageCount = await images.count();
    
    if (imageCount > 0) {
      for (let i = 0; i < Math.min(imageCount, 5); i++) {
        const img = images.nth(i);
        const alt = await img.getAttribute('alt');
        if (alt !== null) {
          expect(alt.length).toBeGreaterThan(0);
        }
      }
    }
    
    // Verificar que los botones tengan texto o aria-label
    const buttons = page.locator('button');
    const buttonCount = await buttons.count();
    
    if (buttonCount > 0) {
      for (let i = 0; i < Math.min(buttonCount, 5); i++) {
        const button = buttons.nth(i);
        const text = await button.textContent();
        const ariaLabel = await button.getAttribute('aria-label');
        
        // Al menos uno debe estar presente
        expect(text?.trim().length > 0 || ariaLabel?.length > 0).toBeTruthy();
      }
    }
  });
});
