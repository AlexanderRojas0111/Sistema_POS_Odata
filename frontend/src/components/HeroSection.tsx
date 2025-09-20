import React from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, Star, Users, Clock } from 'lucide-react';

const HeroSection: React.FC = () => {
  const scrollToMenu = () => {
    const menuSection = document.getElementById('menu');
    if (menuSection) {
      menuSection.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const stats = [
    {
      icon: <Users className="w-6 h-6" />,
      value: '10K+',
      label: 'Clientes felices'
    },
    {
      icon: <Star className="w-6 h-6" />,
      value: '4.9',
      label: 'Calificación'
    },
    {
      icon: <Clock className="w-6 h-6" />,
      value: '15min',
      label: 'Tiempo promedio'
    }
  ];

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-sabrositas-primary via-sabrositas-accent to-sabrositas-secondary">
      {/* Fondo con patrón */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0 pattern-dots"></div>
      </div>

      <div className="container-custom relative z-10">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Contenido izquierdo */}
          <motion.div
            className="text-center lg:text-left"
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
          >
            <motion.div
              className="inline-flex items-center space-x-2 bg-white/20 backdrop-blur-sm rounded-full px-4 py-2 mb-6"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.6 }}
            >
              <span className="text-white text-sm font-medium">🍽️ Las mejores arepas cuadradas</span>
            </motion.div>

            <motion.h1
              className="text-5xl md:text-6xl lg:text-7xl font-bold text-white mb-6 leading-tight"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.8 }}
            >
              <span className="block">Sabrositas</span>
              <span className="block font-dancing text-sabrositas-secondary text-4xl md:text-5xl lg:text-6xl mt-2">
                Las arepas cuadradas
              </span>
            </motion.h1>

            <motion.p
              className="text-xl text-white/90 mb-8 max-w-2xl leading-relaxed"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4, duration: 0.8 }}
            >
              Descubre 18 sabores únicos de arepas cuadradas, cada una con su personalidad especial. 
              Desde las más sencillas hasta las más premium, todas preparadas con amor y los mejores ingredientes.
            </motion.p>

            <motion.div
              className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5, duration: 0.8 }}
            >
              <motion.button
                onClick={scrollToMenu}
                className="btn-primary text-lg px-8 py-4 flex items-center justify-center space-x-2"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <span>Ver Menú</span>
                <ArrowRight className="w-5 h-5" />
              </motion.button>

              <motion.a
                href="tel:+573134531128"
                className="btn-secondary text-lg px-8 py-4 flex items-center justify-center space-x-2"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <span>Llamar Ahora</span>
                <span className="text-xl">📞</span>
              </motion.a>
            </motion.div>

            {/* Estadísticas */}
            <motion.div
              className="grid grid-cols-3 gap-6 mt-12 max-w-md mx-auto lg:mx-0"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6, duration: 0.8 }}
            >
              {stats.map((stat, index) => (
                <motion.div
                  key={index}
                  className="text-center"
                  whileHover={{ scale: 1.05 }}
                  transition={{ duration: 0.2 }}
                >
                  <div className="flex justify-center text-sabrositas-secondary mb-2">
                    {stat.icon}
                  </div>
                  <div className="text-2xl font-bold text-white">{stat.value}</div>
                  <div className="text-sm text-white/80">{stat.label}</div>
                </motion.div>
              ))}
            </motion.div>
          </motion.div>

          {/* Contenido derecho - Imagen/Ilustración */}
          <motion.div
            className="relative"
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, ease: 'easeOut', delay: 0.3 }}
          >
            {/* Placeholder para imagen de arepas */}
            <div className="relative w-full h-96 lg:h-[500px] bg-gradient-to-br from-white/20 to-white/10 rounded-3xl backdrop-blur-sm border border-white/20 overflow-hidden">
              <div className="absolute inset-0 flex items-center justify-center">
                <motion.div
                  className="text-center"
                  animate={{ 
                    rotate: [0, 5, -5, 0],
                    scale: [1, 1.05, 1]
                  }}
                  transition={{ 
                    duration: 6,
                    repeat: Infinity,
                    ease: 'easeInOut'
                  }}
                >
                  <div className="text-8xl mb-4">🥞</div>
                  <div className="text-white text-xl font-semibold">
                    Arepas Cuadradas
                  </div>
                  <div className="text-white/80 text-sm">
                    Hechas con amor
                  </div>
                </motion.div>
              </div>

              {/* Elementos decorativos flotantes */}
              <motion.div
                className="absolute top-10 left-10 text-4xl"
                animate={{ 
                  y: [0, -20, 0],
                  rotate: [0, 10, 0]
                }}
                transition={{ 
                  duration: 4,
                  repeat: Infinity,
                  ease: 'easeInOut'
                }}
              >
                🌽
              </motion.div>
              
              <motion.div
                className="absolute bottom-10 right-10 text-4xl"
                animate={{ 
                  y: [0, 20, 0],
                  rotate: [0, -10, 0]
                }}
                transition={{ 
                  duration: 5,
                  repeat: Infinity,
                  ease: 'easeInOut'
                }}
              >
                🧀
              </motion.div>

              <motion.div
                className="absolute top-1/2 right-5 text-3xl"
                animate={{ 
                  x: [0, 15, 0],
                  rotate: [0, 15, 0]
                }}
                transition={{ 
                  duration: 6,
                  repeat: Infinity,
                  ease: 'easeInOut'
                }}
              >
                🥓
              </motion.div>
            </div>

            {/* Badge de calidad */}
            <motion.div
              className="absolute -bottom-6 -left-6 bg-white rounded-2xl p-4 shadow-large"
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.8, duration: 0.6 }}
              whileHover={{ scale: 1.05 }}
            >
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-gradient-to-r from-sabrositas-primary to-sabrositas-accent rounded-xl flex items-center justify-center">
                  <Star className="w-6 h-6 text-white" />
                </div>
                <div>
                  <div className="font-bold text-sabrositas-neutral-dark">Calidad Premium</div>
                  <div className="text-sm text-gray-600">Ingredientes frescos</div>
                </div>
              </div>
            </motion.div>

            {/* Badge de tiempo */}
            <motion.div
              className="absolute -top-6 -right-6 bg-white rounded-2xl p-4 shadow-large"
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 1, duration: 0.6 }}
              whileHover={{ scale: 1.05 }}
            >
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-gradient-to-r from-sabrositas-accent to-sabrositas-secondary rounded-xl flex items-center justify-center">
                  <Clock className="w-6 h-6 text-white" />
                </div>
                <div>
                  <div className="font-bold text-sabrositas-neutral-dark">Rápido</div>
                  <div className="text-sm text-gray-600">15 min promedio</div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </div>

      {/* Indicador de scroll */}
      <motion.div
        className="absolute bottom-8 left-1/2 transform -translate-x-1/2"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.2, duration: 0.6 }}
      >
        <motion.div
          className="w-6 h-10 border-2 border-white/50 rounded-full flex justify-center"
          animate={{ 
            borderColor: ['rgba(255,255,255,0.5)', 'rgba(255,255,255,1)', 'rgba(255,255,255,0.5)']
          }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <motion.div
            className="w-1 h-3 bg-white rounded-full mt-2"
            animate={{ y: [0, 12, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
          />
        </motion.div>
      </motion.div>
    </section>
  );
};

export default HeroSection;
