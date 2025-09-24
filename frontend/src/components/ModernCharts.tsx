/**
 * Componentes de Gráficos Modernos - Sistema POS Sabrositas
 * Gráficos mejorados con animaciones y diseño atractivo
 */

import React from 'react';
import { motion } from 'framer-motion';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  RadialBarChart,
  RadialBar
} from 'recharts';
import { TrendingUp, TrendingDown, DollarSign, ShoppingCart, Users, Package } from 'lucide-react';

// Colores modernos y atractivos
const COLORS = {
  primary: '#3B82F6',
  secondary: '#8B5CF6',
  success: '#10B981',
  warning: '#F59E0B',
  danger: '#EF4444',
  info: '#06B6D4',
  gradient: {
    from: '#3B82F6',
    to: '#8B5CF6'
  }
};

const GRADIENT_COLORS = [
  '#3B82F6', '#8B5CF6', '#10B981', '#F59E0B', '#EF4444', '#06B6D4',
  '#EC4899', '#84CC16', '#F97316', '#6366F1', '#14B8A6', '#F43F5E'
];

interface ChartContainerProps {
  title: string;
  subtitle?: string;
  icon?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}

const ChartContainer: React.FC<ChartContainerProps> = ({ 
  title, 
  subtitle, 
  icon, 
  children, 
  className = '' 
}) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5 }}
    className={`bg-white rounded-2xl shadow-lg border border-gray-100 p-6 ${className}`}
  >
    <div className="flex items-center justify-between mb-6">
      <div>
        <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2">
          {icon}
          {title}
        </h3>
        {subtitle && (
          <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
        )}
      </div>
    </div>
    <div className="h-80">
      {children}
    </div>
  </motion.div>
);

interface SalesTrendChartProps {
  data: Array<{
    date: string;
    sales: number;
    revenue: number;
    day_name: string;
  }>;
}

export const SalesTrendChart: React.FC<SalesTrendChartProps> = ({ data }) => (
  <ChartContainer
    title="Tendencia de Ventas"
    subtitle="Ventas y ingresos por día"
    icon={<TrendingUp className="w-5 h-5 text-blue-500" />}
  >
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="salesGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={COLORS.primary} stopOpacity={0.3}/>
            <stop offset="95%" stopColor={COLORS.primary} stopOpacity={0}/>
          </linearGradient>
          <linearGradient id="revenueGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={COLORS.success} stopOpacity={0.3}/>
            <stop offset="95%" stopColor={COLORS.success} stopOpacity={0}/>
          </linearGradient>
        </defs>
        <XAxis 
          dataKey="day_name" 
          axisLine={false}
          tickLine={false}
          tick={{ fontSize: 12, fill: '#6B7280' }}
        />
        <YAxis 
          axisLine={false}
          tickLine={false}
          tick={{ fontSize: 12, fill: '#6B7280' }}
        />
        <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
        <Tooltip
          contentStyle={{
            backgroundColor: 'white',
            border: 'none',
            borderRadius: '12px',
            boxShadow: '0 10px 25px rgba(0,0,0,0.1)'
          }}
        />
        <Area
          type="monotone"
          dataKey="sales"
          stroke={COLORS.primary}
          fillOpacity={1}
          fill="url(#salesGradient)"
          strokeWidth={3}
        />
        <Area
          type="monotone"
          dataKey="revenue"
          stroke={COLORS.success}
          fillOpacity={1}
          fill="url(#revenueGradient)"
          strokeWidth={3}
        />
      </AreaChart>
    </ResponsiveContainer>
  </ChartContainer>
);

interface TopProductsChartProps {
  data: Array<{
    name: string;
    total_sold: number;
    total_revenue: number;
  }>;
}

export const TopProductsChart: React.FC<TopProductsChartProps> = ({ data }) => (
  <ChartContainer
    title="Productos Más Vendidos"
    subtitle="Top 10 productos por cantidad vendida"
    icon={<Package className="w-5 h-5 text-purple-500" />}
  >
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data.slice(0, 10)} layout="horizontal" margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
        <XAxis type="number" axisLine={false} tickLine={false} />
        <YAxis 
          dataKey="name" 
          type="category" 
          axisLine={false} 
          tickLine={false}
          width={120}
          tick={{ fontSize: 11 }}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: 'white',
            border: 'none',
            borderRadius: '12px',
            boxShadow: '0 10px 25px rgba(0,0,0,0.1)'
          }}
        />
        <Bar 
          dataKey="total_sold" 
          fill={COLORS.primary}
          radius={[0, 8, 8, 0]}
        />
      </BarChart>
    </ResponsiveContainer>
  </ChartContainer>
);

