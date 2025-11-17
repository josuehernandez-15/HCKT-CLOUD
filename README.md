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
     - Cuerpo (opcional, soporta filtros):

       ```json
       {
         "page": 0,
         "size": 10,
         "estado": "en_progreso",    // opcional: filtra por estado
         "tipo": "mantenimiento",    // opcional: filtra por tipo
         "nivel_urgencia": "medio"   // opcional: filtra por nivel_urgencia
       }
       ```

     - Comportamiento por rol (respuesta):
       - Si el solicitante es **estudiante**, cada item en `contents` contiene campos resumidos:

         ```json
         {
           "titulo": "...",
           "piso": 2,
           "tipo": "mantenimiento",
           "nivel_urgencia": "medio",
           "estado": "en_progreso",
           "created_at": "2025-11-01T12:00:00Z",
           "updated_at": "2025-11-02T08:00:00Z"
         }
         ```

       - Si el solicitante es **autoridad** o **administrador_empleado**, recibe detalle completo por item:

         ```json
         {
           "incidente_id": "<uuid>",
           "titulo": "...",
           "descripcion": "...",
           "piso": 2,
           "ubicacion": "Bloque A",
           "tipo": "mantenimiento",
           "nivel_urgencia": "medio",
           "evidencias": [],
           "estado": "en_progreso",
           "usuario_correo": "user@utec.edu.pe",
           "created_at": "2025-11-01T12:00:00Z",
           "updated_at": "2025-11-02T08:00:00Z",
           "coordenadas": { "lat": -12.0, "lng": -77.0 }
         }
         ```

       - Respuesta paginada (ambos casos):

         ```json
         {
           "contents": [ /* items */ ],
           "page": 0,
           "size": 10,
           "totalElements": 123,
           "totalPages": 13
         }
         ```

   - **Buscar Incidente (por ID)**
     - Método: POST
     - URL: `{{baserUrl_incidentes}}/incidente/search`
     - Headers: `Authorization: Bearer <token>`
     - Cuerpo:

       ```json
       { "incidente_id": "<uuid>" }
       ```

     - Permisos: sólo pueden consultar **autoridad**, **administrador_empleado** o el **propietario** (usuario que creó el incidente). La respuesta devuelve toda la información disponible del incidente (campos completos mostrados arriba).

   - **Actualizar Incidente (usuario dueño)**
     - Método: POST
     - URL: `{{baserUrl_incidentes}}/incidente/update`
     - Headers: `Authorization: Bearer <token>`
     - Permisos: sólo el **propietario** puede actualizar su incidente.
     - Cuerpo (ejemplo):

       ```json
       {
         "incidente_id": "{{incidente_id}}",
         "titulo": "Fuga de agua actualizada",
         "descripcion": "Actualización del incidente por el estudiante.",
         "piso": 3,
         "ubicacion": { "x": -76.88, "y": -12.88 },
         "tipo": "mantenimiento",
         "nivel_urgencia": "medio"
       }
       ```

   - **Cambiar Estado (admin)**
     - Método: POST
     - URL: `{{baserUrl_incidentes}}/incidente/change-state`
     - Headers: `Authorization: Bearer <token>` (roles: `personal_administrativo`, `autoridad`)
     - Cuerpo (ejemplos):

       - Marcar como en_progreso (requiere `empleado_correo`):

         ```json
         { "incidente_id": "<uuid>", "estado": "en_progreso", "empleado_correo": "empleado@utec.edu.pe" }
         ```

       - Marcar como resuelto (no requiere `empleado_correo`):

         ```json
         { "incidente_id": "<uuid>", "estado": "resuelto" }
         ```

   - **Historial (mis incidentes)**
     - Método: POST
     - URL: `{{baserUrl_incidentes}}/incidentes/historial`
     - Headers: `Authorization: Bearer <token>` (token de estudiante)
     - Cuerpo (opcional, soporta filtros iguales a `list`):

       ```json
       {
         "page": 0,
         "size": 10,
         "estado": "resuelto"   // opcional
       }
       ```

     - Respuesta: igual al formato paginado de `list`, pero contiene sólo los incidentes del usuario autenticado.

   - **Notas adicionales**
     - El filtrado por `tipo`, `estado` y `nivel_urgencia` está soportado en los listados y en el historial.
     - Las rutas y permisos siguen la lógica implementada en `list_report.py`, `search_report.py`, `update_report_users.py` y `update_report_admin.py`.
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

