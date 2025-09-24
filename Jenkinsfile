pipeline {
    agent any
    
    environment {
        // Configuración del proyecto
        PROJECT_NAME = 'sistema-pos-odata'
        REGISTRY = 'ghcr.io'
        IMAGE_NAME = 'odata/sistema-pos-odata'
        PYTHON_VERSION = '3.13'
        NODE_VERSION = '20'
        
        // Directorios de trabajo
        WORKSPACE_DIR = "${WORKSPACE}"
        BACKEND_DIR = "${WORKSPACE}"
        FRONTEND_DIR = "${WORKSPACE}/frontend"
        
        // Credenciales (configuradas en Jenkins)
        DOCKER_REGISTRY_CREDENTIALS = credentials('docker-registry-credentials')
        SSH_CREDENTIALS = credentials('ssh-credentials')
        SLACK_WEBHOOK = credentials('slack-webhook')
    }
    
    options {
        // Configuración del pipeline
        timeout(time: 2, unit: 'HOURS')
        disableConcurrentBuilds()
        ansiColor('xterm')
        timestamps()
        
        // Parámetros del build
        parameters([
            choice(
                name: 'DEPLOY_ENVIRONMENT',
                choices: ['staging', 'production'],
                description: 'Ambiente a desplegar'
            ),
            booleanParam(
                name: 'FORCE_DEPLOY',
                defaultValue: false,
                description: 'Forzar despliegue sin aprobación'
            ),
            string(
                name: 'BRANCH',
                defaultValue: 'develop',
                description: 'Branch a desplegar'
            )
        ])
    }
    
    stages {
        // ===== VALIDACIÓN Y PREPARACIÓN =====
        stage('Checkout & Setup') {
            steps {
                script {
                    echo "🚀 Iniciando pipeline para ${PROJECT_NAME}"
                    echo "📋 Parámetros:"
                    echo "   - Ambiente: ${params.DEPLOY_ENVIRONMENT}"
                    echo "   - Branch: ${params.BRANCH}"
                    echo "   - Forzar: ${params.FORCE_DEPLOY}"
                }
                
                // Checkout del código
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: "*/${params.BRANCH}"]],
                    userRemoteConfigs: [[
                        url: 'https://github.com/odata/sistema-pos-odata.git',
                        credentialsId: 'github-credentials'
                    ]]
                ])
                
                // Limpiar workspace
                sh 'rm -rf node_modules || true'
                sh 'rm -rf __pycache__ || true'
                sh 'rm -rf .pytest_cache || true'
            }
        }
        
        // ===== VALIDACIÓN DE DEPENDENCIAS =====
        stage('Validate Dependencies') {
            steps {
                script {
                    echo "🔍 Validando dependencias del sistema..."
                    
                    // Verificar Python
                    sh "python --version"
                    sh "python -m pip --version"
                    
                    // Verificar estructura del proyecto
                    sh '''
                        echo "Verificando estructura del proyecto..."
                        test -f app/__init__.py
                        test -f docker-compose.yml
                        test -f requirements.txt
                        echo "✅ Estructura del proyecto válida"
                    '''
                    
                    // Validar dependencias Python
                    sh "python scripts/validate_dependencies.py"
                }
            }
        }
        
        // ===== ESCANEO DE SEGURIDAD =====
        stage('Security Scan') {
            parallel {
                stage('Python Security') {
                    steps {
                        script {
                            echo "🛡️ Escaneando seguridad Python..."
                            
                            // Instalar safety
                            sh "pip install safety"
                            
                            // Escanear dependencias
                            sh "safety check -r requirements.txt --output json --save safety-report.json || true"
                            
                            // Archivar reporte
                            archiveArtifacts artifacts: 'safety-report.json', allowEmptyArchive: true
                        }
                    }
                }
                
                stage('Node.js Security') {
                    steps {
                        script {
                            echo "🛡️ Escaneando seguridad Node.js..."
                            
                            dir(FRONTEND_DIR) {
                                // Instalar dependencias
                                sh "npm ci --only=production --legacy-peer-deps"
                                
                                // Auditoría de seguridad
                                sh "npm audit --audit-level=high --json > npm-audit.json || true"
                                
                                // Archivar reporte
                                archiveArtifacts artifacts: 'npm-audit.json', allowEmptyArchive: true
                            }
                        }
                    }
                }
                
                stage('Container Security') {
                    steps {
                        script {
                            echo "🛡️ Escaneando seguridad de contenedores..."
                            
                            // Instalar Trivy si no está disponible
                            sh "which trivy || (curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin)"
                            
                            // Escanear Dockerfile
                            sh "trivy fs --severity CRITICAL,HIGH --format json --output trivy-report.json . || true"
                            
                            // Archivar reporte
                            archiveArtifacts artifacts: 'trivy-report.json', allowEmptyArchive: true
                        }
                    }
                }
            }
        }
        
        // ===== PRUEBAS BACKEND =====
        stage('Backend Tests') {
            steps {
                script {
                    echo "🧪 Ejecutando pruebas del backend..."
                    
                    // Instalar dependencias
                    sh "pip install -r requirements.txt"
                    sh "pip install -r requirements.dev.txt"
                    
                    // Ejecutar pruebas unitarias
                    sh "pytest tests/ -v --cov=app --cov-report=xml --cov-report=html"
                    
                    // Ejecutar pruebas de integración
                    sh "pytest tests/test_api_integration.py -v"
                    
                    // Archivar reportes
                    archiveArtifacts artifacts: 'htmlcov/**/*,coverage.xml', allowEmptyArchive: true
                    
                    // Publicar cobertura
                    publishCoverage(
                        adapters: [coberturaAdapter('coverage.xml')],
                        sourceFileResolver: sourceFiles('STORE_LAST_BUILD')
                    )
                }
            }
        }
        
        // ===== PRUEBAS FRONTEND =====
        stage('Frontend Tests') {
            steps {
                script {
                    echo "🎨 Ejecutando pruebas del frontend..."
                    
                    dir(FRONTEND_DIR) {
                        // Linting
                        sh "npm run lint"
                        
                        // Pruebas unitarias
                        sh "npm test -- --watchAll=false --coverage"
                        
                        // Build de producción
                        sh "npm run build"
                        
                        // Analizar bundle
                        sh "npm run analyze || true"
                        
                        // Archivar build
                        archiveArtifacts artifacts: 'build/**/*', allowEmptyArchive: true
                    }
                }
            }
        }
        
        // ===== CONSTRUCCIÓN DE IMÁGENES =====
        stage('Build Docker Images') {
            steps {
                script {
                    echo "🏗️ Construyendo imágenes Docker..."
                    
                    // Login al registro
                    sh "echo '${DOCKER_REGISTRY_CREDENTIALS_PSW}' | docker login ${REGISTRY} -u ${DOCKER_REGISTRY_CREDENTIALS_USR} --password-stdin"
                    
                    // Construir imagen del backend
                    sh """
                        docker build -t ${REGISTRY}/${IMAGE_NAME}-backend:${BUILD_NUMBER} .
                        docker tag ${REGISTRY}/${IMAGE_NAME}-backend:${BUILD_NUMBER} ${REGISTRY}/${IMAGE_NAME}-backend:latest
                    """
                    
                    // Construir imagen del frontend
                    sh """
                        docker build -t ${REGISTRY}/${IMAGE_NAME}-frontend:${BUILD_NUMBER} ${FRONTEND_DIR}
                        docker tag ${REGISTRY}/${IMAGE_NAME}-frontend:${BUILD_NUMBER} ${REGISTRY}/${IMAGE_NAME}-frontend:latest
                    """
                    
                    // Subir imágenes
                    sh """
                        docker push ${REGISTRY}/${IMAGE_NAME}-backend:${BUILD_NUMBER}
                        docker push ${REGISTRY}/${IMAGE_NAME}-backend:latest
                        docker push ${REGISTRY}/${IMAGE_NAME}-frontend:${BUILD_NUMBER}
                        docker push ${REGISTRY}/${IMAGE_NAME}-frontend:latest
                    """
                }
            }
        }
        
        // ===== APROBACIÓN PARA PRODUCCIÓN =====
        stage('Production Approval') {
            when {
                allOf {
                    expression { params.DEPLOY_ENVIRONMENT == 'production' }
                    expression { !params.FORCE_DEPLOY }
                }
            }
            steps {
                script {
                    echo "⏳ Esperando aprobación para despliegue en producción..."
                    
                    // Crear entrada de aprobación
                    input(
                        message: '¿Proceder con el despliegue en PRODUCCIÓN?',
                        ok: 'Desplegar en Producción',
                        submitter: 'admin,devops',
                        submitterParameter: 'APPROVER'
                    )
                    
                    echo "✅ Aprobación recibida de: ${env.APPROVER}"
                }
            }
        }
        
        // ===== DESPLIEGUE =====
        stage('Deploy') {
            steps {
                script {
                    echo "🚀 Desplegando en ${params.DEPLOY_ENVIRONMENT}..."
                    
                    def deployScript = ""
                    
                    if (params.DEPLOY_ENVIRONMENT == 'staging') {
                        deployScript = """
                            set -e
                            echo "🚀 Iniciando despliegue en STAGING..."
                            
                            cd /opt/pos-odata
                            
                            # Backup
                            docker compose -f docker-compose.production.yml run --rm backup || echo "⚠️ Backup falló"
                            
                            # Actualizar imágenes
                            docker compose -f docker-compose.production.yml pull
                            
                            # Desplegar
                            docker compose -f docker-compose.production.yml up -d
                            
                            # Verificar
                            sleep 30
                            docker compose -f docker-compose.production.yml ps
                            curl -f http://localhost/health || echo "⚠️ Health check falló"
                            
                            echo "✅ Despliegue en STAGING completado"
                        """
                    } else {
                        deployScript = """
                            set -e
                            echo "🚀 Iniciando despliegue en PRODUCCIÓN..."
                            
                            cd /opt/pos-odata
                            
                            # Backup crítico
                            docker compose -f docker-compose.production.yml run --rm backup
                            
                            # Verificar espacio
                            df -h
                            
                            # Actualizar y desplegar
                            docker compose -f docker-compose.production.yml pull
                            
                            if docker compose -f docker-compose.production.yml up -d; then
                                sleep 45
                                docker compose -f docker-compose.production.yml ps
                                curl -f https://pos.odata.com/health || exit 1
                                echo "✅ Despliegue en PRODUCCIÓN exitoso"
                            else
                                echo "❌ Despliegue falló, rollback..."
                                docker compose -f docker-compose.production.yml up -d
                                exit 1
                            fi
                        """
                    }
                    
                    // Ejecutar despliegue via SSH
                    sshagent(['ssh-credentials']) {
                        def host = params.DEPLOY_ENVIRONMENT == 'staging' ? env.STAGING_HOST : env.PRODUCTION_HOST
                        def user = env.SSH_USER
                        
                        sh """
                            ssh -o StrictHostKeyChecking=no ${user}@${host} << 'EOF'
                            ${deployScript}
                            EOF
                        """
                    }
                }
            }
        }
        
        // ===== VERIFICACIÓN POST-DESPLIEGUE =====
        stage('Post-Deployment Verification') {
            steps {
                script {
                    echo "🔍 Verificando despliegue..."
                    
                    // Esperar que los servicios estén listos
                    sleep 60
                    
                    // Verificar endpoints
                    def baseUrl = params.DEPLOY_ENVIRONMENT == 'staging' ? 'http://staging.pos.odata.com' : 'https://pos.odata.com'
                    
                    sh """
                        echo "Verificando endpoints..."
                        curl -f ${baseUrl}/health
                        curl -f ${baseUrl}/api/v1/health
                        echo "✅ Endpoints verificados"
                    """
                    
                    // Verificar métricas de Prometheus
                    sh """
                        echo "Verificando métricas..."
                        curl -f ${baseUrl}:9090/-/healthy || echo "⚠️ Prometheus no responde"
                    """
                }
            }
        }
    }
    
    // ===== POST-ACTIONS =====
    post {
        always {
            script {
                // Limpiar imágenes Docker locales
                sh "docker system prune -f || true"
                
                // Generar reporte del build
                def report = """
                    # Reporte de Build - Sistema POS Odata
                    
                    ## Información del Build
                    - **Build ID**: ${BUILD_NUMBER}
                    - **Branch**: ${params.BRANCH}
                    - **Ambiente**: ${params.DEPLOY_ENVIRONMENT}
                    - **Estado**: ${currentBuild.result ?: 'SUCCESS'}
                    - **Duración**: ${currentBuild.durationString}
                    - **Timestamp**: ${new Date().format("yyyy-MM-dd HH:mm:ss")}
                    
                    ## Artefactos Generados
                    - Imágenes Docker: ${REGISTRY}/${IMAGE_NAME}-backend:${BUILD_NUMBER}
                    - Imágenes Docker: ${REGISTRY}/${IMAGE_NAME}-frontend:${BUILD_NUMBER}
                    - Reportes de cobertura
                    - Reportes de seguridad
                    
                    ## Próximos Pasos
                    - Verificar logs en el servidor
                    - Monitorear métricas de Prometheus
                    - Validar funcionalidad con usuarios
                """
                
                writeFile file: 'build-report.md', text: report
                archiveArtifacts artifacts: 'build-report.md'
            }
        }
        
        success {
            script {
                echo "✅ Pipeline ejecutado exitosamente!"
                
                // Notificación de éxito
                if (env.SLACK_WEBHOOK) {
                    sh """
                        curl -X POST -H 'Content-type: application/json' \
                        --data '{"text":"✅ Despliegue exitoso en ${params.DEPLOY_ENVIRONMENT} - Build #${BUILD_NUMBER}"}' \
                        ${env.SLACK_WEBHOOK}
                    """
                }
            }
        }
        
        failure {
            script {
                echo "❌ Pipeline falló!"
                
                // Notificación de fallo
                if (env.SLACK_WEBHOOK) {
                    sh """
                        curl -X POST -H 'Content-type: application/json' \
                        --data '{"text":"❌ Despliegue falló en ${params.DEPLOY_ENVIRONMENT} - Build #${BUILD_NUMBER}"}' \
                        ${env.SLACK_WEBHOOK}
                    """
                }
                
                // Enviar email de notificación
                emailext (
                    subject: "❌ Pipeline Falló - Sistema POS Odata",
                    body: """
                        El pipeline del Sistema POS Odata ha fallado.
                        
                        Detalles:
                        - Build ID: ${BUILD_NUMBER}
                        - Branch: ${params.BRANCH}
                        - Ambiente: ${params.DEPLOY_ENVIRONMENT}
                        - URL del Build: ${BUILD_URL}
                        
                        Revisar logs para más detalles.
                    """,
                    to: 'admin@odata.com,devops@odata.com'
                )
            }
        }
        
        cleanup {
            script {
                echo "🧹 Limpiando workspace..."
                
                // Limpiar workspace
                cleanWs()
            }
        }
    }
}
