### Alerta UTEC

Este documento proporciona una guía rápida del proyecto **Alerta UTEC** y muestra cómo usar los servicios incluidos en la colección de Postman adjunta. Atención: el despliegue no se realiza con `sls deploy` de forma directa — vea la sección de despliegue.

### Nota de despliegue (IMPORTANTE)

No use `sls deploy` directamente sin preparar los recursos. Use el script de orquestación `./setup_backend.sh` en la raíz del repositorio. Ese script crea tablas DynamoDB requeridas, instala dependencias, genera datos de ejemplo y finalmente ejecuta el despliegue ordenado con Serverless Framework.

Ejemplo (rápido):
### Servicios Disponibles

1) Usuarios

   El servicio `Usuarios` gestiona registro, login y la administración de usuarios y empleados.

   Endpoints disponibles:

   - Registrar Usuario
     - Método: POST
     - URL: `{{baserUrl_usuarios}}/usuario/crear`
     - Cuerpo:

      ```json
      {
        "nombre": "Yaritza Lopez",
        "correo": "yartiza.lopez@utec.edu.pe",
        "contrasena": "yaritza123"
      }
      ```

   - Login Usuario
     - Método: POST
     - URL: `{{baserUrl_usuarios}}/usuario/login`
     - Cuerpo:

      ```json
      {
        "correo": "{{correo_estudiante}}",
        "contrasena": "{{contrasena_estudiante}}"
      }
      ```

   - Obtener Mi Usuario
     - Método: GET
     - URL: `{{baserUrl_usuarios}}/usuario/mi`
     - Headers: `Authorization: Bearer <token>`

   - Modificar Usuario
     - Método: PUT
     - URL: `{{baserUrl_usuarios}}/usuario/modificar`
     - Headers: `Authorization: Bearer <token>`
     - Cuerpo ejemplo:

      ```json
      {
        "correo": "{{correo_estudiante}}",
        "nombre": "Nombre Actualizado",
        "contrasena": "{{contrasena_estudiante}}"
      }
      ```

   - Eliminar Usuario
     - Método: DELETE
     - URL: `{{baserUrl_usuarios}}/usuario/eliminar`
     - Headers: `Authorization: Bearer <token>`
     - Cuerpo ejemplo:

      ```json
      {
        "correo": "{{correo_estudiante}}"
      }
      ```

   - Obtener Usuario (por correo)
     - Método: GET
     - URL: `{{baserUrl_usuarios}}/usuario/obtener?correo=<correo>`
     - Headers: `Authorization: Bearer <token>`

   - Listar Usuarios (paginado)
     - Método: POST
     - URL: `{{baserUrl_usuarios}}/usuario/listar`
     - Headers: `Authorization: Bearer <token>`
     - Cuerpo ejemplo:

      ```json
      {
        "limit": 5,
        "last_key": "{{usuarios_last_key}}"
      }
      ```

   - Cambiar Contraseña
     - Método: POST
     - URL: `{{baserUrl_usuarios}}/usuario/cambiar-contrasena`
     - Headers: `Authorization: Bearer <token>`
     - Cuerpo ejemplo:

      ```json
      {
        "contrasena_actual": "{{contrasena_estudiante}}",
        "nueva_contrasena": "yaritza456"
      }
      ```

   - Empleados (crear/listar/modificar/eliminar)
    - Crear Empleado: `POST {{baserUrl_usuarios}}/empleados/crear`

      ```json
      {
        "nombre": "Técnico Soporte",
        "tipo_area": "ti",
        "estado": "activo",
        "contacto": {
          "telefono": "+51 900000001",
          "correo": "soporte.ti@utec.edu.pe"
        }
      }
      ```

    - Listar Empleados: `POST {{baserUrl_usuarios}}/empleados/listar` (paginado/filtrado)

      ```json
      {
        "limit": 5,
        "last_key": "{{empleados_last_key}}",
        "estado": "activo"
      }
      ```

    - Modificar Empleado: `PUT {{baserUrl_usuarios}}/empleados/modificar`

      ```json
      {
        "empleado_id": "{{empleado_id}}",
        "nombre": "Técnico Soporte",
        "tipo_area": "ti",
        "estado": "activo",
        "contacto": {
          "telefono": "+51 900000001",
          "correo": "soporte.ti@utec.edu.pe"
        }
      }
      ```

    - Eliminar Empleado: `DELETE {{baserUrl_usuarios}}/empleados/eliminar`

      ```json
      {
        "empleado_id": "{{empleado_id}}"
      }
      ```

2) Incidentes

### Alerta UTEC

**Nota de despliegue (importante)**: Este proyecto NO debe desplegarse con `sls deploy` directamente. Use el script de orquestación en la raíz `setup_backend.sh`, que crea las tablas DynamoDB, instala dependencias, popula datos de ejemplo y luego realiza el despliegue ordenado con Serverless Framework.

Este documento describe los servicios expuestos por la colección Postman incluida y muestra ejemplos de request/response para cada endpoint.

