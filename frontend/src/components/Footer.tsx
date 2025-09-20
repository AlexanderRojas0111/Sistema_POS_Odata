import React from 'react';
import { motion } from 'framer-motion';
import { Heart, ArrowUp, Phone, Mail, MapPin, Instagram, Facebook, Twitter } from 'lucide-react';

const Footer: React.FC = () => {
  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const currentYear = new Date().getFullYear();

  const footerLinks = {
    menu: [
      { name: 'Nuestro Menú', href: '#menu' },
      { name: 'Sucursales', href: '#sucursales' },
      { name: 'Contacto', href: '#contacto' }
    ],
      categories: [
        { name: 'Arepas Sencillas', href: '#menu' },
        { name: 'Arepas Clásicas', href: '#menu' },
        { name: 'Arepas Premium', href: '#menu' },
        { name: 'Bebidas Frías', href: '#menu' },
        { name: 'Bebidas Calientes', href: '#menu' }
      ],
    info: [
      { name: 'Sobre Nosotros', href: '#about' },
      { name: 'Política de Privacidad', href: '#privacy' },
      { name: 'Términos y Condiciones', href: '#terms' },
      { name: 'Trabaja con Nosotros', href: '#careers' }
    ]
  };

  const socialLinks = [
    { name: 'Instagram', icon: <Instagram className="w-5 h-5" />, href: 'https://instagram.com/sabrositas', color: 'hover:text-pink-500' },
    { name: 'Facebook', icon: <Facebook className="w-5 h-5" />, href: 'https://facebook.com/sabrositas', color: 'hover:text-blue-600' },
    { name: 'Twitter', icon: <Twitter className="w-5 h-5" />, href: 'https://twitter.com/sabrositas', color: 'hover:text-blue-400' }
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <footer className="bg-sabrositas-neutral-dark text-white relative overflow-hidden">
      {/* Patrón de fondo */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute inset-0 pattern-dots"></div>
      </div>

      <div className="container-custom relative z-10">
        {/* Contenido principal del footer */}
        <motion.div
          className="py-16"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
        >
          <div className="grid lg:grid-cols-4 md:grid-cols-2 gap-8">
            {/* Logo y descripción */}
            <motion.div className="lg:col-span-1" variants={itemVariants}>
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-12 h-12 bg-gradient-to-r from-sabrositas-primary to-sabrositas-accent rounded-xl flex items-center justify-center">
                  <span className="text-white font-bold text-xl font-dancing">S</span>
                </div>
                <div>
                  <h3 className="text-2xl font-bold">Sabrositas</h3>
                  <p className="text-sm text-gray-300 font-dancing">
                    Las arepas cuadradas
                  </p>
                </div>
              </div>
              
              <p className="text-gray-300 mb-6 leading-relaxed">
                Especialistas en arepas cuadradas desde 2020. Cada arepa tiene su personalidad única, 
                preparada con ingredientes frescos y mucho amor.
              </p>

              {/* Información de contacto */}
              <div className="space-y-3">
                <div className="flex items-center space-x-3 text-gray-300">
                  <Phone className="w-5 h-5 text-sabrositas-secondary" />
                  <a href="tel:+573134531128" className="hover:text-white transition-colors duration-300">
                    (+57) 313 453-1128
                  </a>
                </div>
                <div className="flex items-center space-x-3 text-gray-300">
                  <Mail className="w-5 h-5 text-sabrositas-secondary" />
                  <a href="mailto:alexrojas8211@gmail.com" className="hover:text-white transition-colors duration-300">
                    alexrojas8211@gmail.com
                  </a>
                </div>
                <div className="flex items-center space-x-3 text-gray-300">
                  <MapPin className="w-5 h-5 text-sabrositas-secondary" />
                  <span>Bogotá, Colombia</span>
                </div>
              </div>
            </motion.div>

            {/* Enlaces del menú */}
            <motion.div variants={itemVariants}>
              <h4 className="text-lg font-semibold mb-6">Menú</h4>
              <ul className="space-y-3">
                {footerLinks.menu.map((link, index) => (
                  <li key={index}>
                    <a
                      href={link.href}
                      className="text-gray-300 hover:text-sabrositas-secondary transition-colors duration-300"
                    >
                      {link.name}
                    </a>
                  </li>
                ))}
              </ul>
            </motion.div>

            {/* Categorías */}
            <motion.div variants={itemVariants}>
              <h4 className="text-lg font-semibold mb-6">Categorías</h4>
              <ul className="space-y-3">
                {footerLinks.categories.map((link, index) => (
                  <li key={index}>
                    <a
                      href={link.href}
                      className="text-gray-300 hover:text-sabrositas-secondary transition-colors duration-300"
                    >
                      {link.name}
                    </a>
                  </li>
                ))}
              </ul>
            </motion.div>

            {/* Información y redes sociales */}
            <motion.div variants={itemVariants}>
              <h4 className="text-lg font-semibold mb-6">Información</h4>
              <ul className="space-y-3 mb-6">
                {footerLinks.info.map((link, index) => (
                  <li key={index}>
                    <a
                      href={link.href}
                      className="text-gray-300 hover:text-sabrositas-secondary transition-colors duration-300"
                    >
                      {link.name}
                    </a>
                  </li>
                ))}
              </ul>

              {/* Redes sociales */}
              <div>
                <h5 className="text-sm font-semibold mb-4 text-gray-300">Síguenos</h5>
                <div className="flex space-x-4">
                  {socialLinks.map((social, index) => (
                    <motion.a
                      key={index}
                      href={social.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className={`text-gray-300 ${social.color} transition-colors duration-300`}
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                    >
                      {social.icon}
                    </motion.a>
                  ))}
                </div>
              </div>
            </motion.div>
          </div>
        </motion.div>

        {/* Línea divisoria */}
        <div className="border-t border-gray-700 py-8">
          <div className="flex flex-col md:flex-row items-center justify-between space-y-4 md:space-y-0">
            {/* Copyright */}
            <motion.div
              className="flex items-center space-x-2 text-gray-300"
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <span>© {currentYear} Sabrositas. Hecho con</span>
              <Heart className="w-4 h-4 text-red-500 fill-current" />
              <span>en Colombia</span>
            </motion.div>

            {/* Botón de scroll to top */}
            <motion.button
              onClick={scrollToTop}
              className="flex items-center space-x-2 bg-sabrositas-primary hover:bg-sabrositas-accent text-white px-4 py-2 rounded-xl transition-colors duration-300"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <ArrowUp className="w-4 h-4" />
              <span>Volver arriba</span>
            </motion.button>
          </div>
        </div>
      </div>

      {/* Elemento decorativo */}
      <div className="absolute bottom-0 left-0 w-full h-1 bg-gradient-to-r from-sabrositas-primary via-sabrositas-accent to-sabrositas-secondary"></div>
    </footer>
  );
};

export default Footer;
