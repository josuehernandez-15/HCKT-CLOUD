#!/bin/bash

set -e  # Salir si hay algún error

echo "============================================================"
echo "🚀 ALERTA UTEC - SETUP BACKEND"
echo "============================================================"

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar que existe el archivo .env
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  Archivo .env no encontrado${NC}"
    echo "Por favor, copia .env.example a .env y configura tus variables"
    exit 1
fi

# Cargar variables de entorno
export $(cat .env | grep -v '^#' | xargs)

echo -e "\n${BLUE}🏗️  Paso 1: Creando recursos de infraestructura (Tablas DynamoDB y Bucket S3)...${NC}"
cd DataGenerator
python3 DataPoblator.py
cd ..

echo -e "\n${GREEN}✅ Setup de infraestructura completado${NC}"

echo -e "\n${BLUE}🚀 Paso 2: Desplegando microservicios con Serverless Compose...${NC}"
sls deploy

echo -e "\n${GREEN}============================================================${NC}"
echo -e "${GREEN}🎉 DESPLIEGUE COMPLETADO EXITOSAMENTE${NC}"
echo -e "${GREEN}============================================================${NC}"

echo -e "\n${BLUE}📋 Endpoints desplegados:${NC}"
sls info --verbose

echo -e "\n${YELLOW}💡 Tip: Usa 'sls logs -f <function-name> -t' para ver logs en tiempo real${NC}"
