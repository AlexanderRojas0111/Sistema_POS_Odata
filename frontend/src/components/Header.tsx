import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShoppingCart, Menu, X, Search, MapPin, Phone } from 'lucide-react';

interface HeaderProps {
  onSearch?: (query: string) => void;
  onNavigateToSection?: (section: string) => void;
  onToggleCart?: () => void;
  cartItemCount?: number;
}

const Header: React.FC<HeaderProps> = ({ onSearch, onNavigateToSection, onToggleCart, cartItemCount = 0 }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Detectar scroll para cambiar el estilo del header
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (onSearch && searchQuery.trim()) {
      onSearch(searchQuery.trim());
    }
  };

  const handleNavigation = (section: string) => {
    if (onNavigateToSection) {
      onNavigateToSection(section);
    }
    setIsMenuOpen(false);
  };

  const navItems = [
    { id: 'menu', label: 'Menú', href: '#menu' },
    { id: 'sucursales', label: 'Sucursales', href: '#sucursales' },
    { id: 'contacto', label: 'Contacto', href: '#contacto' },
  ];

  return (
    <motion.header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled 
          ? 'bg-white/95 backdrop-blur-custom shadow-soft' 
          : 'bg-transparent'
      }`}
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
    >
      <div className="container-custom">
        <div className="flex items-center justify-between h-20">
          {/* Logo */}
          <motion.div
            className="flex items-center space-x-3"
            whileHover={{ scale: 1.05 }}
            transition={{ duration: 0.2 }}
          >
            <div className="w-12 h-12 bg-gradient-to-r from-sabrositas-primary to-sabrositas-accent rounded-xl flex items-center justify-center">
              <span className="text-white font-bold text-xl font-dancing">S</span>
            </div>
            <div>
              <h1 className={`text-2xl font-bold gradient-text ${isScrolled ? 'text-sabrositas-neutral-dark' : 'text-white'}`}>
                Sabrositas
              </h1>
              <p className={`text-sm font-dancing ${isScrolled ? 'text-sabrositas-primary' : 'text-sabrositas-secondary'}`}>
                Las arepas cuadradas
              </p>
            </div>
          </motion.div>

          {/* Navegación Desktop */}
          <nav className="hidden lg:flex items-center space-x-8">
            {navItems.map((item) => (
              <motion.button
                key={item.id}
                onClick={() => handleNavigation(item.id)}
                className={`font-medium transition-colors duration-300 ${
                  isScrolled 
                    ? 'text-sabrositas-neutral-dark hover:text-sabrositas-primary' 
                    : 'text-white hover:text-sabrositas-secondary'
                }`}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                {item.label}
              </motion.button>
            ))}
          </nav>

          {/* Barra de búsqueda Desktop */}
          <div className="hidden md:flex items-center space-x-4">
            <form onSubmit={handleSearch} className="relative">
              <input
                type="text"
                placeholder="Buscar arepas..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className={`w-64 px-4 py-2 pl-10 rounded-xl border transition-all duration-300 ${
                  isScrolled
                    ? 'bg-white border-gray-200 focus:border-sabrositas-primary'
                    : 'bg-white/90 border-white/20 focus:border-sabrositas-secondary'
                }`}
              />
              <Search className={`absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 ${
                isScrolled ? 'text-gray-400' : 'text-gray-500'
              }`} />
            </form>
          </div>

          {/* Carrito y Menú Móvil */}
          <div className="flex items-center space-x-4">
            {/* Botón del carrito */}
            <motion.button
              onClick={onToggleCart}
              className={`relative p-3 rounded-xl transition-all duration-300 ${
                isScrolled
                  ? 'bg-sabrositas-primary hover:bg-sabrositas-accent text-white'
                  : 'bg-white/90 hover:bg-white text-sabrositas-primary'
              }`}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <ShoppingCart className="w-6 h-6" />
              {cartItemCount > 0 && (
                <motion.span
                  className="absolute -top-2 -right-2 bg-sabrositas-accent text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ duration: 0.2 }}
                >
                  {cartItemCount > 99 ? '99+' : cartItemCount}
                </motion.span>
              )}
            </motion.button>

            {/* Botón de menú móvil */}
            <motion.button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className={`lg:hidden p-3 rounded-xl transition-all duration-300 ${
                isScrolled
                  ? 'bg-sabrositas-primary hover:bg-sabrositas-accent text-white'
                  : 'bg-white/90 hover:bg-white text-sabrositas-primary'
              }`}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </motion.button>
          </div>
        </div>
      </div>

      {/* Menú móvil */}
      <AnimatePresence>
        {isMenuOpen && (
          <motion.div
            className="lg:hidden bg-white border-t border-gray-200"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            <div className="container-custom py-4">
              {/* Barra de búsqueda móvil */}
              <form onSubmit={handleSearch} className="mb-6">
                <div className="relative">
                  <input
                    type="text"
                    placeholder="Buscar arepas..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full px-4 py-3 pl-10 rounded-xl border border-gray-200 focus:border-sabrositas-primary focus:ring-2 focus:ring-sabrositas-primary/20"
                  />
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                </div>
              </form>

              {/* Navegación móvil */}
              <nav className="space-y-4">
                {navItems.map((item) => (
                  <motion.button
                    key={item.id}
                    onClick={() => handleNavigation(item.id)}
                    className="block w-full text-left py-3 px-4 text-sabrositas-neutral-dark hover:bg-sabrositas-neutral-light rounded-xl transition-colors duration-300"
                    whileHover={{ x: 5 }}
                  >
                    {item.label}
                  </motion.button>
                ))}
              </nav>

              {/* Información de contacto móvil */}
              <div className="mt-6 pt-6 border-t border-gray-200">
                <div className="flex items-center space-x-3 mb-3">
                  <Phone className="w-5 h-5 text-sabrositas-primary" />
                  <a 
                    href="tel:+573134531128" 
                    className="text-sabrositas-neutral-dark hover:text-sabrositas-primary transition-colors duration-300"
                  >
                    (313) 453-1128
                  </a>
                </div>
                <div className="flex items-center space-x-3">
                  <MapPin className="w-5 h-5 text-sabrositas-primary" />
                  <span className="text-sabrositas-neutral-dark text-sm">
                    Bogotá, Colombia
                  </span>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.header>
  );
};

export default Header;
