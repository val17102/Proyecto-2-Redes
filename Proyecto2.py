import sys
import logging
import getpass
from optparse import OptionParser

import sleekxmpp
from sleekxmpp.exceptions import IqError, IqTimeout
from sleekxmpp.xmlstream.stanzabase import ET, ElementBase
if sys.version_info < (3, 0):
    from sleekxmpp.util.misc_ops import setdefaultencoding
    setdefaultencoding('utf8')
else:
    raw_input = input

class Register(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        self.add_event_handler("session_start", self.start)
        self.add_event_handler("register", self.register)
    
    def start(self, event):
        self.send_presence()
        self.get_roster()

        # We're only concerned about registering, so nothing more to do here.
        self.disconnect()
    
    def register(self, iq):
        resp = self.Iq()
        resp['type'] = 'set'
        resp['register']['username'] = self.boundjid.user
        resp['register']['password'] = self.password

        try:
            resp.send(now=True)
            logging.info("Account created for %s!" % self.boundjid)
        except IqError as e:
            logging.error("Could not register account: %s" % 
                    e.iq['error']['text'])
            self.disconnect()
        except IqTimeout:
            logging.error("No response from server.")
            self.disconnect()


class Chat(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        self.room = ''
        self.nick = ''
        self.auto_authorize = True
        self.auto_subscribe = True
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.incoming_message)
        self.add_event_handler("changed_status", self.notification_changed_status)
        self.add_event_handler("changed_subscription", self.notification_changed_subscription) 
        self.add_event_handler("got_offline", self.notification_got_offline)
        self.add_event_handler("got_online", self.notification_got_online)
        self.add_event_handler("presence_subscribe", self.notification_subscribe)
        self.add_event_handler("presence_unsubscribe", self.notification_remove_subscribe)
        if self.connect():
            print(":waving_hand:" + "You have succesfully sign in")
            self.process(block=False)
        else:
            raise Exception("Unable to connect to Redes Jabber server")

    def start(self, event):
        self.send_presence(pshow='chat', pstatus="Conected")
        self.contacts = []
        print("running start")
        self.get_roster()
    
    def notification_changed_status(self, presence):
        if (presence['from'].bare != self.boundjid.bare):
            print("Notificaction Changed Status")
            print(presence['from'].bare, ': ' ,presence['status'])

    def notification_changed_subscription(self, presence):
        if (presence['from'].bare != self.boundjid.bare and presence['show'] != ""):
            print("Notificaction Changed Subscription")
            print(presence['from'].bare, ': ' ,presence['show'])

    def notification_got_offline(self, presence):
        if (presence['from'].bare != self.boundjid.bare):
            print("Notificaction Presence Offline")
            print(presence['from'].bare, ': offline')

    def notification_got_online(self, presence):
        if (presence['from'].bare != self.boundjid.bare):
            print("Notificaction Presence Online")
            print(presence['from'].bare, ': online')

    def notification_subscribe(self, presence):
        if presence['from'].bare != self.boundjid.bare:
            print(presence['from'].bare, ": added to roster")

    def notification_remove_subscribe(self, presence):
        if presence['from'].bare != self.boundjid.bare:
            print(presence['from'].bare, ": removed from roster")

    def incoming_message(self, message):
        if message['type'] in ('chat','normal'):
            print('Direct Message')
            print(message['from'], message['body'])

    def logout(self):
        self.disconnect(wait=True)

    def message(self, msg, recipient):
        self.send_message(mto=recipient,
                          mbody=msg,
                          mtype='chat')
    
    def status(self, status):
        self.send_presence(pstatus=status, pshow='available')

    def send_subscription(self, recipient):
        self.send_presence_subscription(pto=recipient, ptype='subscribe')

    def show_contacts(self):
        self.get_roster()
        groups = self.client_roster.groups()
        data = []
        self.contacts = []
        for group in groups:
            for i in groups[group]:
                self.contacts.append(i)
                sub = self.client_roster[i]['subscription']
                name = self.client_roster[i]['name']
                con = self.client_roster.presence(i)
                status = ''
                for res, pres in con.items():
                    if pres['status']:
                        status = pres['status']
                data.append([name, i, sub, status])
        print(data)
        for j in data:
            if j[1] != self.boundjid:
                print(j[1],": ",j[3])

    def notify_contacts(self):
        roster = self.get_roster()
        for i in roster['roster']['items'].keys():
            self.contacts.append(i)
        for j in self.contacts:
            message = self.Message()
            message['to'] = j
            message['type'] = 'chat'
            message['body'] = 'Ready'
            itemXML = ET.fromstring("<active xmlns='http://jabber.org/protocol/chatstates'/>")
            message.append(itemXML)
            try:
                message.send()
            except IqError as e:
                print("Failed notification", e)


    def remove_contact(self, jid):
        self.get_roster()
        self.del_roster_item(jid)

    def join_room(self, room, nick):
        self.get_roster()
        self.plugin['xep_0045'].joinMUC(room,
                                        nick,
                                        # If a room password is needed, use:
                                        # password=the_room_password,
                                        wait=True)
        self.add_event_handler("groupchat_message", self.muc_message)

    def create_room(self, room, nick):
        self.get_roster()
        self.plugin['xep_0045'].joinMUC(room,
                                        nick,
                                        # If a room password is needed, use:
                                        # password=the_room_password,
                                        wait=True)
        roomform = self.plugin['xep_0045'].getRoomConfig(room)
        roomform.set_values({
            'muc#roomconfig_persistentroom': 1,
            'muc#roomconfig_roomdesc': 'Plin plin plon'
        })
        self.plugin['xep_0045'].configureRoom(room, form=roomform)
    
    def group_message(self, msg):
        self.get_roster()
        self.send_message(mto=self.room,
                          mbody=msg,
                          mtype='groupchat')

    def get_chatRooms(self):
        self.send_presence()
        self.get_roster()
        result = self.plugin['xep_0030'].get_items(jid='conference.redes2020.xyz')
        for room in result['disco_items']:
            print(room['jid'])

    def muc_message(self, msg):
        print("muc message")
        if msg['mucnick'] != self.nick:
            print(msg['mucroom'])
            print(msg['mucnick'], ': ',msg['body'])

    def get_all_users(self):
        users = self.Iq()
        users['type'] = 'set'
        users['to'] = 'search.redes2020.xyz'
        users['from'] = self.boundjid.bare
        users['id'] = 'search_result'
        stanza = ET.fromstring(
            "<query xmlns='jabber:iq:search'>\
                <x xmlns='jabber:x:data' type='submit'>\
                    <field type='hidden' var='FORM_TYPE'>\
                        <value>jabber:iq:search</value>\
                    </field>\
                    <field var='Username'>\
                        <value>1</value>\
                    </field>\
                    <field var='search'>\
                        <value>*</value>\
                    </field>\
                </x>\
            </query>"
        )
        users.append(stanza)
        try:
            print("User List")
            usersR = users.send()
            for i in usersR.findall('.//{jabber:x:data}value'):
                if ((i.text != None) and ("@" in i.text)):
                    print(i.text)
        except IqError as e:
            print(e)
            
                
                

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
    status = ''
    while(option1 != "3"):
        print("Menu")
        print("1. Login")
        print("2. Register")
        print("3. Exit")
        option1 = input("Ingrese la opcion: ")
        if (option1 == "1"):
            opts.jid = raw_input("Username: ")
            opts.password = getpass.getpass("Password: ")
            xmpp = Chat(opts.jid, opts.password)
            xmpp.register_plugin('xep_0077')
            xmpp.register_plugin('xep_0030') # Service Discovery
            xmpp.register_plugin('xep_0199') # XMPP Ping
            xmpp.register_plugin('xep_0045') # Multi-user chat
            xmpp.register_plugin('xep_0096')
            xmpp.register_plugin('xep_0065')
            xmpp.register_plugin('xep_0004')
            
            while(option2 != "10"):
                    print("Menu")
                    print("1. Write message")
                    print("2. Join chat room")
                    print("3. Create chat room")
                    print("4. Add contact")
                    print("5. Remove contact")
                    print("6. Show contacts")
                    print("7. Set Status")
                    print("8. Delete Account")
                    print("9. Get user list")
                    print("10. Logout")
                    option2 = input("Ingrese la opcion")
                    if (option2 == "1"):
                        recipient = input("Enter the recipients jid")
                        msg = input("Message: ")
                        xmpp.message(msg, recipient)
                    elif (option2 == "2"):
                        xmpp.get_chatRooms()
                    elif (option2 == "3"):
                        room = input("Enter chatroom jid")
                        nickname = input("Enter chatroom nickname")
                    elif (option2 == "4"):
                        recipient = input("Enter recipient jid to subscribe")
                        xmpp.send_subscription(recipient)
                    elif (option2 == "5"):
                        recipient = input("Enter contact jid to remove")
                        xmpp.remove_contact(recipient)
                    elif (option2 == "6"):
                        xmpp.show_contacts()
                    elif (option2 == "7"):
                        status = input("Enter new status")
                        xmpp.status(status)
                    elif (option2 == "8"):
                        print("Shut the fuck up")
                    elif (option2 == "9"):
                        xmpp.get_all_users()
                    elif (option2 == "10"):
                        xmpp.logout()
        elif (option1 == "2"):
            opts.jid = raw_input("Username: ")
            opts.password = getpass.getpass("Password: ")

            xmpp = Register(opts.jid, opts.password)
            xmpp.register_plugin('xep_0030') # Service Discovery
            xmpp.register_plugin('xep_0004') # Data forms
            xmpp.register_plugin('xep_0066') # Out-of-band Data
            xmpp.register_plugin('xep_0077') # In-band Registration
            if xmpp.connect():
                xmpp.process(block=True)
                print("Done")
            else:
                print("Unable to connect.")
        elif (option1 == "3"):
            print('')
        else:
            print("Opcion no valida")
