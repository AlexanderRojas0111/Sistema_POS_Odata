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
from .electronic_invoice import ElectronicInvoice, ElectronicInvoiceItem
from .support_document import SupportDocument
from .accounting import AccountingEntry, AccountingEntryLine, ChartOfAccounts
from .digital_certificate import DigitalCertificate, CertificateUsage
from .support import SupportTicket, SupportMessage, SupportChat, ChatMessage
from .help import HelpArticle, FAQ
from .payroll import Employee, PayrollPeriod, Payroll, PayrollItem, PayrollConfig
from .accounts_receivable import Customer, Invoice, AccountsReceivableInvoiceItem, Payment, PaymentAllocation
from .multi_payment import MultiPayment, PaymentDetail
from .quotation import Quotation, QuotationItem, QuotationApproval, QuotationTemplate

# Importar db al final para evitar importaciones circulares
from app import db

__all__ = [
    'db',
    'User',
    'Product', 
    'Sale',
    'SaleItem',
    'InventoryMovement',
    'ProductEmbedding',
    'DocumentEmbedding',
    'ElectronicInvoice',
    'ElectronicInvoiceItem',
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
    'FAQ',
    'Employee',
    'PayrollPeriod',
    'Payroll',
    'PayrollItem',
    'PayrollConfig',
    'Customer',
    'Invoice',
    'AccountsReceivableInvoiceItem',
    'Payment',
    'PaymentAllocation',
    'MultiPayment',
    'PaymentDetail',
    'Quotation',
    'QuotationItem',
    'QuotationApproval',
    'QuotationTemplate'
]
