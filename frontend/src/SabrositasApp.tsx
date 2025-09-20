import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import Header from './components/Header';
import HeroSection from './components/HeroSection';
import MenuSection from './components/MenuSection';
import BranchesSection from './components/BranchesSection';
import ContactSection from './components/ContactSection';
import Footer from './components/Footer';
import CartSidebar from './components/CartSidebar';
import CartUpdater from './components/CartUpdater';
import { EnhancedCartProvider } from './context/EnhancedCartContext';

const SabrositasApp: React.FC = () => {
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [_searchQuery, setSearchQuery] = useState('');
  const [cartItemCount, setCartItemCount] = useState(0);

  // Manejar scroll suave
  useEffect(() => {
    const handleSmoothScroll = (e: Event) => {
      const target = e.target as HTMLAnchorElement;
      if (target.hash) {
        e.preventDefault();
        const element = document.querySelector(target.hash);
        if (element) {
          element.scrollIntoView({ behavior: 'smooth' });
        }
      }
    };

    document.addEventListener('click', handleSmoothScroll);
    return () => document.removeEventListener('click', handleSmoothScroll);
  }, []);

  // Manejar búsqueda
  const handleSearch = (query: string) => {
    setSearchQuery(query);
    // Scroll a la sección del menú
    const menuSection = document.getElementById('menu');
    if (menuSection) {
      menuSection.scrollIntoView({ behavior: 'smooth' });
    }
  };

  // Manejar navegación a secciones
  const handleNavigateToSection = (section: string) => {
    const element = document.getElementById(section);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  // Manejar apertura/cierre del carrito
  const toggleCart = () => {
    setIsCartOpen(!isCartOpen);
  };

  const closeCart = () => {
    setIsCartOpen(false);
  };

  return (
    <div className="min-h-screen bg-white">
      <EnhancedCartProvider>
        {/* Cart Updater para sincronizar el contador */}
        <CartUpdater onCartUpdate={setCartItemCount} />
        
        {/* Header */}
        <Header 
          onSearch={handleSearch}
          onNavigateToSection={handleNavigateToSection}
          onToggleCart={toggleCart}
          cartItemCount={cartItemCount}
        />

        {/* Contenido principal */}
        <main>
          {/* Hero Section */}
          <HeroSection />

          {/* Menu Section */}
          <MenuSection />

          {/* Branches Section */}
          <BranchesSection />

          {/* Contact Section */}
          <ContactSection />
        </main>

        {/* Footer */}
        <Footer />

        {/* Cart Sidebar */}
        <CartSidebar 
          isOpen={isCartOpen}
          onClose={closeCart}
        />

        {/* Botón flotante del carrito para móviles */}
        <motion.button
          onClick={toggleCart}
          className="fixed bottom-6 right-6 lg:hidden bg-gradient-to-r from-sabrositas-primary to-sabrositas-accent text-white p-4 rounded-full shadow-large z-40"
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 1, duration: 0.5 }}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-2.5 5M7 13l2.5 5m0 0L17 13m0 0l2.5 5M17 13l-2.5 5" />
          </svg>
        </motion.button>

        {/* Indicador de carga */}
        <motion.div
          className="fixed top-0 left-0 w-full h-1 bg-gradient-to-r from-sabrositas-primary via-sabrositas-accent to-sabrositas-secondary z-50"
          initial={{ scaleX: 0 }}
          animate={{ scaleX: 1 }}
          transition={{ duration: 2, ease: 'easeOut' }}
          style={{ transformOrigin: 'left' }}
        />

        {/* Notificación de bienvenida */}
        <motion.div
          className="fixed top-24 right-4 bg-white rounded-xl shadow-large p-4 border-l-4 border-sabrositas-primary z-40 max-w-sm"
          initial={{ opacity: 0, x: 300 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 2, duration: 0.6 }}
          exit={{ opacity: 0, x: 300 }}
        >
          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 bg-sabrositas-primary/10 rounded-lg flex items-center justify-center flex-shrink-0">
              <span className="text-sabrositas-primary text-sm">🍽️</span>
            </div>
            <div>
              <h4 className="font-semibold text-sabrositas-neutral-dark text-sm">
                ¡Bienvenido a Sabrositas!
              </h4>
              <p className="text-gray-600 text-xs mt-1">
                Descubre nuestras deliciosas arepas cuadradas
              </p>
            </div>
          </div>
        </motion.div>
      </EnhancedCartProvider>
    </div>
  );
};

export default SabrositasApp;
