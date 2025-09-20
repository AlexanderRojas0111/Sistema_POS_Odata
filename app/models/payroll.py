"""
Payroll Models - Sistema POS Sabrositas
======================================
Modelos para nómina electrónica y liquidación de salarios.
"""

from app import db
from datetime import datetime, date
from typing import Dict, Any, Optional, List
from decimal import Decimal
import uuid

class Employee(db.Model):
    """Modelo de empleado para nómina"""
    
    __tablename__ = 'employees'
    
    # Campos principales
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    employee_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Información personal
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    document_type = db.Column(db.String(10), nullable=False)  # CC, CE, NIT, etc.
    document_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    
    # Información laboral
    position = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    hire_date = db.Column(db.Date, nullable=False)
    termination_date = db.Column(db.Date, nullable=True)
    
    # Salario y beneficios
    base_salary = db.Column(db.Numeric(15, 2), nullable=False)
    salary_type = db.Column(db.String(20), default='monthly')  # monthly, daily, hourly
    work_hours_per_day = db.Column(db.Numeric(5, 2), default=8.0)
    work_days_per_week = db.Column(db.Integer, default=6)
    
    # Estado
    is_active = db.Column(db.Boolean, default=True, index=True)
    status = db.Column(db.String(20), default='active')  # active, inactive, terminated
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    payrolls = db.relationship('Payroll', backref='employee', lazy=True, cascade='all, delete-orphan')
    payroll_items = db.relationship('PayrollItem', backref='employee', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        """Constructor con validaciones"""
        # Generar código de empleado
        self.employee_code = self._generate_employee_code()
        
        # Asignar otros campos
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def _generate_employee_code(self) -> str:
        """Generar código de empleado único"""
        # Formato: EMP + Año + Secuencial (ej: EMP2025001)
        now = datetime.utcnow()
        prefix = f"EMP{now.year}"
        
        # Buscar último número de la serie
        last_employee = Employee.query.filter(
            Employee.employee_code.like(f"{prefix}%")
        ).order_by(Employee.employee_code.desc()).first()
        
        if last_employee:
            last_number = int(last_employee.employee_code[-3:])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}{new_number:03d}"
    
    @property
    def full_name(self) -> str:
        """Nombre completo del empleado"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_currently_active(self) -> bool:
        """Verificar si el empleado está activo actualmente"""
        if not self.is_active or self.status != 'active':
            return False
        
        if self.termination_date and self.termination_date <= date.today():
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'employee_code': self.employee_code,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'document_type': self.document_type,
            'document_number': self.document_number,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'position': self.position,
            'department': self.department,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'termination_date': self.termination_date.isoformat() if self.termination_date else None,
            'base_salary': float(self.base_salary),
            'salary_type': self.salary_type,
            'work_hours_per_day': float(self.work_hours_per_day),
            'work_days_per_week': self.work_days_per_week,
            'is_active': self.is_active,
            'status': self.status,
            'is_currently_active': self.is_currently_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self) -> str:
        return f'<Employee {self.employee_code}: {self.full_name}>'

class PayrollPeriod(db.Model):
    """Modelo de período de nómina"""
    
    __tablename__ = 'payroll_periods'
    
    # Campos principales
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    period_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Información del período
    year = db.Column(db.Integer, nullable=False, index=True)
    month = db.Column(db.Integer, nullable=False, index=True)
    period_type = db.Column(db.String(20), default='monthly')  # monthly, biweekly, weekly
    
    # Fechas del período
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    
    # Estado
    status = db.Column(db.String(20), default='draft')  # draft, processing, completed, cancelled
    is_locked = db.Column(db.Boolean, default=False)
    
    # Totales
    total_employees = db.Column(db.Integer, default=0)
    total_gross_salary = db.Column(db.Numeric(15, 2), default=0.0)
    total_deductions = db.Column(db.Numeric(15, 2), default=0.0)
    total_net_salary = db.Column(db.Numeric(15, 2), default=0.0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)
    
    # Relaciones
    payrolls = db.relationship('Payroll', backref='period', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, year: int, month: int, **kwargs):
        """Constructor con validaciones"""
        self.year = year
        self.month = month
        self.period_code = self._generate_period_code()
        
        # Calcular fechas del período
        self._calculate_period_dates()
        
        # Asignar otros campos
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def _generate_period_code(self) -> str:
        """Generar código de período único"""
        return f"PER{self.year}{self.month:02d}"
    
    def _calculate_period_dates(self):
        """Calcular fechas del período"""
        # Fecha de inicio del mes
        self.start_date = date(self.year, self.month, 1)
        
        # Fecha de fin del mes
        if self.month == 12:
            self.end_date = date(self.year + 1, 1, 1) - date.resolution
        else:
            self.end_date = date(self.year, self.month + 1, 1) - date.resolution
        
        # Fecha de pago (último día del mes siguiente)
        if self.month == 12:
            self.payment_date = date(self.year + 1, 1, 31)
        else:
            self.payment_date = date(self.year, self.month + 1, 1) - date.resolution
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'period_code': self.period_code,
            'year': self.year,
            'month': self.month,
            'period_type': self.period_type,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'status': self.status,
            'is_locked': self.is_locked,
            'total_employees': self.total_employees,
            'total_gross_salary': float(self.total_gross_salary),
            'total_deductions': float(self.total_deductions),
            'total_net_salary': float(self.total_net_salary),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }
    
    def __repr__(self) -> str:
        return f'<PayrollPeriod {self.period_code}>'

class Payroll(db.Model):
    """Modelo de nómina individual"""
    
    __tablename__ = 'payrolls'
    
    # Campos principales
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    payroll_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Referencias
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    period_id = db.Column(db.Integer, db.ForeignKey('payroll_periods.id'), nullable=False)
    
    # Información laboral del período
    days_worked = db.Column(db.Numeric(5, 2), nullable=False)
    hours_worked = db.Column(db.Numeric(6, 2), nullable=False)
    overtime_hours = db.Column(db.Numeric(6, 2), default=0.0)
    
    # Salarios
    base_salary = db.Column(db.Numeric(15, 2), nullable=False)
    overtime_pay = db.Column(db.Numeric(15, 2), default=0.0)
    bonuses = db.Column(db.Numeric(15, 2), default=0.0)
    commissions = db.Column(db.Numeric(15, 2), default=0.0)
    gross_salary = db.Column(db.Numeric(15, 2), nullable=False)
    
    # Deducciones
    health_deduction = db.Column(db.Numeric(15, 2), default=0.0)
    pension_deduction = db.Column(db.Numeric(15, 2), default=0.0)
    income_tax = db.Column(db.Numeric(15, 2), default=0.0)
    other_deductions = db.Column(db.Numeric(15, 2), default=0.0)
    total_deductions = db.Column(db.Numeric(15, 2), default=0.0)
    
    # Neto a pagar
    net_salary = db.Column(db.Numeric(15, 2), nullable=False)
    
    # Estado
    status = db.Column(db.String(20), default='draft')  # draft, calculated, approved, paid, cancelled
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    calculated_at = db.Column(db.DateTime, nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    paid_at = db.Column(db.DateTime, nullable=True)
    
    # Relaciones
    items = db.relationship('PayrollItem', backref='payroll', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, employee_id: int, period_id: int, **kwargs):
        """Constructor con validaciones"""
        self.employee_id = employee_id
        self.period_id = period_id
        self.payroll_number = self._generate_payroll_number()
        
        # Asignar otros campos
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def _generate_payroll_number(self) -> str:
        """Generar número de nómina único"""
        # Formato: NOM + Año + Mes + Secuencial (ej: NOM2025010001)
        now = datetime.utcnow()
        prefix = f"NOM{now.year}{now.month:02d}"
        
        # Buscar último número de la serie
        last_payroll = Payroll.query.filter(
            Payroll.payroll_number.like(f"{prefix}%")
        ).order_by(Payroll.payroll_number.desc()).first()
        
        if last_payroll:
            last_number = int(last_payroll.payroll_number[-4:])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}{new_number:04d}"
    
    def calculate_payroll(self, payroll_config: 'PayrollConfig') -> None:
        """Calcular nómina automáticamente"""
        # Calcular salario base proporcional
        period = PayrollPeriod.query.get(self.period_id)
        if not period:
            raise ValueError("Período de nómina no encontrado")
        
        # Calcular días del mes
        days_in_month = (period.end_date - period.start_date).days + 1
        self.days_worked = min(self.days_worked, days_in_month)
        
        # Salario base proporcional
        daily_salary = self.base_salary / days_in_month
        self.base_salary = daily_salary * self.days_worked
        
        # Horas extras
        if self.overtime_hours > 0:
            hourly_rate = daily_salary / self.employee.work_hours_per_day
            self.overtime_pay = self.overtime_hours * hourly_rate * payroll_config.overtime_multiplier
        
        # Salario bruto
        self.gross_salary = self.base_salary + self.overtime_pay + self.bonuses + self.commissions
        
        # Calcular deducciones
        self._calculate_deductions(payroll_config)
        
        # Salario neto
        self.net_salary = self.gross_salary - self.total_deductions
        
        # Actualizar estado
        self.status = 'calculated'
        self.calculated_at = datetime.utcnow()
    
    def _calculate_deductions(self, payroll_config: 'PayrollConfig') -> None:
        """Calcular deducciones según configuración"""
        # Salud (4% del salario base)
        self.health_deduction = self.base_salary * payroll_config.health_percentage / 100
        
        # Pensión (4% del salario base)
        self.pension_deduction = self.base_salary * payroll_config.pension_percentage / 100
        
        # Retención en la fuente (según tabla de retenciones)
        self.income_tax = self._calculate_income_tax(payroll_config)
        
        # Total deducciones
        self.total_deductions = (
            self.health_deduction + 
            self.pension_deduction + 
            self.income_tax + 
            self.other_deductions
        )
    
    def _calculate_income_tax(self, payroll_config: 'PayrollConfig') -> Decimal:
        """Calcular retención en la fuente"""
        # Tabla de retenciones simplificada para Colombia
        annual_gross = self.gross_salary * 12
        
        if annual_gross <= payroll_config.tax_free_annual_amount:
            return Decimal('0.00')
        elif annual_gross <= 36000000:  # 36 UVT
            return (annual_gross - payroll_config.tax_free_annual_amount) * Decimal('0.19') / 12
        elif annual_gross <= 54000000:  # 54 UVT
            return (annual_gross - payroll_config.tax_free_annual_amount) * Decimal('0.28') / 12
        else:
            return (annual_gross - payroll_config.tax_free_annual_amount) * Decimal('0.33') / 12
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'payroll_number': self.payroll_number,
            'employee_id': self.employee_id,
            'period_id': self.period_id,
            'days_worked': float(self.days_worked),
            'hours_worked': float(self.hours_worked),
            'overtime_hours': float(self.overtime_hours),
            'base_salary': float(self.base_salary),
            'overtime_pay': float(self.overtime_pay),
            'bonuses': float(self.bonuses),
            'commissions': float(self.commissions),
            'gross_salary': float(self.gross_salary),
            'health_deduction': float(self.health_deduction),
            'pension_deduction': float(self.pension_deduction),
            'income_tax': float(self.income_tax),
            'other_deductions': float(self.other_deductions),
            'total_deductions': float(self.total_deductions),
            'net_salary': float(self.net_salary),
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'calculated_at': self.calculated_at.isoformat() if self.calculated_at else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None
        }
    
    def __repr__(self) -> str:
        return f'<Payroll {self.payroll_number}>'

class PayrollItem(db.Model):
    """Modelo de item de nómina (conceptos)"""
    
    __tablename__ = 'payroll_items'
    
    # Campos principales
    id = db.Column(db.Integer, primary_key=True)
    payroll_id = db.Column(db.Integer, db.ForeignKey('payrolls.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    
    # Información del concepto
    concept_code = db.Column(db.String(20), nullable=False)
    concept_name = db.Column(db.String(100), nullable=False)
    concept_type = db.Column(db.String(20), nullable=False)  # earning, deduction
    category = db.Column(db.String(50), nullable=False)  # salary, bonus, health, pension, tax, etc.
    
    # Valores
    base_amount = db.Column(db.Numeric(15, 2), nullable=False)
    percentage = db.Column(db.Numeric(5, 2), nullable=True)
    calculated_amount = db.Column(db.Numeric(15, 2), nullable=False)
    
    # Información adicional
    description = db.Column(db.String(200), nullable=True)
    is_mandatory = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, payroll_id: int, employee_id: int, **kwargs):
        """Constructor con validaciones"""
        self.payroll_id = payroll_id
        self.employee_id = employee_id
        
        # Asignar otros campos
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        return {
            'id': self.id,
            'payroll_id': self.payroll_id,
            'employee_id': self.employee_id,
            'concept_code': self.concept_code,
            'concept_name': self.concept_name,
            'concept_type': self.concept_type,
            'category': self.category,
            'base_amount': float(self.base_amount),
            'percentage': float(self.percentage) if self.percentage else None,
            'calculated_amount': float(self.calculated_amount),
            'description': self.description,
            'is_mandatory': self.is_mandatory,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self) -> str:
        return f'<PayrollItem {self.concept_code}: {self.concept_name}>'

class PayrollConfig(db.Model):
    """Modelo de configuración de nómina"""
    
    __tablename__ = 'payroll_configs'
    
    # Campos principales
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    config_name = db.Column(db.String(100), nullable=False)
    
    # Porcentajes de deducciones
    health_percentage = db.Column(db.Numeric(5, 2), default=4.0)
    pension_percentage = db.Column(db.Numeric(5, 2), default=4.0)
    
    # Configuración de horas extras
    overtime_multiplier = db.Column(db.Numeric(3, 2), default=1.5)
    night_overtime_multiplier = db.Column(db.Numeric(3, 2), default=1.75)
    holiday_multiplier = db.Column(db.Numeric(3, 2), default=2.0)
    
    # Configuración de retenciones
    tax_free_annual_amount = db.Column(db.Numeric(15, 2), default=12000000)  # 12 UVT 2025
    
    # Configuración de salarios
    minimum_wage = db.Column(db.Numeric(15, 2), default=1300000)  # Salario mínimo 2025
    transportation_allowance = db.Column(db.Numeric(15, 2), default=162000)  # Auxilio transporte 2025
    
    # Estado
    is_active = db.Column(db.Boolean, default=True)
    is_default = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, config_name: str, **kwargs):
        """Constructor con validaciones"""
        self.config_name = config_name
        
        # Asignar otros campos
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'config_name': self.config_name,
            'health_percentage': float(self.health_percentage),
            'pension_percentage': float(self.pension_percentage),
            'overtime_multiplier': float(self.overtime_multiplier),
            'night_overtime_multiplier': float(self.night_overtime_multiplier),
            'holiday_multiplier': float(self.holiday_multiplier),
            'tax_free_annual_amount': float(self.tax_free_annual_amount),
            'minimum_wage': float(self.minimum_wage),
            'transportation_allowance': float(self.transportation_allowance),
            'is_active': self.is_active,
            'is_default': self.is_default,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self) -> str:
        return f'<PayrollConfig {self.config_name}>'
