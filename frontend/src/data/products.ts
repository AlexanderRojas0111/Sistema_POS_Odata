export interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  category: 'Sencillas' | 'Clásicas' | 'Premium';
  ingredients: string[];
  image: string;
  popular?: boolean;
  new?: boolean;
  spicy?: boolean;
}

export const products: Product[] = [
  // Sencillas
  {
    id: 'la-facil',
    name: 'LA FÁCIL',
    description: 'La arepa más sencilla pero deliciosa, con mucho queso derretido.',
    price: 7000,
    category: 'Sencillas',
    ingredients: ['Queso'],
    image: '/images/la-facil.jpg',
    popular: true
  },
  {
    id: 'la-sencilla',
    name: 'LA SENCILLA',
    description: 'Jamón con queso, una combinación clásica que nunca falla.',
    price: 9000,
    category: 'Sencillas',
    ingredients: ['Jamón', 'Queso'],
    image: '/images/la-sencilla.jpg'
  },

  // Clásicas
  {
    id: 'la-compinche',
    name: 'LA COMPINCHE',
    description: 'Carne desmechada con maduro al horno y queso, una amiga fiel.',
    price: 12000,
    category: 'Clásicas',
    ingredients: ['Carne desmechada', 'Maduro al horno', 'Queso'],
    image: '/images/la-compinche.jpg',
    popular: true
  },
  {
    id: 'la-creida',
    name: 'LA CREÍDA',
    description: 'Pollo con salchicha y queso, sabe que es especial.',
    price: 13000,
    category: 'Clásicas',
    ingredients: ['Pollo', 'Salchicha', 'Queso'],
    image: '/images/la-creida.jpg'
  },
  {
    id: 'la-gomela',
    name: 'LA GOMELA',
    description: 'Carne con salchicha y queso, la más elegante del barrio.',
    price: 13500,
    category: 'Clásicas',
    ingredients: ['Carne', 'Salchicha', 'Queso'],
    image: '/images/la-gomela.jpg'
  },
  {
    id: 'la-infiel',
    name: 'LA INFIEL',
    description: 'Pollo con carne y queso, no puede decidirse por una sola proteína.',
    price: 13000,
    category: 'Clásicas',
    ingredients: ['Pollo', 'Carne', 'Queso'],
    image: '/images/la-infiel.jpg'
  },
  {
    id: 'la-sexy',
    name: 'LA SEXY',
    description: 'Pollo con champiñones y queso, irresistible y sofisticada.',
    price: 12000,
    category: 'Clásicas',
    ingredients: ['Pollo', 'Champiñones', 'Queso'],
    image: '/images/la-sexy.jpg'
  },
  {
    id: 'la-soltera',
    name: 'LA SOLTERA',
    description: 'Carne con maíz tierno y queso, independiente y deliciosa.',
    price: 12500,
    category: 'Clásicas',
    ingredients: ['Carne', 'Maíz tierno', 'Queso'],
    image: '/images/la-soltera.jpg'
  },
  {
    id: 'la-sumisa',
    name: 'LA SUMISA',
    description: 'Pollo con maíz tierno y queso, suave y complaciente.',
    price: 11500,
    category: 'Clásicas',
    ingredients: ['Pollo', 'Maíz tierno', 'Queso'],
    image: '/images/la-sumisa.jpg'
  },

  // Premium
  {
    id: 'la-patrona',
    name: 'LA PATRONA',
    description: 'Chicharrón, carne desmechada, maduro al horno y queso. La reina de las arepas.',
    price: 15000,
    category: 'Premium',
    ingredients: ['Chicharrón', 'Carne desmechada', 'Maduro al horno', 'Queso'],
    image: '/images/la-patrona.jpg',
    popular: true,
    new: true
  },
  {
    id: 'la-caprichosa',
    name: 'LA CAPRICHOSA',
    description: 'Carne desmechada, pollo, huevo y queso. Tiene todos los caprichos.',
    price: 14000,
    category: 'Premium',
    ingredients: ['Carne desmechada', 'Pollo', 'Huevo', 'Queso'],
    image: '/images/la-caprichosa.jpg',
    popular: true
  },
  {
    id: 'la-churra',
    name: 'LA CHURRA',
    description: 'Carne con chorizo santarrosano y queso, auténtica sabor colombiano.',
    price: 14500,
    category: 'Premium',
    ingredients: ['Carne', 'Chorizo santarrosano', 'Queso'],
    image: '/images/la-churra.jpg'
  },
  {
    id: 'la-diva',
    name: 'LA DIVA',
    description: 'Carne, pollo, champiñones, salchicha y queso. La más completa y exigente.',
    price: 16000,
    category: 'Premium',
    ingredients: ['Carne', 'Pollo', 'Champiñones', 'Salchicha', 'Queso'],
    image: '/images/la-diva.jpg',
    new: true
  },
  {
    id: 'la-toxica',
    name: 'LA TÓXICA',
    description: 'Costilla BBQ, carne, chorizo, maíz tierno y queso. Adictiva y peligrosa.',
    price: 18000,
    category: 'Premium',
    ingredients: ['Costilla BBQ', 'Carne', 'Chorizo', 'Maíz tierno', 'Queso'],
    image: '/images/la-toxica.jpg',
    popular: true
  },

];

export const categories = [
  { id: 'all', name: 'Todas', count: products.length },
  { id: 'Sencillas', name: 'Sencillas', count: products.filter(p => p.category === 'Sencillas').length },
  { id: 'Clásicas', name: 'Clásicas', count: products.filter(p => p.category === 'Clásicas').length },
  { id: 'Premium', name: 'Premium', count: products.filter(p => p.category === 'Premium').length },
  { id: 'Bebidas Frías', name: 'Bebidas Frías', count: products.filter(p => p.name.toLowerCase().includes('frío') || p.name.toLowerCase().includes('fría')).length },
  { id: 'Bebidas Calientes', name: 'Bebidas Calientes', count: products.filter(p => p.name.toLowerCase().includes('caliente') || p.name.toLowerCase().includes('café')).length },
];

export const getProductById = (id: string): Product | undefined => {
  return products.find(product => product.id === id);
};

export const getProductsByCategory = (category: string): Product[] => {
  if (category === 'all') return products;
  return products.filter(product => product.category === category);
};

export const getPopularProducts = (): Product[] => {
  return products.filter(product => product.popular);
};

export const getNewProducts = (): Product[] => {
  return products.filter(product => product.new);
};

export const getSpicyProducts = (): Product[] => {
  return products.filter(product => product.spicy);
};

export const searchProducts = (query: string): Product[] => {
  const lowercaseQuery = query.toLowerCase();
  return products.filter(product => 
    product.name.toLowerCase().includes(lowercaseQuery) ||
    product.description.toLowerCase().includes(lowercaseQuery) ||
    product.ingredients.some(ingredient => 
      ingredient.toLowerCase().includes(lowercaseQuery)
    )
  );
};
