export interface Branch {
  id: string;
  name: string;
  address: string;
  phone: string;
  whatsapp: string;
  email: string;
  hours: {
    monday: string;
    tuesday: string;
    wednesday: string;
    thursday: string;
    friday: string;
    saturday: string;
    sunday: string;
  };
  coordinates: {
    lat: number;
    lng: number;
  };
  services: string[];
  features: string[];
}

export const branches: Branch[] = [
  {
    id: 'centro',
    name: 'Sucursal Centro',
    address: 'Carrera 15 #25-30, Centro, Bogotá',
    phone: '(+57) 1 234-5678',
    whatsapp: '3134531128',
    email: 'centro@sabrositas.com',
    hours: {
      monday: '6:00 AM - 10:00 PM',
      tuesday: '6:00 AM - 10:00 PM',
      wednesday: '6:00 AM - 10:00 PM',
      thursday: '6:00 AM - 10:00 PM',
      friday: '6:00 AM - 11:00 PM',
      saturday: '7:00 AM - 11:00 PM',
      sunday: '7:00 AM - 9:00 PM'
    },
    coordinates: {
      lat: 4.6097100,
      lng: -74.0817500
    },
    services: ['Domicilios', 'Para llevar', 'Mesa', 'Estacionamiento'],
    features: ['Wifi gratuito', 'Aire acondicionado', 'Terraza', 'Acceso para discapacitados']
  },
  {
    id: 'norte',
    name: 'Sucursal Norte',
    address: 'Calle 85 #12-45, Zona Rosa, Bogotá',
    phone: '(+57) 1 345-6789',
    whatsapp: '3134531128',
    email: 'norte@sabrositas.com',
    hours: {
      monday: '6:30 AM - 10:30 PM',
      tuesday: '6:30 AM - 10:30 PM',
      wednesday: '6:30 AM - 10:30 PM',
      thursday: '6:30 AM - 10:30 PM',
      friday: '6:30 AM - 11:30 PM',
      saturday: '8:00 AM - 11:30 PM',
      sunday: '8:00 AM - 10:00 PM'
    },
    coordinates: {
      lat: 4.6711100,
      lng: -74.0522200
    },
    services: ['Domicilios', 'Para llevar', 'Mesa', 'Delivery express'],
    features: ['Wifi gratuito', 'Aire acondicionado', 'Zona de juegos', 'Parking valet']
  },
  {
    id: 'sur',
    name: 'Sucursal Sur',
    address: 'Avenida 68 #38-25, Kennedy, Bogotá',
    phone: '(+57) 1 456-7890',
    whatsapp: '3134531128',
    email: 'sur@sabrositas.com',
    hours: {
      monday: '6:00 AM - 9:30 PM',
      tuesday: '6:00 AM - 9:30 PM',
      wednesday: '6:00 AM - 9:30 PM',
      thursday: '6:00 AM - 9:30 PM',
      friday: '6:00 AM - 10:30 PM',
      saturday: '7:00 AM - 10:30 PM',
      sunday: '7:00 AM - 9:00 PM'
    },
    coordinates: {
      lat: 4.6097100,
      lng: -74.1500000
    },
    services: ['Domicilios', 'Para llevar', 'Mesa', 'Eventos'],
    features: ['Wifi gratuito', 'Aire acondicionado', 'Espacio para niños', 'Estacionamiento amplio']
  }
];

export const getBranchById = (id: string): Branch | undefined => {
  return branches.find(branch => branch.id === id);
};

export const getAllBranches = (): Branch[] => {
  return branches;
};

export const getBranchServices = (): string[] => {
  const allServices = branches.flatMap(branch => branch.services);
  return [...new Set(allServices)];
};

export const getBranchFeatures = (): string[] => {
  const allFeatures = branches.flatMap(branch => branch.features);
  return [...new Set(allFeatures)];
};

export const formatPhoneNumber = (phone: string): string => {
  return phone.replace(/[^\d]/g, '');
};

export const getWhatsAppLink = (phone: string, message?: string): string => {
  const cleanPhone = formatPhoneNumber(phone);
  const encodedMessage = message ? encodeURIComponent(message) : '';
  return `https://wa.me/${cleanPhone}${encodedMessage ? `?text=${encodedMessage}` : ''}`;
};

export const getGoogleMapsLink = (address: string): string => {
  const encodedAddress = encodeURIComponent(address);
  return `https://www.google.com/maps/search/?api=1&query=${encodedAddress}`;
};
