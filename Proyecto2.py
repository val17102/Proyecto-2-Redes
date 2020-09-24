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
    
    def room_message(self, msg, room):
        self.send_message(mto=room,
                          mbody=msg,
                          mtype='groupchat')
    
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


    def remove_contact(self, jid):
        self.get_roster()
        try:
            self.del_roster_item(jid)
        except IqError as e:
            print(e)

    def join_room(self, room, nick):
        self.room = room
        self.nick = nick
        self.plugin['xep_0045'].joinMUC(room,
                                        nick,
                                        # If a room password is needed, use:
                                        # password=the_room_password,
                                        wait=True)
        self.add_event_handler("groupchat_message", self.muc_message)
        self.send_presence(pto=self.room, pshow="available", pstatus="Conected to Room")

    def create_room(self, room, nick):
        self.room = room
        self.nick = nick
        self.get_roster()
        try:
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
            self.plugin['xep_0045'].setAffiliation(room, self.boundjid.bare, affiliation='owner')
            self.add_event_handler("groupchat_message", self.muc_message)
            self.send_presence(pto=self.room, pshow="available", pstatus="Conected to Room")

        except IqError as e:
            print(e)
        
    def group_message(self, msg):
        self.get_roster()
        self.send_message(mto=self.room,
                          mbody=msg,
                          mtype='groupchat')

    def get_chatRooms(self):
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
    
    def user_info(self, jid):
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
            c = 0
            for i in usersR.findall('.//{jabber:x:data}value'):
                if ((i.text != None) and (i.text == jid)):
                    print(i.text)
                    c = 1
                elif ((i.text != None) and not("@" in i.text) and (c == 1)):
                    print(i.text)
                elif ((i.text != None) and (c==1) and ("@" in i.text)):
                    c = 0
        except IqError as e:
            print(e)
    
    def delete_account(self):
        delete = self.Iq()
        delete['type'] = 'set'
        delete['from'] = self.boundjid.bare
        itemXML = ET.fromstring("<query xmlns='jabber:iq:register'><remove/></query>")
        delete.append(itemXML)
        try:
            delete.send(now=True)
            print("Deleted Account")
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
    room = ''
    nickname = ''
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
            
            while(option2 != "12"):
                    print("Menu")
                    print("1. Write message")
                    print("2. Write message to room")
                    print("3. Join chat room")
                    print("4. Create chat room")
                    print("5. Add contact")
                    print("6. Remove contact")
                    print("7. Show contacts")
                    print("8. Set Status")
                    print("9. Delete Account")
                    print("10. Get user list")
                    print("11. Get user info")
                    print("12. Logout")
                    option2 = input("Ingrese la opcion: ")
                    if (option2 == "1"):
                        recipient = input("Enter the recipients jid: ")
                        msg = input("Message: ")
                        xmpp.message(msg, recipient)
                    elif (option2 == "2"):
                        recipient = input("Enter the room jid: ")
                        msg = input("Message: ")
                        xmpp.room_message(msg, recipient)
                    elif (option2 == "3"):
                        print("Available Rooms")
                        xmpp.get_chatRooms()
                        room = input("Enter room: ")
                        nickname = input("Enter nickname: ")
                        xmpp.join_room(room, nickname)
                    elif (option2 == "4"):
                        room = input("Enter chatroom jid: ")
                        nickname = input("Enter chatroom nickname: ")
                        xmpp.create_room(room, nickname)
                    elif (option2 == "5"):
                        recipient = input("Enter recipient jid to subscribe: ")
                        xmpp.send_subscription(recipient)
                    elif (option2 == "6"):
                        recipient = input("Enter contact jid to remove: ")
                        xmpp.remove_contact(recipient)
                    elif (option2 == "7"):
                        xmpp.show_contacts()
                    elif (option2 == "8"):
                        status = input("Enter new status: ")
                        xmpp.status(status)
                    elif (option2 == "9"):
                        xmpp.delete_account()
                    elif (option2 == "10"):
                        xmpp.get_all_users()
                    elif (option2 == "11"):
                        recipient = input("Enter user jid: ")
                        xmpp.user_info(recipient)
                    elif (option2 == "12"):
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
