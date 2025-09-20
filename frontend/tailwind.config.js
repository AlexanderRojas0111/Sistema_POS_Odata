/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Paleta de colores institucionales Sabrositas
        sabrositas: {
          primary: '#f59e0b',    // Ámbar principal (Amber 600)
          secondary: '#ea580c',  // Naranja secundario (Orange 500)
          accent: '#d97706',     // Ámbar más oscuro para hover
          neutral: {
            light: '#F5F5F5',    // Fondo claro
            dark: '#333333'      // Texto principal
          },
          success: '#28A745',    // Verde para confirmaciones
        },
        // Colores de categorías de productos
      category: {
        sencilla: '#10b981',   // Verde para sencillas
        clasica: '#f59e0b',    // Ámbar para clásicas
        premium: '#ea580c',    // Naranja para premium
        'bebida-fria': '#3b82f6',    // Azul para bebidas frías
        'bebida-caliente': '#ef4444' // Rojo para bebidas calientes
      }
      },
      fontFamily: {
        'poppins': ['Poppins', 'sans-serif'],
        'inter': ['Inter', 'sans-serif'],
        'dancing': ['Dancing Script', 'cursive'],
      },
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
        '5xl': ['3rem', { lineHeight: '1' }],
        '6xl': ['3.75rem', { lineHeight: '1' }],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      borderRadius: {
        'xl': '0.75rem',
        '2xl': '1rem',
        '3xl': '1.5rem',
      },
      boxShadow: {
        'soft': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'medium': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        'large': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
        'amber': '0 4px 14px 0 rgba(245, 158, 11, 0.25)',
        'amber-lg': '0 10px 25px 0 rgba(245, 158, 11, 0.3)',
      },
      backgroundImage: {
        'gradient-amber': 'linear-gradient(135deg, #f59e0b 0%, #ea580c 100%)',
        'gradient-amber-text': 'linear-gradient(135deg, #f59e0b 0%, #ea580c 100%)',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'bounce-gentle': 'bounceGentle 2s infinite',
        'pulse-soft': 'pulseSoft 2s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        bounceGentle: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-5px)' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.8' },
        },
      },
      screens: {
        'xs': '320px',
        'sm': '640px',
        'md': '768px',
        'lg': '1024px',
        'xl': '1280px',
        '2xl': '1536px',
      },
    },
  },
  plugins: [],
}
