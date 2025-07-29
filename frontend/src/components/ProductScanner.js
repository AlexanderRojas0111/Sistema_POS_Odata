import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Alert,
  CircularProgress,
  IconButton,
  Tooltip,
  Snackbar,
  Chip
} from '@mui/material';
import { styled } from '@mui/material/styles';
import {
  QrCodeScanner as ScannerIcon,
  Keyboard as KeyboardIcon,
  Settings as SettingsIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Videocam as VideocamIcon
} from '@mui/icons-material';
import { useZxing } from 'react-zxing';

// Componentes styled para mejor UX
const ScannerContainer = styled(Box)(({ theme }) => ({
  border: `2px dashed ${theme.palette.primary.main}`,
  borderRadius: theme.shape.borderRadius * 2,
  padding: theme.spacing(3),
  textAlign: 'center',
  backgroundColor: theme.palette.action.hover,
  position: 'relative',
  minHeight: 120,
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  transition: 'all 0.3s ease',
  '&:hover': {
    borderColor: theme.palette.primary.dark,
    backgroundColor: theme.palette.action.selected,
  }
}));

const DisabledScannerContainer = styled(Box)(({ theme }) => ({
  border: `2px dashed ${theme.palette.text.disabled}`,
  borderRadius: theme.shape.borderRadius * 2,
  padding: theme.spacing(3),
  textAlign: 'center',
  backgroundColor: theme.palette.action.hover,
  transition: 'all 0.3s ease'
}));

const StatsContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  gap: theme.spacing(1),
  flexWrap: 'wrap',
  marginTop: theme.spacing(2)
}));

export default function ProductScanner({ onScan }) {
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState('');
  const [lastScanned, setLastScanned] = useState('');
  const [scanHistory, setScanHistory] = useState([]);
  const [showSuccess, setShowSuccess] = useState(false);
  const [scanCount, setScanCount] = useState(0);
  const [hasCamera, setHasCamera] = useState(true);

  const { ref } = useZxing({
    onDecodeResult(result) {
      const data = result.getText();
      if (data && data.trim()) {
        setLastScanned(data);
        setError('');
        setShowSuccess(true);
        setScanCount(prev => prev + 1);
        
        // Agregar al historial
        const newScan = {
          code: data,
          timestamp: new Date().toLocaleTimeString(),
          id: Date.now()
        };
        setScanHistory(prev => [newScan, ...prev.slice(0, 4)]);
        
        onScan(data);
        
        // Feedback visual
        setTimeout(() => {
          setLastScanned('');
          setShowSuccess(false);
        }, 2000);
      }
    },
    onError(error) {
      console.error('Scanner error:', error);
      setError('Error en el scanner. Verifique la conexión del dispositivo.');
    },
    paused: !isScanning
  });

  useEffect(() => {
    // Verificar si hay cámara disponible
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(stream => {
        stream.getTracks().forEach(track => track.stop());
        setHasCamera(true);
      })
      .catch(() => {
        setHasCamera(false);
        setError('No se detectó una cámara. Por favor, conecte una cámara para escanear.');
      });
  }, []);

  const toggleScanner = () => {
    setIsScanning(!isScanning);
    setError('');
  };

  return (
    <Paper sx={{ p: 2, mb: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center' }}>
          <ScannerIcon sx={{ mr: 1 }} />
          Scanner de Códigos
        </Typography>
        
        <Box>
          <Tooltip title="Estado de la cámara">
            <IconButton size="small" color={hasCamera ? "success" : "error"}>
              <VideocamIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Configurar scanner">
            <IconButton size="small">
              <SettingsIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {isScanning && hasCamera && (
        <ScannerContainer>
          <video ref={ref} style={{ width: '100%', maxHeight: '300px', objectFit: 'contain' }} />
          
          {lastScanned && (
            <Alert severity="success" sx={{ mt: 1, width: '100%', position: 'absolute', bottom: 16, left: 0, right: 0, mx: 2 }}>
              Código escaneado: {lastScanned}
            </Alert>
          )}
        </ScannerContainer>
      )}

      {(!isScanning || !hasCamera) && (
        <DisabledScannerContainer>
          <KeyboardIcon sx={{ fontSize: 40, color: 'text.disabled', mb: 1 }} />
          <Typography variant="body2" color="text.secondary">
            {!hasCamera ? 'Cámara no disponible' : 'Scanner desactivado'}
          </Typography>
        </DisabledScannerContainer>
      )}

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}

      <StatsContainer>
        <Button
          variant={isScanning ? "outlined" : "contained"}
          onClick={toggleScanner}
          startIcon={isScanning ? <KeyboardIcon /> : <ScannerIcon />}
          sx={{ flex: 1, minWidth: 200 }}
          disabled={!hasCamera}
        >
          {isScanning ? 'Desactivar Scanner' : 'Activar Scanner'}
        </Button>
        
        {scanCount > 0 && (
          <Chip
            icon={<CheckIcon />}
            label={`${scanCount} escaneos`}
            color="success"
            variant="outlined"
            size="small"
          />
        )}
      </StatsContainer>

      {/* Historial de escaneos recientes */}
      {scanHistory.length > 0 && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Escaneos recientes:
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {scanHistory.map((scan) => (
              <Chip
                key={scan.id}
                label={`${scan.code} (${scan.timestamp})`}
                size="small"
                variant="outlined"
                onClick={() => onScan(scan.code)}
                sx={{ cursor: 'pointer' }}
              />
            ))}
          </Box>
        </Box>
      )}

      <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
        💡 Tip: Mantenga el código de barras estable frente a la cámara para un escaneo exitoso
      </Typography>

      {/* Snackbar para feedback de éxito */}
      <Snackbar
        open={showSuccess}
        autoHideDuration={2000}
        onClose={() => setShowSuccess(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert severity="success" sx={{ width: '100%' }}>
          Código escaneado exitosamente
        </Alert>
      </Snackbar>
    </Paper>
  );
} 