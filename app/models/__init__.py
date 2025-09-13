"""
Models Package - Sistema POS Sabrositas
======================================
Modelos de base de datos del sistema.
"""

from .user import User
from .product import Product
from .sale import Sale, SaleItem
from .inventory import InventoryMovement
from .ai_models import ProductEmbedding, DocumentEmbedding
from .electronic_invoice import ElectronicInvoice, InvoiceItem
from .support_document import SupportDocument
from .accounting import AccountingEntry, AccountingEntryLine, ChartOfAccounts
from .digital_certificate import DigitalCertificate, CertificateUsage
from .support import SupportTicket, SupportMessage, SupportChat, ChatMessage
from .help import HelpArticle, FAQ

__all__ = [
    'User',
    'Product', 
    'Sale',
    'SaleItem',
    'InventoryMovement',
    'ProductEmbedding',
    'DocumentEmbedding',
    'ElectronicInvoice',
    'InvoiceItem',
    'SupportDocument',
    'AccountingEntry',
    'AccountingEntryLine',
    'ChartOfAccounts',
    'DigitalCertificate',
    'CertificateUsage',
    'SupportTicket',
    'SupportMessage',
    'SupportChat',
    'ChatMessage',
    'HelpArticle',
    'FAQ'
]
