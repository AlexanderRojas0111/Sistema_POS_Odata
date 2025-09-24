/**
 * Tabla de Ventas Moderna - Sistema POS Sabrositas
 * Tabla optimizada para mostrar ventas con mejor presentación
 */

import React from 'react';
import { motion } from 'framer-motion';
import { ShoppingCart, Edit, Trash2, Eye, DollarSign, User, Calendar, CreditCard } from 'lucide-react';
import ModernTable from './ModernTable';

interface Sale {
  id: number;
  total: number;
  payment_method: string;
  customer_name?: string;
  user_name: string;
  created_at: string;
  updated_at: string;
  status: string;
  items_count: number;
  discount?: number;
  tax?: number;
}

interface SalesTableProps {
  sales: Sale[];
  onEdit?: (sale: Sale) => void;
  onDelete?: (sale: Sale) => void;
  onView?: (sale: Sale) => void;
  loading?: boolean;
  title?: string;
  subtitle?: string;
}

export const SalesTable: React.FC<SalesTableProps> = ({
  sales,
  onEdit,
  onDelete,
  onView,
  loading = false,
  title = "Ventas",
  subtitle = "Historial de ventas realizadas"
}) => {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0
    }).format(value);
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      'completed': { color: 'bg-green-100 text-green-800', text: 'Completada' },
      'pending': { color: 'bg-yellow-100 text-yellow-800', text: 'Pendiente' },
      'cancelled': { color: 'bg-red-100 text-red-800', text: 'Cancelada' },
      'refunded': { color: 'bg-gray-100 text-gray-800', text: 'Reembolsada' }
    };

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.pending;

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
        {config.text}
      </span>
    );
  };

  const getPaymentMethodIcon = (method: string) => {
    const icons = {
      'cash': '💵',
      'card': '💳',
      'transfer': '🏦',
      'qr': '📱',
      'other': '💰'
    };
    return icons[method as keyof typeof icons] || '💰';
  };

  const columns = [
    {
      key: 'id' as keyof Sale,
      title: 'ID Venta',
      sortable: true,
      width: '10%',
      render: (value: number) => (
        <div className="flex items-center gap-2">
          <ShoppingCart className="w-4 h-4 text-blue-600" />
          <span className="font-mono text-sm font-semibold text-gray-900">
            #{value.toString().padStart(6, '0')}
          </span>
        </div>
      )
    },
    {
      key: 'total' as keyof Sale,
      title: 'Total',
      sortable: true,
      width: '15%',
      align: 'right' as const,
      render: (value: number) => (
        <div className="flex items-center gap-1 justify-end">
          <DollarSign className="w-4 h-4 text-green-600" />
          <span className="font-bold text-lg text-gray-900">{formatCurrency(value)}</span>
        </div>
      )
    },
    {
      key: 'payment_method' as keyof Sale,
      title: 'Método de Pago',
      sortable: true,
      width: '15%',
      render: (value: string) => (
        <div className="flex items-center gap-2">
          <span className="text-lg">{getPaymentMethodIcon(value)}</span>
          <span className="capitalize text-sm font-medium text-gray-700">
            {value === 'card' ? 'Tarjeta' : 
             value === 'cash' ? 'Efectivo' :
             value === 'transfer' ? 'Transferencia' :
             value === 'qr' ? 'QR' : value}
          </span>
        </div>
      )
    },
    {
      key: 'customer_name' as keyof Sale,
      title: 'Cliente',
      sortable: true,
      width: '15%',
      render: (value: string, row: Sale) => (
        <div className="flex items-center gap-2">
          <User className="w-4 h-4 text-gray-400" />
          <span className="text-sm font-medium text-gray-900">
            {value || 'Cliente General'}
          </span>
        </div>
      )
    },
    {
      key: 'user_name' as keyof Sale,
      title: 'Vendedor',
      sortable: true,
      width: '15%',
      render: (value: string) => (
        <span className="text-sm font-medium text-gray-700">{value}</span>
      )
    },
    {
      key: 'items_count' as keyof Sale,
      title: 'Items',
      sortable: true,
      width: '8%',
      align: 'center' as const,
      render: (value: number) => (
        <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
          {value}
        </span>
      )
    },
    {
      key: 'status' as keyof Sale,
      title: 'Estado',
      sortable: true,
      width: '12%',
      align: 'center' as const,
      render: (value: string) => getStatusBadge(value)
    },
    {
      key: 'created_at' as keyof Sale,
      title: 'Fecha',
      sortable: true,
      width: '15%',
      render: (value: string) => (
        <div className="flex items-center gap-1">
          <Calendar className="w-4 h-4 text-gray-400" />
          <span className="text-sm text-gray-600">
            {new Date(value).toLocaleDateString('es-ES', {
              day: '2-digit',
              month: '2-digit',
              year: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
            })}
          </span>
        </div>
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
        data={sales}
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
        emptyMessage="No hay ventas disponibles"
        className="shadow-xl"
      />
    </motion.div>
  );
};

export default SalesTable;
