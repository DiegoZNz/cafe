# cafe
Proyecto Integrador realizado en la materia de Fundamentos de Programación Orientada a Objetos y Administración de base de datos, del 6to cuatrimestre de la carrera de Ingeniería en Computación de la Universidad Politécnica de Querétaro | MAYO - AGOSTO 2023

## Tecnologías utilizadas:

Flask, Python, SqlServer, Bootstrap, CSS

## Introducción

Este proyecto nació como respuesta a una problemática que identificamos en nuestra universidad. En la cafetería, los estudiantes se veían obligados a esperar en largas filas para hacer pedidos, lo que resultaba en una pérdida considerable de tiempo. Además, la preparación de los pedidos anteriores a menudo llevaba mucho tiempo, lo que agregaba más demoras. Nos preguntamos si era posible abordar este problema mediante el desarrollo de una aplicación web que agilizara el proceso de pedidos.

## Desarrollo del Proyecto
Iniciamos el proyecto diseñando y normalizando la base de datos, conectándola a SQL Server y estableciendo todas las funcionalidades necesarias. A continuación, describimos las principales características de la aplicación:

## Interfaz de Usuario
Inicio de Sesión: Al ingresar a la aplicación, se le presentará a los usuarios una pantalla de inicio de sesión que determinará su tipo (administrador o usuario general).

### Panel de Control Administrativo: Para los administradores, el panel de control mostrará las siguientes funciones:

Consulta y edición de productos.

Filtro de productos por disponibilidad.

Gestión de pedidos, incluyendo detalles, estado y acciones como "En proceso" o "Completado."

Seguimiento de usuarios penalizados, con eliminación automática después de tres penalizaciones.

### Funciones del Cliente: Los clientes también tendrán un panel de control desde donde podrán:

Visualizar productos disponibles, agregar al carrito y seleccionar cantidades.

Acumular productos en el carrito y ver el precio total.

Realizar pedidos y consultar su estado en la sección de pedidos.

## Justificación
Nuestra aplicación tiene como objetivo mejorar significativamente la experiencia de compra en la cafetería universitaria. Aunque es posible que no podamos eliminar por completo las filas, nuestro sistema permite a los estudiantes realizar pedidos y pagar sin tener que esperar largos períodos. Esto facilita la vida de los estudiantes, que a menudo tienen poco tiempo para comer entre clases. Además, ayuda al personal de la cafetería a gestionar pedidos de manera más eficiente, ya que la aplicación es amigable y ofrece funciones interactivas para completar y gestionar pedidos con facilidad.