interface PaymentMethodsChartProps {
  data: Array<{
    method: string;
    count: number;
    total: number;
    percentage: number;
  }>;
}

export const PaymentMethodsChart: React.FC<PaymentMethodsChartProps> = ({ data }) => (
  <ChartContainer
    title="Métodos de Pago"
    subtitle="Distribución de pagos por método"
    icon={<DollarSign className="w-5 h-5 text-green-500" />}
  >
    <ResponsiveContainer width="100%" height="100%">
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={({ name, percentage }) => `${name} (${percentage}%)`}
          outerRadius={100}
          fill="#8884d8"
          dataKey="count"
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={GRADIENT_COLORS[index % GRADIENT_COLORS.length]} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{
            backgroundColor: 'white',
            border: 'none',
            borderRadius: '12px',
            boxShadow: '0 10px 25px rgba(0,0,0,0.1)'
          }}
        />
      </PieChart>
    </ResponsiveContainer>
  </ChartContainer>
);

interface RevenueChartProps {
  data: Array<{
    period: string;
    revenue: number;
    sales: number;
  }>;
}

export const RevenueChart: React.FC<RevenueChartProps> = ({ data }) => (
  <ChartContainer
    title="Ingresos por Período"
    subtitle="Comparación de ingresos y ventas"
    icon={<DollarSign className="w-5 h-5 text-green-500" />}
  >
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
        <XAxis 
          dataKey="period" 
          axisLine={false}
          tickLine={false}
          tick={{ fontSize: 12, fill: '#6B7280' }}
        />
        <YAxis 
          axisLine={false}
          tickLine={false}
          tick={{ fontSize: 12, fill: '#6B7280' }}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: 'white',
            border: 'none',
            borderRadius: '12px',
            boxShadow: '0 10px 25px rgba(0,0,0,0.1)'
          }}
        />
        <Legend />
        <Bar 
          dataKey="revenue" 
          fill={COLORS.success}
          radius={[4, 4, 0, 0]}
          name="Ingresos"
        />
        <Bar 
          dataKey="sales" 
          fill={COLORS.primary}
          radius={[4, 4, 0, 0]}
          name="Ventas"
        />
      </BarChart>
    </ResponsiveContainer>
  </ChartContainer>
);

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: number;
  icon: React.ReactNode;
  color: string;
  trend?: 'up' | 'down' | 'neutral';
}

export const MetricCard: React.FC<MetricCardProps> = ({ 
  title, 
  value, 
  change, 
  icon, 
  color, 
  trend = 'neutral' 
}) => (
  <motion.div
    initial={{ opacity: 0, scale: 0.9 }}
    animate={{ opacity: 1, scale: 1 }}
    transition={{ duration: 0.3 }}
    className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 hover:shadow-xl transition-shadow duration-300"
  >
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-gray-600">{title}</p>
        <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
        {change !== undefined && (
          <div className="flex items-center mt-2">
            {trend === 'up' && <TrendingUp className="w-4 h-4 text-green-500 mr-1" />}
            {trend === 'down' && <TrendingDown className="w-4 h-4 text-red-500 mr-1" />}
            <span className={`text-sm font-medium ${
              trend === 'up' ? 'text-green-600' : 
              trend === 'down' ? 'text-red-600' : 
              'text-gray-600'
            }`}>
              {change > 0 ? '+' : ''}{change}%
            </span>
          </div>
        )}
      </div>
      <div className={`p-3 rounded-xl ${color}`}>
        {icon}
      </div>
    </div>
  </motion.div>
);

interface PerformanceChartProps {
  data: Array<{
    name: string;
    performance: number;
    target: number;
  }>;
}

export const PerformanceChart: React.FC<PerformanceChartProps> = ({ data }) => (
  <ChartContainer
    title="Rendimiento vs Objetivo"
    subtitle="Comparación de rendimiento actual vs objetivos"
    icon={<TrendingUp className="w-5 h-5 text-blue-500" />}
  >
    <ResponsiveContainer width="100%" height="100%">
      <RadialBarChart cx="50%" cy="50%" innerRadius="20%" outerRadius="90%" data={data}>
        <RadialBar
          dataKey="performance"
          cornerRadius={10}
          fill={COLORS.primary}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: 'white',
            border: 'none',
            borderRadius: '12px',
            boxShadow: '0 10px 25px rgba(0,0,0,0.1)'
          }}
        />
      </RadialBarChart>
    </ResponsiveContainer>
  </ChartContainer>
);

export default {
  SalesTrendChart,
  TopProductsChart,
  PaymentMethodsChart,
  RevenueChart,
  MetricCard,
  PerformanceChart,
  ChartContainer
};
