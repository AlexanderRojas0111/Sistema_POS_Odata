"""
Payroll API v1 - Sistema POS Sabrositas
======================================
API endpoints para gestión de nómina electrónica.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from typing import Dict, Any
import logging

from app.services.payroll_service import PayrollService
from app.exceptions import BusinessLogicError, ValidationError

logger = logging.getLogger(__name__)

# Crear blueprint
payroll_bp = Blueprint('payroll', __name__)

# Inicializar servicio
payroll_service = PayrollService()

# ==================== EMPLEADOS ====================

@payroll_bp.route('/employees', methods=['POST'])
@jwt_required()
def create_employee():
    """Crear nuevo empleado"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos requeridos'}), 400
        
        employee = payroll_service.create_employee(data)
        return jsonify({
            'message': 'Empleado creado exitosamente',
            'employee': employee.to_dict()
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except BusinessLogicError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creando empleado: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@payroll_bp.route('/employees', methods=['GET'])
@jwt_required()
def get_employees():
    """Obtener lista de empleados"""
    try:
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        department = request.args.get('department')
        
        employees = payroll_service.get_employees(active_only=active_only, department=department)
        
        return jsonify({
            'employees': [employee.to_dict() for employee in employees],
            'total': len(employees)
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo empleados: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@payroll_bp.route('/employees/<int:employee_id>', methods=['GET'])
@jwt_required()
def get_employee(employee_id):
    """Obtener empleado por ID"""
    try:
        employee = payroll_service.get_employee(employee_id)
        if not employee:
            return jsonify({'error': 'Empleado no encontrado'}), 404
        
        return jsonify({'employee': employee.to_dict()}), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo empleado: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@payroll_bp.route('/employees/<int:employee_id>', methods=['PUT'])
@jwt_required()
def update_employee(employee_id):
    """Actualizar empleado"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos requeridos'}), 400
        
        employee = payroll_service.update_employee(employee_id, data)
        return jsonify({
            'message': 'Empleado actualizado exitosamente',
            'employee': employee.to_dict()
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except BusinessLogicError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error actualizando empleado: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@payroll_bp.route('/employees/<int:employee_id>/deactivate', methods=['POST'])
@jwt_required()
def deactivate_employee(employee_id):
    """Desactivar empleado"""
    try:
        data = request.get_json() or {}
        termination_date = data.get('termination_date')
        
        employee = payroll_service.deactivate_employee(employee_id, termination_date)
        return jsonify({
            'message': 'Empleado desactivado exitosamente',
            'employee': employee.to_dict()
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except BusinessLogicError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error desactivando empleado: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== PERÍODOS DE NÓMINA ====================

@payroll_bp.route('/periods', methods=['POST'])
@jwt_required()
def create_payroll_period():
    """Crear período de nómina"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos requeridos'}), 400
        
        year = data.get('year')
        month = data.get('month')
        period_type = data.get('period_type', 'monthly')
        
        if not year or not month:
            return jsonify({'error': 'Año y mes son requeridos'}), 400
        
        period = payroll_service.create_payroll_period(year, month, period_type)
        return jsonify({
            'message': 'Período de nómina creado exitosamente',
            'period': period.to_dict()
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except BusinessLogicError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creando período: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@payroll_bp.route('/periods', methods=['GET'])
@jwt_required()
def get_payroll_periods():
    """Obtener períodos de nómina"""
    try:
        year = request.args.get('year', type=int)
        
        periods = payroll_service.get_payroll_periods(year=year)
        
        return jsonify({
            'periods': [period.to_dict() for period in periods],
            'total': len(periods)
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo períodos: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@payroll_bp.route('/periods/<int:period_id>', methods=['GET'])
@jwt_required()
def get_payroll_period(period_id):
    """Obtener período por ID"""
    try:
        period = payroll_service.get_payroll_period(period_id)
        if not period:
            return jsonify({'error': 'Período no encontrado'}), 404
        
        return jsonify({'period': period.to_dict()}), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo período: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@payroll_bp.route('/periods/<int:period_id>/lock', methods=['POST'])
@jwt_required()
def lock_payroll_period(period_id):
    """Bloquear período de nómina"""
    try:
        period = payroll_service.lock_payroll_period(period_id)
        return jsonify({
            'message': 'Período bloqueado exitosamente',
            'period': period.to_dict()
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except BusinessLogicError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error bloqueando período: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== NÓMINA ====================

@payroll_bp.route('/payrolls', methods=['POST'])
@jwt_required()
def create_payroll():
    """Crear nómina individual"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos requeridos'}), 400
        
        employee_id = data.get('employee_id')
        period_id = data.get('period_id')
        
        if not employee_id or not period_id:
            return jsonify({'error': 'ID de empleado y período son requeridos'}), 400
        
        payroll = payroll_service.create_payroll(employee_id, period_id, data)
        return jsonify({
            'message': 'Nómina creada exitosamente',
            'payroll': payroll.to_dict()
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except BusinessLogicError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creando nómina: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@payroll_bp.route('/payrolls/<int:payroll_id>/calculate', methods=['POST'])
@jwt_required()
def calculate_payroll(payroll_id):
    """Calcular nómina automáticamente"""
    try:
        payroll = payroll_service.calculate_payroll(payroll_id)
        return jsonify({
            'message': 'Nómina calculada exitosamente',
            'payroll': payroll.to_dict()
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except BusinessLogicError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error calculando nómina: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@payroll_bp.route('/payrolls/<int:payroll_id>', methods=['GET'])
@jwt_required()
def get_payroll(payroll_id):
    """Obtener nómina por ID"""
    try:
        payroll = payroll_service.get_payroll(payroll_id)
        if not payroll:
            return jsonify({'error': 'Nómina no encontrada'}), 404
        
        return jsonify({'payroll': payroll.to_dict()}), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo nómina: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@payroll_bp.route('/payrolls/period/<int:period_id>', methods=['GET'])
@jwt_required()
def get_payrolls_by_period(period_id):
    """Obtener nóminas por período"""
    try:
        payrolls = payroll_service.get_payrolls_by_period(period_id)
        
        return jsonify({
            'payrolls': [payroll.to_dict() for payroll in payrolls],
            'total': len(payrolls)
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo nóminas por período: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@payroll_bp.route('/payrolls/employee/<int:employee_id>', methods=['GET'])
@jwt_required()
def get_payrolls_by_employee(employee_id):
    """Obtener nóminas por empleado"""
    try:
        year = request.args.get('year', type=int)
        
        payrolls = payroll_service.get_payrolls_by_employee(employee_id, year=year)
        
        return jsonify({
            'payrolls': [payroll.to_dict() for payroll in payrolls],
            'total': len(payrolls)
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo nóminas por empleado: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@payroll_bp.route('/payrolls/<int:payroll_id>/approve', methods=['POST'])
@jwt_required()
def approve_payroll(payroll_id):
    """Aprobar nómina"""
    try:
        payroll = payroll_service.approve_payroll(payroll_id)
        return jsonify({
            'message': 'Nómina aprobada exitosamente',
            'payroll': payroll.to_dict()
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except BusinessLogicError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error aprobando nómina: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@payroll_bp.route('/payrolls/<int:payroll_id>/pay', methods=['POST'])
@jwt_required()
def pay_payroll(payroll_id):
    """Marcar nómina como pagada"""
    try:
        payroll = payroll_service.pay_payroll(payroll_id)
        return jsonify({
            'message': 'Nómina marcada como pagada',
            'payroll': payroll.to_dict()
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except BusinessLogicError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error pagando nómina: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== CONFIGURACIÓN ====================

@payroll_bp.route('/configs', methods=['POST'])
@jwt_required()
def create_payroll_config():
    """Crear configuración de nómina"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos requeridos'}), 400
        
        config = payroll_service.create_payroll_config(data)
        return jsonify({
            'message': 'Configuración creada exitosamente',
            'config': config.to_dict()
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except BusinessLogicError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creando configuración: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@payroll_bp.route('/configs', methods=['GET'])
@jwt_required()
def get_payroll_configs():
    """Obtener configuraciones de nómina"""
    try:
        configs = payroll_service.get_payroll_configs()
        
        return jsonify({
            'configs': [config.to_dict() for config in configs],
            'total': len(configs)
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo configuraciones: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== REPORTES ====================

@payroll_bp.route('/reports/period/<int:period_id>/summary', methods=['GET'])
@jwt_required()
def get_payroll_summary(period_id):
    """Obtener resumen de nómina por período"""
    try:
        summary = payroll_service.get_payroll_summary(period_id)
        return jsonify(summary), 200
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except BusinessLogicError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error generando resumen: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@payroll_bp.route('/reports/employee/<int:employee_id>/history', methods=['GET'])
@jwt_required()
def get_employee_payroll_history(employee_id):
    """Obtener historial de nómina de empleado"""
    try:
        year = request.args.get('year', type=int)
        
        history = payroll_service.get_employee_payroll_history(employee_id, year=year)
        return jsonify(history), 200
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except BusinessLogicError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error generando historial: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== LIQUIDADOR DE NÓMINA ====================

@payroll_bp.route('/calculator/calculate', methods=['POST'])
@jwt_required()
def calculate_payroll_batch():
    """Calcular nómina en lote para un período"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos requeridos'}), 400
        
        period_id = data.get('period_id')
        employee_ids = data.get('employee_ids', [])
        
        if not period_id:
            return jsonify({'error': 'ID de período es requerido'}), 400
        
        # Obtener período
        period = payroll_service.get_payroll_period(period_id)
        if not period:
            return jsonify({'error': 'Período no encontrado'}), 404
        
        if period.is_locked:
            return jsonify({'error': 'Período bloqueado'}), 400
        
        # Obtener empleados activos
        if employee_ids:
            employees = [payroll_service.get_employee(eid) for eid in employee_ids]
            employees = [e for e in employees if e and e.is_currently_active]
        else:
            employees = payroll_service.get_employees(active_only=True)
        
        results = []
        errors = []
        
        for employee in employees:
            try:
                # Crear nómina si no existe
                existing_payroll = payroll_service.get_payrolls_by_period(period_id)
                existing_payroll = next((p for p in existing_payroll if p.employee_id == employee.id), None)
                
                if not existing_payroll:
                    # Crear nómina básica
                    payroll_data = {
                        'days_worked': 30,  # Días del mes
                        'hours_worked': employee.work_hours_per_day * 30,
                        'overtime_hours': 0,
                        'bonuses': 0,
                        'commissions': 0,
                        'other_deductions': 0
                    }
                    
                    payroll = payroll_service.create_payroll(employee.id, period_id, payroll_data)
                else:
                    payroll = existing_payroll
                
                # Calcular nómina
                payroll = payroll_service.calculate_payroll(payroll.id)
                results.append(payroll.to_dict())
                
            except Exception as e:
                errors.append({
                    'employee_id': employee.id,
                    'employee_code': employee.employee_code,
                    'error': str(e)
                })
        
        return jsonify({
            'message': f'Nómina calculada para {len(results)} empleados',
            'results': results,
            'errors': errors,
            'total_processed': len(results),
            'total_errors': len(errors)
        }), 200
        
    except Exception as e:
        logger.error(f"Error calculando nómina en lote: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500
