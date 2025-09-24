import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Grid,
  Typography,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  TextField,
  Divider,
  Chip,
  Alert,
  Snackbar,
  Card,
  CardContent,
  CardActions,
  Fab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  Add as AddIcon,
  Remove as RemoveIcon,
  Delete as DeleteIcon,
  Receipt as ReceiptIcon,
  ShoppingCart as CartIcon,
  Payment as PaymentIcon,
  Clear as ClearIcon
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import api from '../services/api';
import ProductScanner from './ProductScanner';
import Ticket from './Ticket';

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  margin: theme.spacing(2),
  minHeight: '80vh',
  display: 'flex',
  flexDirection: 'column'
}));

const CartItem = styled(ListItem)(({ theme }) => ({
  border: `1px solid ${theme.palette.divider}`,
  borderRadius: theme.spacing(1),
  marginBottom: theme.spacing(1),
  backgroundColor: theme.palette.background.paper
}));

const TotalCard = styled(Card)(({ theme }) => ({
  backgroundColor: theme.palette.primary.main,
  color: theme.palette.primary.contrastText,
  marginTop: theme.spacing(2)
}));

export default function PosBox() {
  const [cart, setCart] = useState([]);
  const [ticket, setTicket] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [manualCode, setManualCode] = useState('');
  const [paymentDialog, setPaymentDialog] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState('cash');

  // Calcular totales
  const subtotal = cart.reduce((sum, item) => sum + (item.quantity * item.price), 0);
  const tax = subtotal * 0.16; // 16% IVA
  const total = subtotal + tax;

  const handleScan = async (barcode) => {
    await addProductToCart(barcode);
  };

  const handleManualAdd = async () => {
    if (manualCode.trim()) {
      await addProductToCart(manualCode.trim());
      setManualCode('');
    }
  };

  const addProductToCart = async (code) => {
    setLoading(true);
    setError('');
    
    try {
      const res = await api.get(`/api/v1/products/?code=${code}`);
      if (res.data && res.data.items && res.data.items.length > 0) {
        const product = res.data.items[0];
        addToCart(product);
        setSuccess(`Producto agregado: ${product.name}`);
      } else {
        setError('Producto no encontrado');
      }
    } catch (err) {
      setError('Error al buscar producto');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const addToCart = (product) => {
    const existingItem = cart.find(item => item.id === product.id);
    
    if (existingItem) {
      setCart(cart.map(item => 
        item.id === product.id 
          ? { ...item, quantity: item.quantity + 1 }
          : item
      ));
    } else {
      setCart([...cart, { ...product, quantity: 1 }]);
    }
  };

  const updateQuantity = (productId, newQuantity) => {
    if (newQuantity <= 0) {
      removeFromCart(productId);
    } else {
      setCart(cart.map(item => 
        item.id === productId 
          ? { ...item, quantity: newQuantity }
          : item
      ));
    }
  };

  const removeFromCart = (productId) => {
    setCart(cart.filter(item => item.id !== productId));
  };

  const clearCart = () => {
    setCart([]);
    setTicket(null);
  };

  const handlePayment = () => {
    if (cart.length === 0) {
      setError('El carrito está vacío');
      return;
    }
    setPaymentDialog(true);
  };

  const processSale = async () => {
    setLoading(true);
    setError('');
    
    try {
      const saleData = {
        items: cart.map(item => ({
          product_id: item.id,
          quantity: item.quantity,
          unit_price: item.price
        })),
        payment_method: paymentMethod,
        total_amount: total
      };

      const res = await api.post('/api/v1/sales/', saleData);
      setTicket(res.data);
      setCart([]);
      setSuccess('Venta registrada exitosamente');
      setPaymentDialog(false);
    } catch (err) {
      setError('Error al procesar la venta');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleManualAdd();
    }
  };

  return (
    <Box sx={{ flexGrow: 1, p: 2 }}>
      <Grid container spacing={3}>
        {/* Panel izquierdo - Productos y Scanner */}
        <Grid item xs={12} md={8}>
          <StyledPaper>
            <Typography variant="h4" gutterBottom>
              <CartIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Punto de Venta
            </Typography>
            
            <Divider sx={{ my: 2 }} />
            
            {/* Scanner y entrada manual */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Escanear Producto
              </Typography>
              <ProductScanner onScan={handleScan} />
              
              <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                <TextField
                  fullWidth
                  label="Código de producto"
                  value={manualCode}
                  onChange={(e) => setManualCode(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ingrese código manualmente"
                />
                <Button
                  variant="contained"
                  onClick={handleManualAdd}
                  disabled={loading || !manualCode.trim()}
                  startIcon={<AddIcon />}
                >
                  Agregar
                </Button>
              </Box>
            </Box>

            {/* Lista de productos en carrito */}
            <Typography variant="h6" gutterBottom>
              Productos en Carrito ({cart.length})
            </Typography>
            
            {cart.length === 0 ? (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <CartIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
                <Typography variant="body1" color="text.secondary">
                  El carrito está vacío. Escanee productos para comenzar.
                </Typography>
              </Box>
            ) : (
              <List>
                {cart.map((item) => (
                  <CartItem key={item.id}>
                    <ListItemText
                      primary={item.name}
                      secondary={`$${item.price.toFixed(2)} c/u`}
                    />
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <IconButton
                        size="small"
                        onClick={() => updateQuantity(item.id, item.quantity - 1)}
                      >
                        <RemoveIcon />
                      </IconButton>
                      <Chip label={item.quantity} color="primary" />
                      <IconButton
                        size="small"
                        onClick={() => updateQuantity(item.id, item.quantity + 1)}
                      >
                        <AddIcon />
                      </IconButton>
                      <Typography variant="body2" sx={{ minWidth: 80, textAlign: 'right' }}>
                        ${(item.quantity * item.price).toFixed(2)}
                      </Typography>
                      <IconButton
                        color="error"
                        onClick={() => removeFromCart(item.id)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Box>
                  </CartItem>
                ))}
              </List>
            )}
          </StyledPaper>
        </Grid>

        {/* Panel derecho - Totales y Pago */}
        <Grid item xs={12} md={4}>
          <Box sx={{ position: 'sticky', top: 16 }}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Resumen de Venta
                </Typography>
                
                <Box sx={{ my: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography>Subtotal:</Typography>
                    <Typography>${subtotal.toFixed(2)}</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography>IVA (16%):</Typography>
                    <Typography>${tax.toFixed(2)}</Typography>
                  </Box>
                  <Divider sx={{ my: 1 }} />
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="h6">Total:</Typography>
                    <Typography variant="h6" color="primary">
                      ${total.toFixed(2)}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
              
              <CardActions sx={{ flexDirection: 'column', gap: 1 }}>
                <Button
                  fullWidth
                  variant="contained"
                  size="large"
                  startIcon={<PaymentIcon />}
                  onClick={handlePayment}
                  disabled={cart.length === 0 || loading}
                >
                  Cobrar
                </Button>
                
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<ClearIcon />}
                  onClick={clearCart}
                  disabled={cart.length === 0}
                >
                  Limpiar Carrito
                </Button>
              </CardActions>
            </Card>

            {/* Ticket generado */}
            {ticket && (
              <Box sx={{ mt: 2 }}>
                <Ticket data={ticket} />
              </Box>
            )}
          </Box>
        </Grid>
      </Grid>

      {/* Diálogo de pago */}
      <Dialog open={paymentDialog} onClose={() => setPaymentDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Método de Pago</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <Typography variant="h6">Total a pagar: ${total.toFixed(2)}</Typography>
            
            <Box>
              <Typography variant="subtitle1" gutterBottom>
                Seleccione método de pago:
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {['cash', 'card', 'transfer'].map((method) => (
                  <Chip
                    key={method}
                    label={method === 'cash' ? 'Efectivo' : method === 'card' ? 'Tarjeta' : 'Transferencia'}
                    onClick={() => setPaymentMethod(method)}
                    color={paymentMethod === method ? 'primary' : 'default'}
                    variant={paymentMethod === method ? 'filled' : 'outlined'}
                  />
                ))}
              </Box>
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPaymentDialog(false)}>Cancelar</Button>
          <Button
            variant="contained"
            onClick={processSale}
            disabled={loading}
            startIcon={<ReceiptIcon />}
          >
            {loading ? 'Procesando...' : 'Confirmar Venta'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Notificaciones */}
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError('')}
      >
        <Alert severity="error" onClose={() => setError('')}>
          {error}
        </Alert>
      </Snackbar>

      <Snackbar
        open={!!success}
        autoHideDuration={4000}
        onClose={() => setSuccess('')}
      >
        <Alert severity="success" onClose={() => setSuccess('')}>
          {success}
        </Alert>
      </Snackbar>
    </Box>
  );
} 