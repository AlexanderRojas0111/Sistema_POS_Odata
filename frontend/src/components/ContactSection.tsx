import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Send, Phone, Mail, MapPin, MessageCircle, Clock, CheckCircle } from 'lucide-react';
import { useForm } from 'react-hook-form';

interface ContactFormData {
  name: string;
  email: string;
  phone: string;
  subject: string;
  message: string;
}

const ContactSection: React.FC = () => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset
  } = useForm<ContactFormData>();

  const onSubmit = async (data: ContactFormData) => {
    setIsSubmitting(true);
    
    // Simular envío del formulario
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    console.log('Formulario enviado:', data);
    setIsSubmitted(true);
    setIsSubmitting(false);
    
    // Resetear formulario después de 3 segundos
    setTimeout(() => {
      setIsSubmitted(false);
      reset();
    }, 3000);
  };

  const contactInfo = [
    {
      icon: <Phone className="w-6 h-6" />,
      title: 'Teléfono',
      content: '(+57) 313 453-1128',
      action: 'tel:+573134531128',
      color: 'text-green-600'
    },
    {
      icon: <MessageCircle className="w-6 h-6" />,
      title: 'WhatsApp',
      content: 'Chatea con nosotros',
      action: 'https://wa.me/573134531128',
      color: 'text-green-600'
    },
    {
      icon: <Mail className="w-6 h-6" />,
      title: 'Email',
      content: 'alexrojas8211@gmail.com',
      action: 'mailto:alexrojas8211@gmail.com',
      color: 'text-blue-600'
    },
    {
      icon: <MapPin className="w-6 h-6" />,
      title: 'Ubicación',
      content: 'Bogotá, Colombia',
      action: '#sucursales',
      color: 'text-red-600'
    }
  ];

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
    <section id="contacto" className="section-padding bg-white">
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
            Contáctanos
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            ¿Tienes alguna pregunta, sugerencia o quieres hacer un pedido especial? 
            Estamos aquí para ayudarte. ¡Contáctanos de la manera que prefieras!
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-12">
          {/* Información de contacto */}
          <motion.div
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            <motion.div variants={itemVariants} className="mb-8">
              <h3 className="text-2xl font-bold text-sabrositas-neutral-dark mb-6">
                Información de Contacto
              </h3>
              
              <div className="space-y-6">
                {contactInfo.map((info, index) => (
                  <motion.a
                    key={index}
                    href={info.action}
                    className="flex items-start space-x-4 p-4 bg-sabrositas-neutral-light rounded-xl hover:shadow-soft transition-all duration-300 group"
                    variants={itemVariants}
                    whileHover={{ scale: 1.02, x: 5 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <div className={`p-3 rounded-xl bg-white group-hover:scale-110 transition-transform duration-300 ${info.color}`}>
                      {info.icon}
                    </div>
                    <div>
                      <h4 className="font-semibold text-sabrositas-neutral-dark mb-1">
                        {info.title}
                      </h4>
                      <p className="text-gray-600">{info.content}</p>
                    </div>
                  </motion.a>
                ))}
              </div>
            </motion.div>

            {/* Horarios de atención */}
            <motion.div variants={itemVariants}>
              <div className="bg-gradient-to-r from-sabrositas-primary to-sabrositas-accent rounded-2xl p-6 text-white">
                <div className="flex items-center space-x-3 mb-4">
                  <Clock className="w-6 h-6" />
                  <h4 className="text-xl font-semibold">Horarios de Atención</h4>
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Lunes - Jueves</span>
                    <span className="font-semibold">6:00 AM - 10:00 PM</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Viernes</span>
                    <span className="font-semibold">6:00 AM - 11:00 PM</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Sábado</span>
                    <span className="font-semibold">7:00 AM - 11:00 PM</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Domingo</span>
                    <span className="font-semibold">7:00 AM - 9:00 PM</span>
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>

          {/* Formulario de contacto */}
          <motion.div
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            <motion.div variants={itemVariants}>
              <div className="card">
                <div className="p-8">
                  <h3 className="text-2xl font-bold text-sabrositas-neutral-dark mb-6">
                    Envíanos un Mensaje
                  </h3>

                  {isSubmitted ? (
                    <motion.div
                      className="text-center py-8"
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ duration: 0.5 }}
                    >
                      <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <CheckCircle className="w-8 h-8 text-green-600" />
                      </div>
                      <h4 className="text-xl font-semibold text-green-600 mb-2">
                        ¡Mensaje enviado!
                      </h4>
                      <p className="text-gray-600">
                        Gracias por contactarnos. Te responderemos pronto.
                      </p>
                    </motion.div>
                  ) : (
                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                      <div className="grid md:grid-cols-2 gap-6">
                        <div>
                          <label className="block text-sm font-semibold text-sabrositas-neutral-dark mb-2">
                            Nombre Completo *
                          </label>
                          <input
                            type="text"
                            {...register('name', { required: 'El nombre es requerido' })}
                            className={`input-field ${errors.name ? 'border-red-500' : ''}`}
                            placeholder="Tu nombre completo"
                          />
                          {errors.name && (
                            <p className="text-red-500 text-sm mt-1">{errors.name.message}</p>
                          )}
                        </div>

                        <div>
                          <label className="block text-sm font-semibold text-sabrositas-neutral-dark mb-2">
                            Email *
                          </label>
                          <input
                            type="email"
                            {...register('email', { 
                              required: 'El email es requerido',
                              pattern: {
                                value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                                message: 'Email inválido'
                              }
                            })}
                            className={`input-field ${errors.email ? 'border-red-500' : ''}`}
                            placeholder="tu@email.com"
                          />
                          {errors.email && (
                            <p className="text-red-500 text-sm mt-1">{errors.email.message}</p>
                          )}
                        </div>
                      </div>

                      <div className="grid md:grid-cols-2 gap-6">
                        <div>
                          <label className="block text-sm font-semibold text-sabrositas-neutral-dark mb-2">
                            Teléfono
                          </label>
                          <input
                            type="tel"
                            {...register('phone')}
                            className="input-field"
                            placeholder="(+57) 300 123-4567"
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-semibold text-sabrositas-neutral-dark mb-2">
                            Asunto *
                          </label>
                          <select
                            {...register('subject', { required: 'El asunto es requerido' })}
                            className={`input-field ${errors.subject ? 'border-red-500' : ''}`}
                          >
                            <option value="">Selecciona un asunto</option>
                            <option value="pedido">Hacer un pedido</option>
                            <option value="consulta">Consulta general</option>
                            <option value="sugerencia">Sugerencia</option>
                            <option value="reclamo">Reclamo</option>
                            <option value="trabajo">Oportunidades de trabajo</option>
                            <option value="otro">Otro</option>
                          </select>
                          {errors.subject && (
                            <p className="text-red-500 text-sm mt-1">{errors.subject.message}</p>
                          )}
                        </div>
                      </div>

                      <div>
                        <label className="block text-sm font-semibold text-sabrositas-neutral-dark mb-2">
                          Mensaje *
                        </label>
                        <textarea
                          {...register('message', { 
                            required: 'El mensaje es requerido',
                            minLength: {
                              value: 10,
                              message: 'El mensaje debe tener al menos 10 caracteres'
                            }
                          })}
                          rows={5}
                          className={`input-field resize-none ${errors.message ? 'border-red-500' : ''}`}
                          placeholder="Cuéntanos en qué podemos ayudarte..."
                        />
                        {errors.message && (
                          <p className="text-red-500 text-sm mt-1">{errors.message.message}</p>
                        )}
                      </div>

                      <motion.button
                        type="submit"
                        disabled={isSubmitting}
                        className="w-full btn-primary flex items-center justify-center space-x-2 py-4 text-lg disabled:opacity-50 disabled:cursor-not-allowed"
                        whileHover={{ scale: isSubmitting ? 1 : 1.02 }}
                        whileTap={{ scale: isSubmitting ? 1 : 0.98 }}
                      >
                        {isSubmitting ? (
                          <>
                            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                            <span>Enviando...</span>
                          </>
                        ) : (
                          <>
                            <Send className="w-5 h-5" />
                            <span>Enviar Mensaje</span>
                          </>
                        )}
                      </motion.button>

                      <p className="text-sm text-gray-500 text-center">
                        * Campos obligatorios. Te responderemos en menos de 24 horas.
                      </p>
                    </form>
                  )}
                </div>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default ContactSection;
