/**
 * Tabla de Productos Moderna - Sistema POS Sabrositas
 * Tabla optimizada para mostrar productos con mejor presentación
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Package, Edit, Trash2, Eye, DollarSign, TrendingUp } from 'lucide-react';
import ModernTable from './ModernTable';

interface Product {
  id: number;
  name: string;
  sku: string;
  category: string;
  price: number;
  stock: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  description?: string;
  image_url?: string;
}

interface ProductsTableProps {
  products: Product[];
  onEdit?: (product: Product) => void;
  onDelete?: (product: Product) => void;
  onView?: (product: Product) => void;
  loading?: boolean;
  title?: string;
  subtitle?: string;
}

export const ProductsTable: React.FC<ProductsTableProps> = ({
  products,
  onEdit,
  onDelete,
  onView,
  loading = false,
  title = "Productos",
  subtitle = "Gestión de productos del inventario"
}) => {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0
    }).format(value);
  };

  const getStockStatus = (stock: number) => {
    if (stock === 0) {
      return (
        <span className="px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
          Sin Stock
        </span>
      );
    } else if (stock < 10) {
      return (
        <span className="px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
          Bajo Stock
        </span>
      );
    } else {
      return (
        <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
          En Stock
        </span>
      );
    }
  };

  const getStatusBadge = (isActive: boolean) => {
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
        isActive 
          ? 'bg-green-100 text-green-800' 
          : 'bg-gray-100 text-gray-800'
      }`}>
        {isActive ? 'Activo' : 'Inactivo'}
      </span>
    );
  };

  const columns = [
    {
      key: 'name' as keyof Product,
      title: 'Producto',
      sortable: true,
      filterable: true,
      width: '25%',
      render: (value: string, row: Product) => (
        <div className="flex items-center gap-3">
          {row.image_url ? (
            <img 
              src={row.image_url} 
              alt={value}
              className="w-10 h-10 rounded-lg object-cover"
            />
          ) : (
            <div className="w-10 h-10 bg-gray-200 rounded-lg flex items-center justify-center">
              <Package className="w-5 h-5 text-gray-400" />
            </div>
          )}
          <div>
            <p className="font-medium text-gray-900">{value}</p>
            <p className="text-sm text-gray-500">SKU: {row.sku}</p>
          </div>
        </div>
      )
    },
    {
      key: 'category' as keyof Product,
      title: 'Categoría',
      sortable: true,
      filterable: true,
      width: '15%',
      render: (value: string) => (
        <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
          {value}
        </span>
      )
    },
    {
      key: 'price' as keyof Product,
      title: 'Precio',
      sortable: true,
      width: '15%',
      align: 'right' as const,
      render: (value: number) => (
        <div className="flex items-center gap-1">
          <DollarSign className="w-4 h-4 text-green-600" />
          <span className="font-semibold text-gray-900">{formatCurrency(value)}</span>
        </div>
      )
    },
    {
      key: 'stock' as keyof Product,
      title: 'Stock',
      sortable: true,
      width: '15%',
      align: 'center' as const,
      render: (value: number) => (
        <div className="text-center">
          <p className="font-semibold text-gray-900">{value}</p>
          {getStockStatus(value)}
        </div>
      )
    },
    {
      key: 'is_active' as keyof Product,
      title: 'Estado',
      sortable: true,
      width: '10%',
      align: 'center' as const,
      render: (value: boolean) => getStatusBadge(value)
    },
    {
      key: 'created_at' as keyof Product,
      title: 'Fecha Creación',
      sortable: true,
      width: '15%',
      render: (value: string) => (
        <span className="text-sm text-gray-600">
          {new Date(value).toLocaleDateString('es-ES')}
        </span>
      )
    }
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <ModernTable
        data={products}
        columns={columns}
        title={title}
        subtitle={subtitle}
        searchable={true}
        filterable={true}
        exportable={true}
        selectable={true}
        onEdit={onEdit}
        onDelete={onDelete}
        loading={loading}
        emptyMessage="No hay productos disponibles"
        className="shadow-xl"
      />
    </motion.div>
  );
};

export default ProductsTable;