### Servicios Disponibles

1. **Usuarios**

   El servicio `Usuarios` gestiona registro, inicio de sesión y administración básica de usuarios.

   - **Registrar Usuario**
     - Método: POST
     - URL: `{{baserUrl_usuarios}}/usuario/crear`
     - Cuerpo de la solicitud:

       ```json
       {
         "nombre": "Yaritza Lopez",
         "correo": "yaritza.lopez@utec.edu.pe",
         "contrasena": "yaritza123",
         "rol": "estudiante"
       }
       ```

   - **Login Usuario**
     - Método: POST
     - URL: `{{baserUrl_usuarios}}/usuario/login`
     - Cuerpo de la solicitud:

       ```json
       {
         "correo": "yaritza.lopez@utec.edu.pe",
         "contrasena": "yaritza123"
       }
       ```

   - **Mi Usuario**
     - Método: GET
     - URL: `{{baserUrl_usuarios}}/usuario/mi`
     - Headers: `Authorization: Bearer <token>`

2. **Incidentes**

   Gestión de reportes de incidentes, evidencias y estados.

   - **Crear Incidente**
     - Método: POST
     - URL: `{{baserUrl_incidentes}}/incidente/create`
     - Headers: `Authorization: Bearer <token>`
     - Cuerpo de la solicitud:

       ```json
       {
         "titulo": "Luz quemada",
         "descripcion": "Falla en pasillo",
         "piso": 2,
         "ubicacion": "Bloque A",
         "tipo": "mantenimiento",
         "nivel_urgencia": "medio",
         "coordenadas": { "lat": -12.0, "lng": -77.0 },
         "evidencias": { "file_base64": "<base64>" }
       }
       ```

   - **Listar Incidentes (paginado)**
     - Método: POST
     - URL: `{{baserUrl_incidentes}}/incidente/list`
     - Headers: `Authorization: Bearer <token>`
     - Cuerpo (opcional):

       ```json
       { "page": 0, "size": 10 }
       ```

   - **Buscar Incidente (por ID)**
     - Método: POST
     - URL: `{{baserUrl_incidentes}}/incidente/search`
     - Headers: `Authorization: Bearer <token>`
     - Cuerpo:

       ```json
       { "incidente_id": "<uuid>" }
       ```

   - **Actualizar Incidente (usuario dueño)**
     - Método: POST
     - URL: `{{baserUrl_incidentes}}/incidente/update`
     - Headers: `Authorization: Bearer <token>`
     - Cuerpo: (misma estructura que creación + `incidente_id`)

   - **Cambiar Estado (admin)**
     - Método: POST
     - URL: `{{baserUrl_incidentes}}/incidente/change-state`
     - Headers: `Authorization: Bearer <token>` (rol `personal_administrativo` o `autoridad`)
     - Cuerpo:

       ```json
       { "incidente_id": "<uuid>", "estado": "en_progreso" }
       ```

3. **Notificaciones (HTTP + WebSocket)**

   - **Notificar incidente (HTTP -> broadcast WS)**
     - Método: POST
     - URL: `{{baserUrl_notificaciones}}/notificaciones/incidente`
     - Cuerpo de la solicitud (ejemplo):

      ```json
      {
        "incidente_id": "INC-001",
        "estado": "EN_PROCESO",
        "destinatarios": ["{{correo_estudiante}}"],
        "datos": {
          "mensaje": "Prueba de notificación"
        }
      }
      ```

   - **WebSocket $connect**
     - URL (WebSocket): `wss://<websocket-endpoint>/?token=<jwt>`
     - El parámetro `token` es obligatorio; la Lambda guarda la conexión en `TABLE_CONEXIONES`.

4. **Analítica**

   Endpoints para triggers y reportes analíticos (ETL/Airflow).

   - **Trigger ETL**
     - Método: POST
     - URL: `{{baserUrl_analitica}}/analitica/trigger-etl`

   - **Incidentes por piso / por tipo / tiempo de resolución**
     - Método: GET
     - URL: `{{baserUrl_analitica}}/analitica/incidentes-por-piso`

5. **Logs**

   - **Listar logs**
     - Método: POST
     - URL: `{{baserUrl_logs}}/logs/list`
     - Headers: `Authorization: Bearer <token>` (solo roles administrativos)
     - Cuerpo (opcional): `{ "page": 0, "size": 20 }`

### Despliegue sin servidor (Serverless)

Este proyecto usa Serverless Framework, pero debe desplegarse usando el script de orquestación `setup_backend.sh` en la raíz. El script realiza en orden:

| 9 | Análisis Predictivo y visualización (Opcional) • Integración con SageMaker para modelos predictivos y visualizaciones | ✅ (opcional, requiere integración adicional) |

Si quieres, puedo:
- generar ejemplos de payload más completos para cada endpoint;
- añadir la lista de variables de entorno por función en el `README`;
- crear un archivo `API.md` separado con ejemplos curl/Postman.

