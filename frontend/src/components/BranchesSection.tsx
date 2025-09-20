import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { MapPin, Phone, Car, Wifi, Users, Star, Navigation, MessageCircle } from 'lucide-react';
import { branches, getWhatsAppLink, getGoogleMapsLink } from '../data/branches';

const BranchesSection: React.FC = () => {
  const [selectedBranch, setSelectedBranch] = useState(branches[0]);

  const getServiceIcon = (service: string) => {
    const icons: { [key: string]: React.ReactNode } = {
      'Domicilios': <Car className="w-4 h-4" />,
      'Para llevar': <Car className="w-4 h-4" />,
      'Mesa': <Users className="w-4 h-4" />,
      'Estacionamiento': <Car className="w-4 h-4" />,
      'Delivery express': <Car className="w-4 h-4" />,
      'Eventos': <Star className="w-4 h-4" />
    };
    return icons[service] || <Star className="w-4 h-4" />;
  };

  const getFeatureIcon = (feature: string) => {
    const icons: { [key: string]: React.ReactNode } = {
      'Wifi gratuito': <Wifi className="w-4 h-4" />,
      'Aire acondicionado': <Car className="w-4 h-4" />,
      'Terraza': <Star className="w-4 h-4" />,
      'Acceso para discapacitados': <Users className="w-4 h-4" />,
      'Zona de juegos': <Users className="w-4 h-4" />,
      'Parking valet': <Car className="w-4 h-4" />,
      'Espacio para niños': <Users className="w-4 h-4" />,
      'Estacionamiento amplio': <Car className="w-4 h-4" />
    };
    return icons[feature] || <Star className="w-4 h-4" />;
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <section id="sucursales" className="section-padding bg-sabrositas-neutral-light">
      <div className="container-custom">
        {/* Header de la sección */}
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="text-4xl md:text-5xl font-bold gradient-text mb-4">
            Nuestras Sucursales
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Encuentra la sucursal más cercana a ti. Cada una tiene su personalidad única 
            pero todas comparten el mismo amor por las arepas cuadradas.
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Lista de sucursales */}
          <motion.div
            className="lg:col-span-1"
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            <div className="space-y-4">
              {branches.map((branch, _index) => (
                <motion.div
                  key={branch.id}
                  className={`card cursor-pointer transition-all duration-300 ${
                    selectedBranch.id === branch.id
                      ? 'ring-2 ring-sabrositas-primary shadow-medium'
                      : 'hover:shadow-medium'
                  }`}
                  variants={itemVariants}
                  onClick={() => setSelectedBranch(branch)}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <div className="p-6">
                    <div className="flex items-start space-x-4">
                      <div className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 ${
                        selectedBranch.id === branch.id
                          ? 'bg-gradient-to-r from-sabrositas-primary to-sabrositas-accent'
                          : 'bg-sabrositas-neutral-light'
                      }`}>
                        <MapPin className={`w-6 h-6 ${
                          selectedBranch.id === branch.id ? 'text-white' : 'text-sabrositas-primary'
                        }`} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className={`text-lg font-semibold mb-1 ${
                          selectedBranch.id === branch.id
                            ? 'text-sabrositas-primary'
                            : 'text-sabrositas-neutral-dark'
                        }`}>
                          {branch.name}
                        </h3>
                        <p className="text-sm text-gray-600 mb-2 line-clamp-2">
                          {branch.address}
                        </p>
                        <div className="flex items-center space-x-2 text-sm text-gray-500">
                          <Phone className="w-4 h-4" />
                          <span>{branch.phone}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Detalles de la sucursal seleccionada */}
          <motion.div
            className="lg:col-span-2"
            key={selectedBranch.id}
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="card">
              <div className="p-8">
                {/* Header de la sucursal */}
                <div className="flex items-start justify-between mb-6">
                  <div>
                    <h3 className="text-2xl font-bold text-sabrositas-neutral-dark mb-2">
                      {selectedBranch.name}
                    </h3>
                    <div className="flex items-center space-x-2 text-gray-600">
                      <MapPin className="w-5 h-5" />
                      <span>{selectedBranch.address}</span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2 text-yellow-500">
                    <Star className="w-5 h-5 fill-current" />
                    <span className="font-semibold">4.8</span>
                  </div>
                </div>

                {/* Mapa placeholder */}
                <div className="h-64 bg-gradient-to-br from-sabrositas-primary/20 to-sabrositas-accent/20 rounded-2xl mb-6 flex items-center justify-center relative overflow-hidden">
                  <div className="text-center">
                    <div className="text-6xl mb-4">🗺️</div>
                    <p className="text-sabrositas-neutral-dark font-semibold mb-2">
                      Ubicación en el mapa
                    </p>
                    <p className="text-sm text-gray-600">
                      {selectedBranch.address}
                    </p>
                  </div>
                  
                  {/* Botón de Google Maps */}
                  <motion.a
                    href={getGoogleMapsLink(selectedBranch.address)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="absolute bottom-4 right-4 btn-accent flex items-center space-x-2"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <Navigation className="w-4 h-4" />
                    <span>Abrir en Maps</span>
                  </motion.a>
                </div>

                {/* Información de contacto */}
                <div className="grid md:grid-cols-2 gap-6 mb-6">
                  <div className="space-y-4">
                    <h4 className="text-lg font-semibold text-sabrositas-neutral-dark">
                      Información de Contacto
                    </h4>
                    
                    <div className="space-y-3">
                      <motion.a
                        href={`tel:${selectedBranch.phone}`}
                        className="flex items-center space-x-3 p-3 bg-sabrositas-neutral-light rounded-xl hover:bg-gray-200 transition-colors duration-300"
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        <Phone className="w-5 h-5 text-sabrositas-primary" />
                        <span className="font-medium">{selectedBranch.phone}</span>
                      </motion.a>

                      <motion.a
                        href={getWhatsAppLink(selectedBranch.whatsapp, 'Hola! Me gustaría hacer un pedido')}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center space-x-3 p-3 bg-green-50 hover:bg-green-100 rounded-xl transition-colors duration-300"
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        <MessageCircle className="w-5 h-5 text-green-600" />
                        <span className="font-medium">WhatsApp</span>
                      </motion.a>

                      <div className="flex items-center space-x-3 p-3 bg-sabrositas-neutral-light rounded-xl">
                        <span className="w-5 h-5 text-sabrositas-primary">📧</span>
                        <span className="font-medium">{selectedBranch.email}</span>
                      </div>
                    </div>
                  </div>

                  {/* Horarios */}
                  <div className="space-y-4">
                    <h4 className="text-lg font-semibold text-sabrositas-neutral-dark">
                      Horarios de Atención
                    </h4>
                    
                    <div className="space-y-2">
                      {Object.entries(selectedBranch.hours).map(([day, hours]) => (
                        <div key={day} className="flex justify-between items-center py-2 border-b border-gray-100 last:border-b-0">
                          <span className="font-medium text-gray-600 capitalize">
                            {day === 'monday' ? 'Lunes' :
                             day === 'tuesday' ? 'Martes' :
                             day === 'wednesday' ? 'Miércoles' :
                             day === 'thursday' ? 'Jueves' :
                             day === 'friday' ? 'Viernes' :
                             day === 'saturday' ? 'Sábado' : 'Domingo'}
                          </span>
                          <span className="text-sabrositas-neutral-dark">{hours}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Servicios y características */}
                <div className="grid md:grid-cols-2 gap-6">
                  {/* Servicios */}
                  <div>
                    <h4 className="text-lg font-semibold text-sabrositas-neutral-dark mb-4">
                      Servicios Disponibles
                    </h4>
                    <div className="space-y-2">
                      {selectedBranch.services.map((service, index) => (
                        <div key={index} className="flex items-center space-x-3">
                          <div className="w-8 h-8 bg-sabrositas-primary/10 rounded-lg flex items-center justify-center">
                            {getServiceIcon(service)}
                          </div>
                          <span className="text-gray-700">{service}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Características */}
                  <div>
                    <h4 className="text-lg font-semibold text-sabrositas-neutral-dark mb-4">
                      Características
                    </h4>
                    <div className="space-y-2">
                      {selectedBranch.features.map((feature, index) => (
                        <div key={index} className="flex items-center space-x-3">
                          <div className="w-8 h-8 bg-sabrositas-accent/10 rounded-lg flex items-center justify-center">
                            {getFeatureIcon(feature)}
                          </div>
                          <span className="text-gray-700">{feature}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Botones de acción */}
                <div className="flex flex-col sm:flex-row gap-4 mt-8">
                  <motion.a
                    href={`tel:${selectedBranch.phone}`}
                    className="btn-primary flex items-center justify-center space-x-2 flex-1"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Phone className="w-5 h-5" />
                    <span>Llamar Ahora</span>
                  </motion.a>

                  <motion.a
                    href={getWhatsAppLink(selectedBranch.whatsapp, 'Hola! Me gustaría hacer un pedido')}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-secondary flex items-center justify-center space-x-2 flex-1"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <MessageCircle className="w-5 h-5" />
                    <span>WhatsApp</span>
                  </motion.a>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default BranchesSection;
