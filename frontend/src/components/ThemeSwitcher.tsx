/**
 * Theme Switcher - Sistema POS Sabrositas
 * Componente para cambiar entre modos de tema
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sun, Moon, Monitor, ChevronDown } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

const ThemeSwitcher: React.FC = () => {
  const { theme, actualTheme, setTheme } = useTheme();
  const [isOpen, setIsOpen] = useState(false);

  const themes = [
    {
      id: 'light' as const,
      name: 'Claro',
      icon: Sun,
      description: 'Tema claro'
    },
    {
      id: 'dark' as const,
      name: 'Oscuro',
      icon: Moon,
      description: 'Tema oscuro'
    },
    {
      id: 'system' as const,
      name: 'Sistema',
      icon: Monitor,
      description: 'Seguir sistema'
    }
  ];

  const currentTheme = themes.find(t => t.id === theme) || themes[0];
  const CurrentIcon = currentTheme.icon;

  return (
    <div className="relative">
      {/* Botón principal */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`
          flex items-center space-x-2 px-3 py-2 rounded-lg transition-all duration-200
          ${actualTheme === 'dark' 
            ? 'bg-gray-800 hover:bg-gray-700 text-gray-200' 
            : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
          }
          ${isOpen ? 'ring-2 ring-amber-500 ring-opacity-50' : ''}
        `}
        aria-label="Cambiar tema"
      >
        <CurrentIcon className="h-4 w-4" />
        <span className="text-sm font-medium hidden sm:block">
          {currentTheme.name}
        </span>
        <ChevronDown className={`h-3 w-3 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Dropdown */}
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Overlay para cerrar */}
            <div
              className="fixed inset-0 z-10"
              onClick={() => setIsOpen(false)}
            />

            {/* Menu */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: -10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: -10 }}
              transition={{ duration: 0.1 }}
              className={`
                absolute top-full mt-2 right-0 w-48 py-2 rounded-lg shadow-lg border z-20
                ${actualTheme === 'dark'
                  ? 'bg-gray-800 border-gray-700'
                  : 'bg-white border-gray-200'
                }
              `}
            >
              {themes.map((themeOption) => {
                const Icon = themeOption.icon;
                const isSelected = theme === themeOption.id;
                
                return (
                  <button
                    key={themeOption.id}
                    onClick={() => {
                      setTheme(themeOption.id);
                      setIsOpen(false);
                    }}
                    className={`
                      w-full flex items-center space-x-3 px-4 py-2 text-sm transition-colors
                      ${actualTheme === 'dark'
                        ? 'hover:bg-gray-700 text-gray-200'
                        : 'hover:bg-gray-50 text-gray-700'
                      }
                      ${isSelected 
                        ? actualTheme === 'dark'
                          ? 'bg-gray-700 text-amber-400'
                          : 'bg-amber-50 text-amber-600'
                        : ''
                      }
                    `}
                  >
                    <Icon className={`h-4 w-4 ${isSelected ? 'text-amber-500' : ''}`} />
                    <div className="flex-1 text-left">
                      <div className={`font-medium ${isSelected ? 'text-amber-600 dark:text-amber-400' : ''}`}>
                        {themeOption.name}
                      </div>
                      <div className={`text-xs opacity-70 ${isSelected ? 'text-amber-600 dark:text-amber-400' : ''}`}>
                        {themeOption.description}
                      </div>
                    </div>
                    {isSelected && (
                      <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        className="w-2 h-2 bg-amber-500 rounded-full"
                      />
                    )}
                  </button>
                );
              })}
              
              {/* Información adicional */}
              <div className={`
                mt-2 pt-2 px-4 border-t text-xs opacity-70
                ${actualTheme === 'dark' ? 'border-gray-700' : 'border-gray-200'}
              `}>
                Tema actual: <span className="font-medium capitalize">{actualTheme}</span>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ThemeSwitcher;
