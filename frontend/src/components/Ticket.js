import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Divider,
  List,
  ListItem,
  ListItemText,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid
} from '@mui/material';
import {
  Receipt as ReceiptIcon,
  Print as PrintIcon,
  Download as DownloadIcon,
  Share as ShareIcon,
  Close as CloseIcon
} from '@mui/icons-material';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import jsPDF from 'jspdf';
import { styled } from '@mui/material/styles';

const TicketContainer = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  maxWidth: 400,
  margin: '0 auto',
  backgroundColor: '#fff',
  border: `2px solid ${theme.palette.primary.main}`,
  borderRadius: theme.spacing(2)
}));

export default function Ticket({ data, onClose }) {
  const [showDialog, setShowDialog] = useState(false);
  const [loading, setLoading] = useState(false);

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('es-MX', {
      style: 'currency',
      currency: 'MXN'
    }).format(amount);
  };

  const formatDate = (dateString) => {
    return format(new Date(dateString), 'dd/MM/yyyy HH:mm', { locale: es });
  };

  const handlePrint = () => {
    window.print();
  };

  const handleDownload = async () => {
    setLoading(true);
    try {
    const doc = new jsPDF();
      
      // Configurar fuente
      doc.setFontSize(16);
      doc.text('TICKET DE VENTA', 105, 20, { align: 'center' });
      
      doc.setFontSize(10);
      doc.text(`Ticket #: ${data.invoice_number}`, 20, 40);
      doc.text(`Fecha: ${formatDate(data.created_at)}`, 20, 50);
      doc.text(`Cliente: ${data.customer?.name || 'Cliente General'}`, 20, 60);
      doc.text(`Vendedor: ${data.user?.name || 'Sistema'}`, 20, 70);
      
      // Línea separadora
      doc.line(20, 80, 190, 80);
      
      let yPosition = 90;
      data.items?.forEach((item, index) => {
        doc.text(`${item.product.name}`, 20, yPosition);
        doc.text(`${item.quantity} x ${formatCurrency(item.unit_price)}`, 120, yPosition);
        doc.text(formatCurrency(item.quantity * item.unit_price), 170, yPosition);
        yPosition += 10;
      });
      
      // Línea separadora
      doc.line(20, yPosition, 190, yPosition);
      yPosition += 10;
      
      // Totales
      doc.setFontSize(12);
      doc.text('Subtotal:', 120, yPosition);
      doc.text(formatCurrency(data.subtotal || 0), 170, yPosition);
      yPosition += 10;
      
      doc.text('IVA (16%):', 120, yPosition);
      doc.text(formatCurrency(data.tax || 0), 170, yPosition);
      yPosition += 10;
      
      doc.setFontSize(14);
      doc.text('TOTAL:', 120, yPosition);
      doc.text(formatCurrency(data.total_amount), 170, yPosition);
      
      // Pie de página
      doc.setFontSize(8);
      doc.text('¡Gracias por su compra!', 105, 250, { align: 'center' });
      doc.text('Sistema POS con IA', 105, 260, { align: 'center' });
      
      doc.save(`ticket-${data.invoice_number}.pdf`);
    } catch (error) {
      console.error('Error generando PDF:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: `Ticket ${data.invoice_number}`,
        text: `Ticket de venta por ${formatCurrency(data.total_amount)}`,
        url: window.location.href
      });
    } else {
      // Fallback: copiar al portapapeles
      navigator.clipboard.writeText(`Ticket ${data.invoice_number} - ${formatCurrency(data.total_amount)}`);
    }
  };

  if (!data) return null;

  return (
    <>
      <TicketContainer elevation={3}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center' }}>
            <ReceiptIcon sx={{ mr: 1 }} />
            Ticket de Venta
          </Typography>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>

        <Divider sx={{ mb: 2 }} />

        {/* Información del ticket */}
        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              Ticket #
            </Typography>
            <Typography variant="body1" fontWeight="bold">
              {data.invoice_number}
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              Fecha
            </Typography>
            <Typography variant="body1">
              {formatDate(data.created_at)}
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              Cliente
            </Typography>
            <Typography variant="body1">
              {data.customer?.name || 'Cliente General'}
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              Método de Pago
            </Typography>
            <Chip 
              label={data.payment_method === 'cash' ? 'Efectivo' : 
                     data.payment_method === 'card' ? 'Tarjeta' : 'Transferencia'}
              size="small"
              color="primary"
            />
          </Grid>
        </Grid>

        <Divider sx={{ mb: 2 }} />

        {/* Lista de productos */}
        <Typography variant="subtitle2" gutterBottom>
          Productos
        </Typography>
        <List dense>
          {data.items?.map((item, index) => (
            <ListItem key={index} sx={{ px: 0 }}>
              <ListItemText
                primary={item.product.name}
                secondary={`${item.quantity} x ${formatCurrency(item.unit_price)}`}
              />
              <Typography variant="body2" fontWeight="bold">
                {formatCurrency(item.quantity * item.unit_price)}
              </Typography>
            </ListItem>
          ))}
        </List>

        <Divider sx={{ my: 2 }} />

        {/* Totales */}
        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography>Subtotal:</Typography>
            <Typography>{formatCurrency(data.subtotal || 0)}</Typography>
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography>IVA (16%):</Typography>
            <Typography>{formatCurrency(data.tax || 0)}</Typography>
          </Box>
          <Divider sx={{ my: 1 }} />
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Typography variant="h6">Total:</Typography>
            <Typography variant="h6" color="primary" fontWeight="bold">
              {formatCurrency(data.total_amount)}
            </Typography>
          </Box>
        </Box>

        {/* Acciones */}
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <Button
            variant="outlined"
            startIcon={<PrintIcon />}
            onClick={handlePrint}
            size="small"
          >
            Imprimir
          </Button>
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={handleDownload}
            disabled={loading}
            size="small"
          >
            {loading ? 'Generando...' : 'PDF'}
          </Button>
          <Button
            variant="outlined"
            startIcon={<ShareIcon />}
            onClick={handleShare}
            size="small"
          >
            Compartir
          </Button>
        </Box>

        <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block', textAlign: 'center' }}>
          ¡Gracias por su compra!
        </Typography>
      </TicketContainer>

      {/* Diálogo de vista previa */}
      <Dialog 
        open={showDialog} 
        onClose={() => setShowDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Vista Previa del Ticket</DialogTitle>
        <DialogContent>
          <Ticket data={data} onClose={() => setShowDialog(false)} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowDialog(false)}>Cerrar</Button>
        </DialogActions>
      </Dialog>
    </>
  );
} 