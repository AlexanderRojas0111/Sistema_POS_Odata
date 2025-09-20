"""
Payroll Service - Sistema POS Sabrositas
=======================================
Servicio para gestión de nómina electrónica y liquidación de salarios.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, date
from decimal import Decimal
import logging

from app import db
from app.models.payroll import Employee, PayrollPeriod, Payroll, PayrollItem, PayrollConfig
from app.exceptions import BusinessLogicError, ValidationError

logger = logging.getLogger(__name__)

class PayrollService:
    """Servicio para gestión de nómina"""
    
    def __init__(self):
        self.logger = logger
    
    # ==================== EMPLEADOS ====================
    
    def create_employee(self, employee_data: Dict[str, Any]) -> Employee:
        """Crear nuevo empleado"""
        try:
            # Validar datos requeridos
            required_fields = ['first_name', 'last_name', 'document_type', 'document_number', 
                             'position', 'department', 'hire_date', 'base_salary']
            
            for field in required_fields:
                if field not in employee_data or not employee_data[field]:
                    raise ValidationError(f"Campo requerido: {field}")
            
            # Crear empleado
            employee = Employee(**employee_data)
            db.session.add(employee)
            db.session.commit()
            
            self.logger.info(f"Empleado creado: {employee.employee_code}")
            return employee
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error creando empleado: {str(e)}")
            raise BusinessLogicError(f"Error creando empleado: {str(e)}")
    
    def get_employee(self, employee_id: int) -> Optional[Employee]:
        """Obtener empleado por ID"""
        return Employee.query.get(employee_id)
    
    def get_employee_by_code(self, employee_code: str) -> Optional[Employee]:
        """Obtener empleado por código"""
        return Employee.query.filter_by(employee_code=employee_code).first()
    
    def get_employees(self, active_only: bool = True, department: str = None) -> List[Employee]:
        """Obtener lista de empleados"""
        query = Employee.query
        
        if active_only:
            query = query.filter_by(is_active=True, status='active')
        
        if department:
            query = query.filter_by(department=department)
        
        return query.order_by(Employee.last_name, Employee.first_name).all()
    
    def update_employee(self, employee_id: int, employee_data: Dict[str, Any]) -> Employee:
        """Actualizar empleado"""
        try:
            employee = self.get_employee(employee_id)
            if not employee:
                raise ValidationError("Empleado no encontrado")
            
            # Actualizar campos
            for key, value in employee_data.items():
                if hasattr(employee, key) and key not in ['id', 'uuid', 'employee_code', 'created_at']:
                    setattr(employee, key, value)
            
            employee.updated_at = datetime.utcnow()
            db.session.commit()
            
            self.logger.info(f"Empleado actualizado: {employee.employee_code}")
            return employee
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error actualizando empleado: {str(e)}")
            raise BusinessLogicError(f"Error actualizando empleado: {str(e)}")
    
    def deactivate_employee(self, employee_id: int, termination_date: date = None) -> Employee:
        """Desactivar empleado"""
        try:
            employee = self.get_employee(employee_id)
            if not employee:
                raise ValidationError("Empleado no encontrado")
            
            employee.is_active = False
            employee.status = 'terminated'
            if termination_date:
                employee.termination_date = termination_date
            else:
                employee.termination_date = date.today()
            
            employee.updated_at = datetime.utcnow()
            db.session.commit()
            
            self.logger.info(f"Empleado desactivado: {employee.employee_code}")
            return employee
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error desactivando empleado: {str(e)}")
            raise BusinessLogicError(f"Error desactivando empleado: {str(e)}")
    
    # ==================== PERÍODOS DE NÓMINA ====================
    
    def create_payroll_period(self, year: int, month: int, period_type: str = 'monthly') -> PayrollPeriod:
        """Crear período de nómina"""
        try:
            # Verificar si ya existe
            existing = PayrollPeriod.query.filter_by(year=year, month=month).first()
            if existing:
                raise ValidationError(f"Ya existe un período para {year}-{month:02d}")
            
            period = PayrollPeriod(year=year, month=month, period_type=period_type)
            db.session.add(period)
            db.session.commit()
            
            self.logger.info(f"Período de nómina creado: {period.period_code}")
            return period
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error creando período de nómina: {str(e)}")
            raise BusinessLogicError(f"Error creando período de nómina: {str(e)}")
    
    def get_payroll_period(self, period_id: int) -> Optional[PayrollPeriod]:
        """Obtener período de nómina por ID"""
        return PayrollPeriod.query.get(period_id)
    
    def get_payroll_periods(self, year: int = None) -> List[PayrollPeriod]:
        """Obtener períodos de nómina"""
        query = PayrollPeriod.query
        
        if year:
            query = query.filter_by(year=year)
        
        return query.order_by(PayrollPeriod.year.desc(), PayrollPeriod.month.desc()).all()
    
    def lock_payroll_period(self, period_id: int) -> PayrollPeriod:
        """Bloquear período de nómina"""
        try:
            period = self.get_payroll_period(period_id)
            if not period:
                raise ValidationError("Período de nómina no encontrado")
            
            period.is_locked = True
            period.status = 'processing'
            period.updated_at = datetime.utcnow()
            db.session.commit()
            
            self.logger.info(f"Período de nómina bloqueado: {period.period_code}")
            return period
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error bloqueando período: {str(e)}")
            raise BusinessLogicError(f"Error bloqueando período: {str(e)}")
    
    # ==================== NÓMINA ====================
    
    def create_payroll(self, employee_id: int, period_id: int, payroll_data: Dict[str, Any]) -> Payroll:
        """Crear nómina individual"""
        try:
            # Verificar empleado
            employee = self.get_employee(employee_id)
            if not employee:
                raise ValidationError("Empleado no encontrado")
            
            # Verificar período
            period = self.get_payroll_period(period_id)
            if not period:
                raise ValidationError("Período de nómina no encontrado")
            
            if period.is_locked:
                raise ValidationError("Período de nómina bloqueado")
            
            # Verificar si ya existe nómina para este empleado en este período
            existing = Payroll.query.filter_by(employee_id=employee_id, period_id=period_id).first()
            if existing:
                raise ValidationError("Ya existe nómina para este empleado en este período")
            
            # Crear nómina
            payroll_data.update({
                'employee_id': employee_id,
                'period_id': period_id,
                'base_salary': employee.base_salary
            })
            
            payroll = Payroll(**payroll_data)
            db.session.add(payroll)
            db.session.commit()
            
            self.logger.info(f"Nómina creada: {payroll.payroll_number}")
            return payroll
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error creando nómina: {str(e)}")
            raise BusinessLogicError(f"Error creando nómina: {str(e)}")
    
    def calculate_payroll(self, payroll_id: int) -> Payroll:
        """Calcular nómina automáticamente"""
        try:
            payroll = Payroll.query.get(payroll_id)
            if not payroll:
                raise ValidationError("Nómina no encontrada")
            
            # Obtener configuración de nómina
            config = self.get_default_payroll_config()
            if not config:
                raise ValidationError("Configuración de nómina no encontrada")
            
            # Calcular nómina
            payroll.calculate_payroll(config)
            
            # Crear items de nómina
            self._create_payroll_items(payroll, config)
            
            db.session.commit()
            
            self.logger.info(f"Nómina calculada: {payroll.payroll_number}")
            return payroll
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error calculando nómina: {str(e)}")
            raise BusinessLogicError(f"Error calculando nómina: {str(e)}")
    
    def _create_payroll_items(self, payroll: Payroll, config: PayrollConfig) -> None:
        """Crear items de nómina"""
        # Limpiar items existentes
        PayrollItem.query.filter_by(payroll_id=payroll.id).delete()
        
        # Salario base
        PayrollItem(
            payroll_id=payroll.id,
            employee_id=payroll.employee_id,
            concept_code='SAL001',
            concept_name='Salario Base',
            concept_type='earning',
            category='salary',
            base_amount=payroll.base_salary,
            calculated_amount=payroll.base_salary,
            is_mandatory=True
        )
        
        # Horas extras
        if payroll.overtime_pay > 0:
            PayrollItem(
                payroll_id=payroll.id,
                employee_id=payroll.employee_id,
                concept_code='HOR001',
                concept_name='Horas Extras',
                concept_type='earning',
                category='overtime',
                base_amount=payroll.overtime_hours,
                calculated_amount=payroll.overtime_pay,
                is_mandatory=False
            )
        
        # Bonificaciones
        if payroll.bonuses > 0:
            PayrollItem(
                payroll_id=payroll.id,
                employee_id=payroll.employee_id,
                concept_code='BON001',
                concept_name='Bonificaciones',
                concept_type='earning',
                category='bonus',
                base_amount=payroll.bonuses,
                calculated_amount=payroll.bonuses,
                is_mandatory=False
            )
        
        # Comisiones
        if payroll.commissions > 0:
            PayrollItem(
                payroll_id=payroll.id,
                employee_id=payroll.employee_id,
                concept_code='COM001',
                concept_name='Comisiones',
                concept_type='earning',
                category='commission',
                base_amount=payroll.commissions,
                calculated_amount=payroll.commissions,
                is_mandatory=False
            )
        
        # Deducción salud
        if payroll.health_deduction > 0:
            PayrollItem(
                payroll_id=payroll.id,
                employee_id=payroll.employee_id,
                concept_code='DES001',
                concept_name='Deducción Salud',
                concept_type='deduction',
                category='health',
                base_amount=payroll.base_salary,
                percentage=config.health_percentage,
                calculated_amount=payroll.health_deduction,
                is_mandatory=True
            )
        
        # Deducción pensión
        if payroll.pension_deduction > 0:
            PayrollItem(
                payroll_id=payroll.id,
                employee_id=payroll.employee_id,
                concept_code='DES002',
                concept_name='Deducción Pensión',
                concept_type='deduction',
                category='pension',
                base_amount=payroll.base_salary,
                percentage=config.pension_percentage,
                calculated_amount=payroll.pension_deduction,
                is_mandatory=True
            )
        
        # Retención en la fuente
        if payroll.income_tax > 0:
            PayrollItem(
                payroll_id=payroll.id,
                employee_id=payroll.employee_id,
                concept_code='DES003',
                concept_name='Retención en la Fuente',
                concept_type='deduction',
                category='tax',
                base_amount=payroll.gross_salary,
                calculated_amount=payroll.income_tax,
                is_mandatory=True
            )
        
        # Otras deducciones
        if payroll.other_deductions > 0:
            PayrollItem(
                payroll_id=payroll.id,
                employee_id=payroll.employee_id,
                concept_code='DES004',
                concept_name='Otras Deducciones',
                concept_type='deduction',
                category='other',
                base_amount=payroll.other_deductions,
                calculated_amount=payroll.other_deductions,
                is_mandatory=False
            )
    
    def get_payroll(self, payroll_id: int) -> Optional[Payroll]:
        """Obtener nómina por ID"""
        return Payroll.query.get(payroll_id)
    
    def get_payrolls_by_period(self, period_id: int) -> List[Payroll]:
        """Obtener nóminas por período"""
        return Payroll.query.filter_by(period_id=period_id).order_by(Payroll.employee_id).all()
    
    def get_payrolls_by_employee(self, employee_id: int, year: int = None) -> List[Payroll]:
        """Obtener nóminas por empleado"""
        query = Payroll.query.filter_by(employee_id=employee_id)
        
        if year:
            query = query.join(PayrollPeriod).filter(PayrollPeriod.year == year)
        
        return query.order_by(PayrollPeriod.year.desc(), PayrollPeriod.month.desc()).all()
    
    def approve_payroll(self, payroll_id: int) -> Payroll:
        """Aprobar nómina"""
        try:
            payroll = self.get_payroll(payroll_id)
            if not payroll:
                raise ValidationError("Nómina no encontrada")
            
            if payroll.status != 'calculated':
                raise ValidationError("La nómina debe estar calculada para ser aprobada")
            
            payroll.status = 'approved'
            payroll.approved_at = datetime.utcnow()
            payroll.updated_at = datetime.utcnow()
            db.session.commit()
            
            self.logger.info(f"Nómina aprobada: {payroll.payroll_number}")
            return payroll
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error aprobando nómina: {str(e)}")
            raise BusinessLogicError(f"Error aprobando nómina: {str(e)}")
    
    def pay_payroll(self, payroll_id: int) -> Payroll:
        """Marcar nómina como pagada"""
        try:
            payroll = self.get_payroll(payroll_id)
            if not payroll:
                raise ValidationError("Nómina no encontrada")
            
            if payroll.status != 'approved':
                raise ValidationError("La nómina debe estar aprobada para ser pagada")
            
            payroll.status = 'paid'
            payroll.paid_at = datetime.utcnow()
            payroll.updated_at = datetime.utcnow()
            db.session.commit()
            
            self.logger.info(f"Nómina pagada: {payroll.payroll_number}")
            return payroll
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error pagando nómina: {str(e)}")
            raise BusinessLogicError(f"Error pagando nómina: {str(e)}")
    
    # ==================== CONFIGURACIÓN ====================
    
    def create_payroll_config(self, config_data: Dict[str, Any]) -> PayrollConfig:
        """Crear configuración de nómina"""
        try:
            config = PayrollConfig(**config_data)
            db.session.add(config)
            db.session.commit()
            
            self.logger.info(f"Configuración de nómina creada: {config.config_name}")
            return config
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error creando configuración: {str(e)}")
            raise BusinessLogicError(f"Error creando configuración: {str(e)}")
    
    def get_default_payroll_config(self) -> Optional[PayrollConfig]:
        """Obtener configuración por defecto"""
        return PayrollConfig.query.filter_by(is_default=True, is_active=True).first()
    
    def get_payroll_configs(self) -> List[PayrollConfig]:
        """Obtener todas las configuraciones"""
        return PayrollConfig.query.filter_by(is_active=True).all()
    
    # ==================== REPORTES ====================
    
    def get_payroll_summary(self, period_id: int) -> Dict[str, Any]:
        """Obtener resumen de nómina por período"""
        try:
            period = self.get_payroll_period(period_id)
            if not period:
                raise ValidationError("Período de nómina no encontrado")
            
            payrolls = self.get_payrolls_by_period(period_id)
            
            summary = {
                'period': period.to_dict(),
                'total_employees': len(payrolls),
                'total_gross_salary': sum(float(p.gross_salary) for p in payrolls),
                'total_deductions': sum(float(p.total_deductions) for p in payrolls),
                'total_net_salary': sum(float(p.net_salary) for p in payrolls),
                'payrolls': [p.to_dict() for p in payrolls]
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generando resumen: {str(e)}")
            raise BusinessLogicError(f"Error generando resumen: {str(e)}")
    
    def get_employee_payroll_history(self, employee_id: int, year: int = None) -> Dict[str, Any]:
        """Obtener historial de nómina de empleado"""
        try:
            employee = self.get_employee(employee_id)
            if not employee:
                raise ValidationError("Empleado no encontrado")
            
            payrolls = self.get_payrolls_by_employee(employee_id, year)
            
            history = {
                'employee': employee.to_dict(),
                'total_payrolls': len(payrolls),
                'total_gross_salary': sum(float(p.gross_salary) for p in payrolls),
                'total_deductions': sum(float(p.total_deductions) for p in payrolls),
                'total_net_salary': sum(float(p.net_salary) for p in payrolls),
                'payrolls': [p.to_dict() for p in payrolls]
            }
            
            return history
            
        except Exception as e:
            self.logger.error(f"Error generando historial: {str(e)}")
            raise BusinessLogicError(f"Error generando historial: {str(e)}")
