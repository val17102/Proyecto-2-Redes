import sys
import logging
import getpass
from optparse import OptionParser

import sleekxmpp

if sys.version_info < (3, 0):
    from sleekxmpp.util.misc_ops import setdefaultencoding
    setdefaultencoding('utf8')
else:
    raw_input = input

class Chat(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        self.room = ''
        self.nick = ''

        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.incoming_message)
        self.add_event_handler("changed_status", self.notification_changed_status)
        self.add_event_handler("changed_subscription", self.notification_changed_subscription) 
        self.add_event_handler("got_offline", self.notification_got_offline)
        self.add_event_handler("got_online", self.notification_got_online)


    def start(self, event):
        print("running start")
        self.get_roster()
        self.send_presence()
    
    def notification_changed_status(self, presence):
        print("Notificaction Changed Status")
        print(presence['status'])

    def notification_changed_subscription(self, presence):
        print("Notificaction Changed Subscription")
        print(presence['type'])

    def notification_got_offline(self, presence):
        print("Notificaction Presence Offline")
        print(presence['type'])

    def notification_got_online(self, presence):
        print("Notificaction Presence Online")
        print(presence['type'])

    def incoming_message(self, message):
        if message['type'] in ('chat','normal'):
            print('Direct Message')
            print(message['from'], message['body'])

    def logout(self):
        self.disconnect(wait=True)

    def message(self, msg, recipient):
        self.send_presence()
        self.get_roster()
        self.send_message(mto=recipient,
                          mbody=msg,
                          mtype='chat')
    
    def status(self, status):
        self.send_presence()
        self.get_roster()
        self.make_presence(pfrom=self.jid, pstatus=status)

    def send_subscription(self, recipient):
        self.send_presence_subscription(pto=recipient, ptype='subscribe')


if __name__ == '__main__':
    # Setup the command line arguments.
    optp = OptionParser()

    # Output verbosity options.
    optp.add_option('-q', '--quiet', help='set logging to ERROR',
                    action='store_const', dest='loglevel',
                    const=logging.ERROR, default=logging.INFO)
    optp.add_option('-d', '--debug', help='set logging to DEBUG',
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
    optp.add_option('-v', '--verbose', help='set logging to COMM',
                    action='store_const', dest='loglevel',
                    const=5, default=logging.INFO)

    # JID and password options.
    optp.add_option("-j", "--jid", dest="jid",
                    help="JID to use")
    optp.add_option("-p", "--password", dest="password",
                    help="password to use")
    optp.add_option("-r", "--room", dest="room",
                    help="MUC room to join")
    optp.add_option("-n", "--nick", dest="nick",
                    help="MUC nickname")

    opts, args = optp.parse_args()

    # Setup logging.
    logging.basicConfig(level=opts.loglevel,
                        format='%(levelname)-8s %(message)s')
    
    option1 = -1
    option2 = -1
    msg = ''
    recipient = ''
    room = ''
    nickname = ''
    status = ''
    while(option1 != 3):
        print("Menu")
        print("1. Login")
        print("2. Register")
        print("3. Exit")
        option1 = input("Ingrese la opcion: ")
        if (option1 == "1"):
            opts.jid = raw_input("Username: ")
            opts.password = getpass.getpass("Password: ")
            xmpp = Chat(opts.jid, opts.password)
            xmpp.register_plugin('xep_0030') # Service Discovery
            xmpp.register_plugin('xep_0199') # XMPP Ping
            xmpp.register_plugin('xep_0045') # Multi-user chat
            if xmpp.connect():
                while(option2 != "9"):
                    print("Menu")
                    print("1. Write message")
                    print("2. Join chat room")
                    print("3. Create chat room")
                    print("4. Add contact")
                    print("5. Remove contact")
                    print("6. Show contacts")
                    print("7. Set Status")
                    print("8. Delete Account")
                    print("9. Logout")
                    option2 = input("Ingrese la opcion")
                    if (option2 == "1"):
                        recipient = input("Enter the recipients jid")
                        msg = input("Message: ")
                        xmpp.message(msg, recipient)
                    elif (option2 == "4"):
                        recipient = input("Enter recipient jid to subscribe")
                        xmpp.send_subscription(recipient)
                    elif (option2 == "7"):
                        status = input("Enter new status")
                        xmpp.status(status)
                    elif (option2 == "9"):
                        xmpp.logout()
                xmpp.process(block=True)

                print("Done")
            else:
                print("Unable to connect.")
        elif (option1 == "2"):
            print('')
        elif (option1 == "3"):
            print('')
        else:
            print("Opcion no valida")
