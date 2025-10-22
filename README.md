Guía para configurar el proyecto
¡Hola! Aquí están los pasos para descargar y ejecutar el proyecto localmente.
Requisitos Previos:
Asegurarse de tener instalado:
•	VS Code: https://code.visualstudio.com/download
•	Python (versión 3.10 o superior): https://www.python.org/downloads/
•	Git: https://git-scm.com/
•	PostgreSQL: https://www.enterprisedb.com/downloads/postgres-postgresql- downloads
Se ejecutan por ahora solo los instaladores de VS Code, Python y Git en este punto. Le dan next a todo y continuan.


Guía de Configuración Inicial:
Paso 1: Clonar el Repositorio
Abran una terminal (CMD / Símbolo del sistema preferiblemente) en la carpeta donde van a guardar el proyecto y ejecuten el siguiente comando:
# git clone https://github.com/pipao1229/proyecto-diseno-software.git
Luego, entren en la carpeta que se acaba de crear:
cd proyecto-diseno-software


Paso 2: Configurar el Entorno Virtual
Cada uno debe tener su propio entorno aislado para las librerías del proyecto. Ejecutar:
# 1. Crear el entorno virtual python -m venv venv

# 2. Activar el entorno virtual venv\Scripts\activate

IMPORTANTE: Se debe usar esta misma terminal para ejecutar todos los siguientes comandos, ya que usa el entorno virtual configurado
 
Paso 3: Instalar Dependencias
Vamos a instalar todas las librerías necesarias que están listadas en el archivo requirements.txt. Ejecutar:
# pip install -r requirements.txt

Paso 4: Configurar la Base de Datos Local
Cada uno necesita su propia base de datos local. El código no se conecta a una base de datos central, sino a una en su propia máquina.
1.	Ejecuten el instalador de PostgreSQL
a.	Instalen todos los componentes recomendados, especialmente pgAdmin 4, para la configuración.
b.	Les pedirá que establezca una contraseña para el superusuario postgres. Anótenla, ya que se necesitará para el siguiente paso.
c.	El puerto por defecto es 5432. Déjenlo así.
d.	La configuración regional déjela en la predeterminada (“DEFAULT”).
e.	Esperan a que termine la descarga y cierran la ventana.
2.	Abran pgAdmin 4: Búsquenlo en su menú de inicio. Es una aplicación que se abrirá en su dispositivo.
a.	Conectarse al Servidor:
i.	En el panel izquierdo, verán "Servers". Hagan doble clic.
ii.	Les pedirá la contraseña del superusuario postgres que establecieron durante la instalación.
b.	Crear un Usuario (Rol de Inicio de Sesión):
i.	Hagan clic derecho sobre "Login/Group Roles" -> "Create" -> "Login/Group Role..."
ii.	En la pestaña General: Ponen este nombre de usuario:
postgres_user.
iii.	En la pestaña Definition: Ponen la contraseña para este usuario. Usamos todos la misma: proyectoDS1234*
Esto porque sino todos tendrían que cambiar la contraseña en el archivo de configuración y luego habría problemas con las versiones
En la pestaña Properties: Asegurense de marcar la casilla “Can login?” para que el usuario siempre se pueda conectar a la base de datos.
c.	Crear la Base de Datos:
i.	Hagan clic derecho sobre "Databases" -> "Create" -> "Database...".
ii.	En la pestaña General: Ponen el nombre de la base de datos. Nuevamente, usamos todos el mismo: campaign_db.
iii.	En el campo Owner (Propietario), seleccionan el usuario que acaban de crear (postgres_user). Esto le da automáticamente todos los permisos necesarios sobre esta base de datos.
iv.	Hacen clic en "Save"
 
¡Listo! Ya crearon la base de datos campaign_db y el usuario postgres_user con la contraseña, y ambos ya están vinculados. Esto queda para la persistencia de datos


Paso 5: Ejecutar las Migraciones
Este comando creará todas las tablas necesarias en su base de datos local recién configurada.
# python manage.py migrate
Paso C: Iniciar el Servidor
¡Ya está todo listo! Pueden iniciar el servidor de desarrollo de Django:
# python manage.py runserver
Visiten http://127.0.0.1:8000/ en su navegador. Deberían ver la página con el dashboard.

De ahora en adelante, pueden usar la terminal directa de VS Code. Presionan sobre "Terminal" -> "Nueva Terminal". Cuando se abra, se va a abrir con powershell, nada más presionan la flecha al lado del botón de “+”, escogen “Command Prompt” y ya se les activa el entorno virtual en esa terminal (aparece como (venv) C:\Users\...)
