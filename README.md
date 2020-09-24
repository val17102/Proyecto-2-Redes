# Proyecto-2-Redes

> Description

> This project is based on the creation of a chat using the XMPP protocol, with which it is possible to register an account on the provided server, start and close session with said account, delete the account, send messages to users and chatrooms, send and get notifications, add and remove contact users, define presence message, get contact details, and send / receive files.


## Contents

- [Instalation](#instalation)
- [Functionality](#functionality)
- [Developers](#developers)


## Instalation

### Tools

> No need to install additional tools. All you need to get started is the command prompt. If it is more convenient you can use any IDE but it is not necessary.

### Python

-Download and install <a href="https://www.python.org/"> Python 3.x </a>

### Libraries

- sys
- logging
- getpass
- base64
- optparse

> These libraries are standard with Python 3.x

- sleekxmpp
- pyasn1
- pyasn1-modules

> Install the listed libraries with pip

```shell
$ pip uninstall pyasn1 peas-modules sleekxmpp
$ pip install pyasn1==0.3.6 pyasn1-modules==0.1.5 
$ pip install sleekxmpp==1.3.3
```

### Clone

> Clone this repository to your local computer `https://github.com/val17102/Proyecto-2-Redes.git`

### Setup

> To start the client: Open a command prompt at the file location "Proyecto2.py"

```shell
$ py Proyecto2.py
```
> Can also be used

```shell
$ python Proyecto2.py
```

> The following options will be presented: 1. To enter with an existing account, 2. To create a new account, 3. To exit the program
```shell
1. Login
2. Register
3. Exit
```

> When logging in with an existing account, all available options will be presented

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

## Functionality

> The communication that is possible with the project is carried out through the XMPP protocol.

## Developers

Miguel Valle
