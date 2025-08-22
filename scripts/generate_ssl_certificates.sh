#!/bin/bash

# Script para generar certificados SSL para Sistema POS Odata
# Dominio: pos.odata.com
# Uso: ./generate_ssl_certificates.sh [--letsencrypt|--self-signed]

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuración
DOMAIN="pos.odata.com"
CERT_DIR="/etc/nginx/ssl"
CERT_FILE="$CERT_DIR/$DOMAIN.crt"
KEY_FILE="$CERT_DIR/$DOMAIN.key"
CSR_FILE="$CERT_DIR/$DOMAIN.csr"
CONFIG_FILE="$CERT_DIR/openssl.conf"

# Función para mostrar mensajes
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Función para verificar dependencias
check_dependencies() {
    log_info "Verificando dependencias..."
    
    if ! command -v openssl &> /dev/null; then
        log_error "OpenSSL no está instalado. Instalando..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y openssl
        elif command -v yum &> /dev/null; then
            sudo yum install -y openssl
        else
            log_error "No se pudo instalar OpenSSL. Instálalo manualmente."
            exit 1
        fi
    fi
    
    if ! command -v certbot &> /dev/null; then
        log_warning "Certbot no está instalado. Para certificados Let's Encrypt, instálalo:"
        echo "  Ubuntu/Debian: sudo apt-get install certbot"
        echo "  CentOS/RHEL: sudo yum install certbot"
    fi
    
    log_success "Dependencias verificadas"
}

# Función para crear directorio de certificados
create_cert_dir() {
    log_info "Creando directorio de certificados..."
    
    if [ ! -d "$CERT_DIR" ]; then
        sudo mkdir -p "$CERT_DIR"
        sudo chmod 700 "$CERT_DIR"
        log_success "Directorio creado: $CERT_DIR"
    else
        log_info "Directorio ya existe: $CERT_DIR"
    fi
}

# Función para generar certificado auto-firmado
generate_self_signed() {
    log_info "Generando certificado auto-firmado..."
    
    # Crear archivo de configuración OpenSSL
    cat > "$CONFIG_FILE" << EOF
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = MX
ST = Estado de México
L = Ciudad de México
O = Odata Systems
OU = IT Department
CN = $DOMAIN
emailAddress = admin@$DOMAIN

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = $DOMAIN
DNS.2 = www.$DOMAIN
DNS.3 = staging.$DOMAIN
IP.1 = 127.0.0.1
EOF
    
    # Generar clave privada
    log_info "Generando clave privada..."
    sudo openssl genrsa -out "$KEY_FILE" 4096
    sudo chmod 600 "$KEY_FILE"
    
    # Generar certificado
    log_info "Generando certificado..."
    sudo openssl req -new -x509 -key "$KEY_FILE" -out "$CERT_FILE" -days 365 -config "$CONFIG_FILE"
    sudo chmod 644 "$CERT_FILE"
    
    # Generar CSR (opcional)
    log_info "Generando CSR..."
    sudo openssl req -new -key "$KEY_FILE" -out "$CSR_FILE" -config "$CONFIG_FILE"
    
    log_success "Certificado auto-firmado generado exitosamente"
    log_info "Certificado: $CERT_FILE"
    log_info "Clave privada: $KEY_FILE"
    log_info "CSR: $CSR_FILE"
}

# Función para generar certificado con Let's Encrypt
generate_letsencrypt() {
    log_info "Generando certificado con Let's Encrypt..."
    
    if ! command -v certbot &> /dev/null; then
        log_error "Certbot no está instalado. Instálalo primero."
        exit 1
    fi
    
    # Verificar que el dominio resuelva correctamente
    log_info "Verificando resolución del dominio..."
    if ! nslookup "$DOMAIN" &> /dev/null; then
        log_error "El dominio $DOMAIN no resuelve. Verifica la configuración DNS."
        exit 1
    fi
    
    # Crear certificado
    log_info "Solicitando certificado de Let's Encrypt..."
    sudo certbot certonly --standalone \
        --email admin@$DOMAIN \
        --agree-tos \
        --no-eff-email \
        --domains $DOMAIN,www.$DOMAIN \
        --cert-path "$CERT_FILE" \
        --key-path "$KEY_FILE"
    
    if [ $? -eq 0 ]; then
        log_success "Certificado de Let's Encrypt generado exitosamente"
        
        # Crear enlaces simbólicos para Nginx
        sudo ln -sf /etc/letsencrypt/live/$DOMAIN/fullchain.pem "$CERT_FILE"
        sudo ln -sf /etc/letsencrypt/live/$DOMAIN/privkey.pem "$KEY_FILE"
        
        log_info "Enlaces simbólicos creados para Nginx"
    else
        log_error "Error al generar certificado de Let's Encrypt"
        exit 1
    fi
}

