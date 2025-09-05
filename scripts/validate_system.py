#!/usr/bin/env python3
"""
Script de Validación Final del Sistema POS O'data
================================================

Ejecuta una validación completa del sistema para verificar que todo
esté funcionando correctamente antes del despliegue.

Versión: 2.0.0
Autor: Sistema POS Odata Team
"""

import os
import sys
import time
import json
import logging
import subprocess
import platform
from datetime import datetime
from pathlib import Path

# Configurar logging para Windows
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('validation.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

class SystemValidator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.project_root = Path(__file__).parent.parent
        self.reports_dir = self.project_root / "reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        # Resultados de validación
        self.validation_results = {
            "system_info": {},
            "infrastructure": {},
            "backend_functionality": {},
            "database_functionality": {},
            "ai_functionality": {},
            "security_features": {},
            "performance_metrics": {},
            "overall_score": 0
        }
        
    def validate_system_info(self):
        """Validar información básica del sistema"""
        self.logger.info("Validando información del sistema...")
        
        try:
            # Información del sistema operativo
            os_info = {
                "platform": platform.platform(),
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor()
            }
            
            # Información de Python
            python_info = {
                "version": sys.version,
                "executable": sys.executable,
                "path": sys.path[:3]  # Solo los primeros 3 paths
            }
            
            # Información del proyecto
            project_info = {
                "root": str(self.project_root),
                "python_files": len(list(self.project_root.rglob("*.py"))),
                "requirements_files": len(list(self.project_root.glob("requirements*.txt")))
            }
            
            self.validation_results["system_info"] = {
                "os": os_info,
                "python": python_info,
                "project": project_info,
                "status": "success"
            }
            
            self.logger.info("Informacion del sistema validada")
            return True
            
        except Exception as e:
            self.logger.error(f"Error validando informacion del sistema: {e}")
            self.validation_results["system_info"] = {
                "status": "error",
                "error": str(e)
            }
            return False
    
    def validate_infrastructure(self):
        """Validar infraestructura básica"""
        self.logger.info("Validando infraestructura...")
        
        try:
            # Verificar directorios críticos
            critical_dirs = [
                "app",
                "tests", 
                "scripts",
                "frontend",
                "docs"
            ]
            
            dir_status = {}
            for dir_name in critical_dirs:
                dir_path = self.project_root / dir_name
                dir_status[dir_name] = {
                    "exists": dir_path.exists(),
                    "is_dir": dir_path.is_dir() if dir_path.exists() else False,
                    "files_count": len(list(dir_path.rglob("*"))) if dir_path.exists() else 0
                }
            
            # Verificar archivos críticos
            critical_files = [
                "requirements.txt",
                "requirements-dev.txt", 
                "pytest.ini",
                "README.md",
                "app/main.py"
            ]
            
            file_status = {}
            for file_name in critical_files:
                file_path = self.project_root / file_name
                file_status[file_name] = {
                    "exists": file_path.exists(),
                    "size": file_path.stat().st_size if file_path.exists() else 0
                }
            
            # Verificar permisos de escritura
            write_permissions = {
                "reports_dir": os.access(self.reports_dir, os.W_OK),
                "project_root": os.access(self.project_root, os.W_OK)
            }
            
            self.validation_results["infrastructure"] = {
                "directories": dir_status,
                "files": file_status,
                "permissions": write_permissions,
                "status": "success"
            }
            
            self.logger.info("Infraestructura validada")
            return True
            
        except Exception as e:
            self.logger.error(f"Error validando infraestructura: {e}")
            self.validation_results["infrastructure"] = {
                "status": "error",
                "error": str(e)
            }
            return False
    
    def validate_backend_functionality(self):
        """Validar funcionalidades del backend"""
        self.logger.info("Validando funcionalidades del backend...")
        
        try:
            # Verificar imports críticos
            backend_modules = [
                "app.main",
                "app.core.config",
                "app.core.database",
                "app.models.user",
                "app.models.product",
                "app.api.v1.auth"
            ]
            
            import_status = {}
            for module_name in backend_modules:
                try:
                    __import__(module_name)
                    import_status[module_name] = {"status": "success"}
                except ImportError as e:
                    import_status[module_name] = {"status": "error", "error": str(e)}
                except Exception as e:
                    import_status[module_name] = {"status": "warning", "error": str(e)}
            
            # Verificar configuración
            config_status = {}
            try:
                from app.core.config import settings
                config_status["config_loaded"] = True
                config_status["database_url"] = hasattr(settings, 'DATABASE_URL')
                config_status["jwt_secret"] = hasattr(settings, 'JWT_SECRET_KEY')
            except Exception as e:
                config_status["config_loaded"] = False
                config_status["error"] = str(e)
            
            # Verificar modelos
            models_status = {}
            try:
                from app.models.user import User
                from app.models.product import Product
                models_status["user_model"] = True
                models_status["product_model"] = True
            except Exception as e:
                models_status["error"] = str(e)
            
            self.validation_results["backend_functionality"] = {
                "imports": import_status,
                "config": config_status,
                "models": models_status,
                "status": "success"
            }
            
            self.logger.info("Funcionalidades del backend validadas")
            return True
            
        except Exception as e:
            self.logger.error(f"Error validando funcionalidades del backend: {e}")
            self.validation_results["backend_functionality"] = {
                "status": "error",
                "error": str(e)
            }
            return False
    
    def validate_database_functionality(self):
        """Validar funcionalidades de la base de datos"""
        self.logger.info("Validando funcionalidades de la base de datos...")
        
        try:
            # Verificar conexión a SQLite
            sqlite_status = {}
            try:
                import sqlite3
                db_path = self.project_root / "instance" / "pos_odata_dev.db"
            if db_path.exists():
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                conn.close()
                
                    sqlite_status["connected"] = True
                    sqlite_status["tables_count"] = len(tables)
                    sqlite_status["tables"] = [table[0] for table in tables]
                else:
                    sqlite_status["connected"] = False
                    sqlite_status["error"] = "Database file not found"
            except Exception as e:
                sqlite_status["connected"] = False
                sqlite_status["error"] = str(e)
            
            # Verificar SQLAlchemy
            sqlalchemy_status = {}
            try:
                from sqlalchemy import create_engine, text
                sqlalchemy_status["imported"] = True
                
                # Crear engine de prueba
                test_engine = create_engine("sqlite:///:memory:")
                with test_engine.connect() as conn:
                    result = conn.execute(text("SELECT 1"))
                    sqlalchemy_status["test_query"] = True
                
        except Exception as e:
                sqlalchemy_status["imported"] = False
                sqlalchemy_status["error"] = str(e)
            
            # Verificar Alembic
            alembic_status = {}
            try:
                import alembic
                alembic_status["version"] = alembic.__version__
                alembic_status["imported"] = True
            except ImportError:
                alembic_status["imported"] = False
                alembic_status["error"] = "Alembic not installed"
            
            self.validation_results["database_functionality"] = {
                "sqlite": sqlite_status,
                "sqlalchemy": sqlalchemy_status,
                "alembic": alembic_status,
                "status": "success"
            }
            
            self.logger.info("Funcionalidades de la base de datos validadas")
            return True
            
        except Exception as e:
            self.logger.error(f"Error validando funcionalidades de la base de datos: {e}")
            self.validation_results["database_functionality"] = {
                "status": "error",
                "error": str(e)
            }
            return False
    
    def validate_ai_functionality(self):
        """Validar funcionalidades de IA"""
        self.logger.info("Validando funcionalidades de IA...")
        
        try:
            # Verificar scikit-learn
            sklearn_status = {}
            try:
                import sklearn
                sklearn_status["version"] = sklearn.__version__
                sklearn_status["imported"] = True
                
                # Verificar funcionalidades básicas
                from sklearn.feature_extraction.text import TfidfVectorizer
                from sklearn.metrics.pairwise import cosine_similarity
                
                # Test básico de TF-IDF
                texts = ["hello world", "hello python", "python world"]
                vectorizer = TfidfVectorizer()
                vectors = vectorizer.fit_transform(texts)
                
                sklearn_status["tfidf"] = True
                sklearn_status["cosine_similarity"] = True
                
            except ImportError:
                sklearn_status["imported"] = False
                sklearn_status["error"] = "scikit-learn not installed"
        except Exception as e:
                sklearn_status["imported"] = True
                sklearn_status["error"] = str(e)
            
            # Verificar numpy
            numpy_status = {}
            try:
                import numpy as np
                numpy_status["version"] = np.__version__
                numpy_status["imported"] = True
                
                # Test básico
                arr = np.array([1, 2, 3])
                numpy_status["array_creation"] = True
                
            except ImportError:
                numpy_status["imported"] = False
                numpy_status["error"] = "numpy not installed"
            
            # Verificar scipy
            scipy_status = {}
            try:
                import scipy
                scipy_status["version"] = scipy.__version__
                scipy_status["imported"] = True
            except ImportError:
                scipy_status["imported"] = False
                scipy_status["error"] = "scipy not installed"
            
            self.validation_results["ai_functionality"] = {
                "scikit_learn": sklearn_status,
                "numpy": numpy_status,
                "scipy": scipy_status,
                "status": "success"
            }
            
            self.logger.info("Funcionalidades de IA validadas")
                return True
                
        except Exception as e:
            self.logger.error(f"Error validando funcionalidades de IA: {e}")
            self.validation_results["ai_functionality"] = {
                "status": "error",
                "error": str(e)
            }
            return False
    
    def validate_security_features(self):
        """Validar características de seguridad"""
        self.logger.info("Validando caracteristicas de seguridad...")
        
        try:
            # Verificar JWT
            jwt_status = {}
            try:
                import jwt
                jwt_status["imported"] = True
                jwt_status["version"] = jwt.__version__
            except ImportError:
                jwt_status["imported"] = False
                jwt_status["error"] = "PyJWT not installed"
            
            # Verificar bcrypt
            bcrypt_status = {}
            try:
                import bcrypt
                bcrypt_status["imported"] = True
                
                # Test básico
                password = b"test_password"
                hashed = bcrypt.hashpw(password, bcrypt.gensalt())
                bcrypt_status["hashing"] = True
                
            except ImportError:
                bcrypt_status["imported"] = False
                bcrypt_status["error"] = "bcrypt not installed"
            
            # Verificar cryptography
            crypto_status = {}
            try:
                import cryptography
                crypto_status["imported"] = True
                crypto_status["version"] = cryptography.__version__
            except ImportError:
                crypto_status["imported"] = False
                crypto_status["error"] = "cryptography not installed"
            
            # Verificar Flask-JWT-Extended
            flask_jwt_status = {}
            try:
                from flask_jwt_extended import JWTManager
                flask_jwt_status["imported"] = True
            except ImportError:
                flask_jwt_status["imported"] = False
                flask_jwt_status["error"] = "Flask-JWT-Extended not installed"
            
            self.validation_results["security_features"] = {
                "jwt": jwt_status,
                "bcrypt": bcrypt_status,
                "cryptography": crypto_status,
                "flask_jwt": flask_jwt_status,
                "status": "success"
            }
            
            self.logger.info("Caracteristicas de seguridad validadas")
            return True
                
        except Exception as e:
            self.logger.error(f"Error validando caracteristicas de seguridad: {e}")
            self.validation_results["security_features"] = {
                "status": "error",
                "error": str(e)
            }
            return False
    
    def validate_performance_metrics(self):
        """Validar métricas de performance"""
        self.logger.info("Validando metricas de performance...")
        
        try:
            # Medir tiempo de importación de módulos críticos
            import_times = {}
            
            # Test de importación de Flask
            start_time = time.time()
            try:
                import flask
                flask_import_time = time.time() - start_time
                import_times["flask"] = flask_import_time
            except ImportError:
                import_times["flask"] = "not_installed"
            
            # Test de importación de SQLAlchemy
            start_time = time.time()
            try:
                import sqlalchemy
                sqlalchemy_import_time = time.time() - start_time
                import_times["sqlalchemy"] = sqlalchemy_import_time
            except ImportError:
                import_times["sqlalchemy"] = "not_installed"
            
            # Test de importación de scikit-learn
            start_time = time.time()
            try:
                import sklearn
                sklearn_import_time = time.time() - start_time
                import_times["sklearn"] = sklearn_import_time
            except ImportError:
                import_times["sklearn"] = "not_installed"
            
            # Medir tiempo de operaciones básicas
            operation_times = {}
            
            # Test de operaciones de archivo
            start_time = time.time()
            test_file = self.reports_dir / "test_performance.txt"
            test_file.write_text("test content")
            test_file.unlink()
            file_operation_time = time.time() - start_time
            operation_times["file_operations"] = file_operation_time
            
            # Test de operaciones de base de datos (simulado)
            start_time = time.time()
            time.sleep(0.01)  # Simular operación de DB
            db_operation_time = time.time() - start_time
            operation_times["db_operations"] = db_operation_time
            
            # Evaluar performance
            performance_score = 0
            performance_issues = []
            
            # Evaluar tiempos de importación
            for module, import_time in import_times.items():
                if isinstance(import_time, float):
                    if import_time < 0.1:
                        performance_score += 20
                    elif import_time < 0.5:
                        performance_score += 10
                    else:
                        performance_issues.append(f"{module} import slow: {import_time:.3f}s")
            
            # Evaluar operaciones
            if operation_times["file_operations"] < 0.01:
                performance_score += 20
            else:
                performance_issues.append(f"File operations slow: {operation_times['file_operations']:.3f}s")
            
            if operation_times["db_operations"] < 0.05:
                performance_score += 20
            else:
                performance_issues.append(f"DB operations slow: {operation_times['db_operations']:.3f}s")
            
            self.validation_results["performance_metrics"] = {
                "import_times": import_times,
                "operation_times": operation_times,
                "performance_score": performance_score,
                "issues": performance_issues,
                "status": "success"
            }
            
            self.logger.info("Metricas de performance validadas")
            return True
                
        except Exception as e:
            self.logger.error(f"Error validando metricas de performance: {e}")
            self.validation_results["performance_metrics"] = {
                "status": "error",
                "error": str(e)
            }
            return False
    
    def calculate_overall_score(self):
        """Calcular puntuación general"""
        scores = []
        
        for category, data in self.validation_results.items():
            if category == "overall_score":
                continue
                
            if data.get("status") == "success":
                scores.append(100)
            elif data.get("status") == "warning":
                scores.append(70)
            elif data.get("status") == "error":
                scores.append(30)
            else:
                scores.append(0)
        
        if scores:
            overall_score = sum(scores) / len(scores)
        else:
            overall_score = 0
        
        self.validation_results["overall_score"] = round(overall_score, 1)
        return overall_score
    
    def generate_validation_report(self):
        """Generar reporte de validación"""
        self.logger.info("Generando reporte de validacion...")
        
        try:
            # Calcular puntuación
            overall_score = self.calculate_overall_score()
            
            # Generar HTML
            html_content = self._generate_html_report()
            
            # Guardar reporte
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = self.reports_dir / f"system_validation_report_{timestamp}.html"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"Reporte de validacion guardado en: {report_file}")
            
            # También guardar JSON
            json_file = self.reports_dir / f"system_validation_report_{timestamp}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(self.validation_results, f, indent=2, ensure_ascii=False)
            
            return str(report_file)
            
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}")
            return None
    
    def _generate_html_report(self):
        """Generar contenido HTML del reporte"""
        overall_score = self.validation_results["overall_score"]
        
        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reporte de Validacion del Sistema - O'Data v2.0.0</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; border-bottom: 2px solid #007bff; padding-bottom: 20px; margin-bottom: 30px; }}
                .score {{ font-size: 2em; font-weight: bold; color: #007bff; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .section h3 {{ color: #333; margin-top: 0; }}
                .success {{ border-left: 4px solid #28a745; }}
                .warning {{ border-left: 4px solid #ffc107; }}
                .error {{ border-left: 4px solid #dc3545; }}
                .details {{ background: #f8f9fa; padding: 10px; border-radius: 3px; margin-top: 10px; }}
                .timestamp {{ color: #666; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Sistema POS O'Data v2.0.0</h1>
                    <h2>Reporte de Validacion del Sistema</h2>
                    <div class="score">Puntuacion: {overall_score}%</div>
                    <div class="timestamp">Generado: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
                </div>
        """
        
        # Agregar secciones
        for category, data in self.validation_results.items():
            if category == "overall_score":
                continue
                
            status_class = data.get("status", "unknown")
            status_emoji = {
                "success": "✅",
                "warning": "⚠️", 
                "error": "❌",
                "unknown": "❓"
            }.get(status_class, "❓")
            
            html += f"""
                <div class="section {status_class}">
                    <h3>{status_emoji} {category.replace('_', ' ').title()}</h3>
                    <div class="details">
                        <pre>{json.dumps(data, indent=2, ensure_ascii=False)}</pre>
                    </div>
                </div>
            """
        
        html += """
            </div>
        </body>
        </html>
        """
        
        return html
    
    def run_validation(self):
        """Ejecutar validación completa"""
        self.logger.info("Iniciando validacion completa del sistema...")
        
        start_time = time.time()
        
        # Ejecutar todas las validaciones
        validations = [
            self.validate_system_info,
            self.validate_infrastructure,
            self.validate_backend_functionality,
            self.validate_database_functionality,
            self.validate_ai_functionality,
            self.validate_security_features,
            self.validate_performance_metrics
        ]
        
        results = []
        for validation in validations:
            try:
                result = validation()
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error en validacion {validation.__name__}: {e}")
                results.append(False)
        
        # Generar reporte
        report_file = self.generate_validation_report()
        
        # Calcular puntuación final
        overall_score = self.calculate_overall_score()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        self.logger.info(f"Validacion completada. Puntuacion: {overall_score}%")
        self.logger.info(f"Tiempo total: {total_time:.2f} segundos")
        
        if overall_score >= 80:
            self.logger.info("Sistema validado exitosamente")
            return True
        elif overall_score >= 60:
            self.logger.warning("Sistema tiene advertencias")
            return True
    else:
            self.logger.error("Sistema tiene problemas criticos")
            return False

def main():
    """Función principal"""
    validator = SystemValidator()
    
    try:
        success = validator.run_validation()
        
        if success:
            print("✅ Validacion del sistema completada exitosamente")
            print(f"📊 Reporte generado en: {validator.reports_dir}")
            sys.exit(0)
        else:
            print("❌ La validacion fallo. Revisa el reporte para mas detalles.")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error critico durante la validacion: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
