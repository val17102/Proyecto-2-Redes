# Proyecto-2-Redes

> Descripción

> El presente proyecto está basado en la creación de un chat utilizando el protocolo XMPP, con el cual sea posible registrar una cuanta en el servidor proveido, iniciar y cerrar sesión con dicha cuenta, eliminar la cuenta, envío de mensajes a usuarios y chatrooms, mandar y obtener notificaciones, agregar y eliminar usuarios de contacto, definir mensaje de presencia, obtener detalles de los contactos, y enviar/recibir archivos.


## Contenido

- [Instalación](#instalación)
- [Funcionamiento](#funcionamiento)
- [Desarrolladores](#desarrolladores)


## Instalación

### Herramientas

> No es necesario instalar herramientas adicionales. Todo lo necesario para comenzar es el command prompt. Si es más conveniente se puede usar cualquier IDE pero no es necesario.

### Python

-Descargar e instalar <a href="https://www.python.org/"> Python 3.x </a>

### Librerías

- sys
- logging
- getpass
- base64
- optparse

> Estas librerías utilizadas son estándar con Python 3.x

- sleekxmpp
- pyasn1
- pyasn1-modules

> Instalar las siguientes librerías con pip

```shell
$ pip uninstall pyasn1 peas-modules sleekxmpp
$ pip install pyasn1==0.3.6 pyasn1-modules==0.1.5 
$ pip install sleekxmpp==1.3.3
```

### Clone

> Clonar este repositorio a tu ordenador local `https://github.com/val17102/Proyecto-2-Redes.git`

### Setup

> Para iniciar el servidor: Abrir un command prompt en la ubicación del archivo "Proyecto2.py"

```shell
$ py Proyecto2.py
```
> También se puede usar

```shell
$ python Proyecto2.py
```

> Se presentaran las siguientes opciones 1. Para ingresar con una cuenta existente, 2. Para crear una cuenta nueva, 3. Para salir del programa

```shell
1. Login
2. Register
3. Exit
```

> Al ingresar con una cuenta existente se presentaran todas las opciones disponibles

```shell
Menu
1. Write message
2. Write message to room
3. Join chat room
4. Create chat room
5. Add contact
6. Remove contact
7. Show contacts
8. Set Status
9. Delete Account
10. Get user list
11. Get user info
12. Logout
```

## Funcionamiento

> El funcionamiento de la comunicación que es posible con el proyecto se lleva a cabo por medio de el protocolo XMPP. 

## Desarrolladores

Miguel Valle