# Función para verificar certificado
verify_certificate() {
    log_info "Verificando certificado..."
    
    if [ -f "$CERT_FILE" ] && [ -f "$KEY_FILE" ]; then
        # Verificar que el certificado y la clave coincidan
        CERT_HASH=$(openssl x509 -noout -modulus -in "$CERT_FILE" | openssl md5)
        KEY_HASH=$(openssl rsa -noout -modulus -in "$KEY_FILE" | openssl md5)
        
        if [ "$CERT_HASH" = "$KEY_HASH" ]; then
            log_success "Certificado y clave privada coinciden"
        else
            log_error "Certificado y clave privada NO coinciden"
            exit 1
        fi
        
        # Mostrar información del certificado
        log_info "Información del certificado:"
        openssl x509 -in "$CERT_FILE" -text -noout | grep -E "(Subject:|Not Before|Not After|DNS:)"
        
        # Verificar fecha de expiración
        EXPIRY=$(openssl x509 -in "$CERT_FILE" -noout -enddate | cut -d= -f2)
        log_info "Fecha de expiración: $EXPIRY"
        
    else
        log_error "Archivos de certificado no encontrados"
        exit 1
    fi
}

# Función para configurar renovación automática (Let's Encrypt)
setup_auto_renewal() {
    if command -v certbot &> /dev/null; then
        log_info "Configurando renovación automática..."
        
        # Crear script de renovación
        RENEWAL_SCRIPT="/usr/local/bin/renew-ssl-certs.sh"
        sudo tee "$RENEWAL_SCRIPT" > /dev/null << 'EOF'
#!/bin/bash
# Script de renovación automática de certificados SSL

DOMAIN="pos.odata.com"
CERT_DIR="/etc/nginx/ssl"
CERT_FILE="$CERT_DIR/$DOMAIN.crt"
KEY_FILE="$CERT_DIR/$DOMAIN.key"

# Renovar certificados
certbot renew --quiet

# Verificar si se renovaron
if [ $? -eq 0 ]; then
    # Actualizar enlaces simbólicos
    ln -sf /etc/letsencrypt/live/$DOMAIN/fullchain.pem "$CERT_FILE"
    ln -sf /etc/letsencrypt/live/$DOMAIN/privkey.pem "$KEY_FILE"
    
    # Recargar Nginx
    systemctl reload nginx
    
    echo "$(date): Certificados SSL renovados exitosamente" >> /var/log/ssl-renewal.log
else
    echo "$(date): Error al renovar certificados SSL" >> /var/log/ssl-renewal.log
fi
EOF
        
        sudo chmod +x "$RENEWAL_SCRIPT"
        
        # Agregar al crontab para renovación diaria
        (crontab -l 2>/dev/null; echo "0 2 * * * $RENEWAL_SCRIPT") | crontab -
        
        log_success "Renovación automática configurada (diaria a las 2:00 AM)"
    fi
}

# Función para mostrar ayuda
show_help() {
    echo "Uso: $0 [OPCIÓN]"
    echo ""
    echo "Opciones:"
    echo "  --letsencrypt    Generar certificado con Let's Encrypt (recomendado para producción)"
    echo "  --self-signed    Generar certificado auto-firmado (solo para desarrollo/pruebas)"
    echo "  --verify         Verificar certificado existente"
    echo "  --help           Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0 --letsencrypt    # Generar certificado de Let's Encrypt"
    echo "  $0 --self-signed    # Generar certificado auto-firmado"
    echo "  $0 --verify         # Verificar certificado existente"
}

# Función principal
main() {
    log_info "Iniciando generación de certificados SSL para $DOMAIN"
    
    # Verificar si se ejecuta como root
    if [ "$EUID" -eq 0 ]; then
        log_error "No ejecutes este script como root. Usa sudo cuando sea necesario."
        exit 1
    fi
    
    # Parsear argumentos
    case "${1:-}" in
        --letsencrypt)
            check_dependencies
            create_cert_dir
            generate_letsencrypt
            verify_certificate
            setup_auto_renewal
            ;;
        --self-signed)
            check_dependencies
            create_cert_dir
            generate_self_signed
            verify_certificate
            ;;
        --verify)
            verify_certificate
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            log_error "Opción no válida. Usa --help para ver las opciones disponibles."
            exit 1
            ;;
    esac
    
    log_success "Proceso completado exitosamente"
    
    # Mostrar próximos pasos
    echo ""
    log_info "Próximos pasos:"
    echo "1. Verifica que los archivos de certificado estén en: $CERT_DIR"
    echo "2. Asegúrate de que Nginx tenga permisos de lectura en los archivos"
    echo "3. Recarga Nginx: sudo systemctl reload nginx"
    echo "4. Verifica la configuración: sudo nginx -t"
    echo "5. Prueba el sitio: curl -I https://$DOMAIN"
}

# Ejecutar función principal
main "$@"
