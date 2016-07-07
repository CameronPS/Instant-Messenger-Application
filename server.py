#! python2


'''
Instant Messenger v1.0
Copyright (c) 2015, Cameron Pickering-Smith
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer. 
Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution. 
Neither the name of Cameron Pickering-Smith nor the names of his contributors may be used to endorse or promote products derived from this software without specific prior written permission. 
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

'''
This program is a server. When run it can be used to connect
to clients. using clients contacts can be added and messages
then sent to said contacts instantly. In addition discussion
notes can be saved.
'''

import socket, json
from thread import *

 
host = ''   
port = 8888 
 
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Socket created'
 
socket.bind((host, port))    
print 'Socket bound'
 
socket.listen(5)
print 'Socket now listening'

serverfrienddict = {}
server_chat_history ={}
server_note_history ={}


def addfriend(UI,friend):
    """Appends a friend to a list corresponding to a dictionary value for a
    key which equals the UI.

    addfriend(str,str) -> None
    """

    if UI not in serverfrienddict: #creates entry (a blank list) if UI is new
        serverfrienddict[UI]=[]      
        
    listofpeople = serverfrienddict[UI]
    if friend not in listofpeople: 
        listofpeople.append(friend)

    
def update_chat_history(people_list,msg):
    """Appends a message to a list of messages, which act as a dictionary
    value for a key equal to a sorted str of conversation participants.
    Returns the total conversation history. 

    update_chat_history(list,str) -> list<str>
    """
      
    message = msg
    participants_list = people_list
    participants_list.sort()
    chat_savename=str(participants_list)

    past_chat_list=server_chat_history[chat_savename]
    updated_past_chat_list = past_chat_list.append(message)
    return server_chat_history[chat_savename]


def return_chat_history(people_list):
    """Returns the total conversation history for a given combination
    of people.

    return_chat_history(list) -> list<str>
    """
    
    participants_list = people_list
    participants_list.sort()
    chat_savename=str(participants_list)

    if chat_savename not in server_chat_history:
    #creates entry (a blank list) if people combination is new
        server_chat_history[chat_savename]=[]    

    past_chat_list=server_chat_history[chat_savename]
    return server_chat_history[chat_savename]


def save_notes(people_list,msg):
    """Saves a copy of the notes for each UI+friend combination in a
    dictionary. Returns a copy as well.

    save_notes(list,str) -> str
    """
      
    message = msg
    participants_list = people_list
    note_savename=str(participants_list)

    if note_savename not in server_note_history: 
        server_note_history[note_savename]=" "    

    server_note_history[note_savename] = message
    return server_note_history[note_savename]


def client_cmd_interpreter(conn): 
    """The main function of the server. Receives (encoded) commands from
    the client, interprets and responds with the appropriate information.

    client_cmd_interpreter(socket) -> None
    """
    try:
        while True:
            data = conn.recv(4096)
            
            if len(data) == 0:
                continue

            decoded=json.loads(data)               
            input_cmd = decoded[0]


            if input_cmd == 'update friends':              
                UI=decoded[1]
                newfriend=decoded[2]
                addfriend(UI,newfriend)
                
                UIsfriends = serverfrienddict[UI]
                encoded2=json.dumps(UIsfriends)
                conn.send(encoded2)            

                
            if input_cmd == 'download friends':
                UI=decoded[1]
                if UI in serverfrienddict:
                    UIsfriends = serverfrienddict.get(UI)
                    encoded2=json.dumps(UIsfriends)
                    conn.send(encoded2)
                else:
                    encoded2=json.dumps('None')
                    conn.send(encoded2)                


            if input_cmd == 'update chat history':
                message=decoded[2]            
                participants_list=decoded[1]
                chat_history=update_chat_history(participants_list,message)

                encodedchat = json.dumps(chat_history)
                conn.send(encodedchat)   


            if input_cmd == 'download chat history':          
                participants_list=decoded[1]
                chat_history=return_chat_history(participants_list)
                encodedchat = json.dumps(chat_history)
                conn.send(encodedchat)


            if input_cmd == 'update notes':
                message=decoded[2]            
                participants_list=decoded[1]
                notes=save_notes(participants_list,message)

                encodedchat = json.dumps(notes)
                conn.send(encodedchat)
                
            if input_cmd == 'download notes':
                participants_list=decoded[1]
                note_savename=str(participants_list)

                if note_savename not in server_note_history: 
                    server_note_history[note_savename]=' '

                notes = server_note_history[note_savename] 

                encodedchat = json.dumps(notes)
                conn.send(encodedchat)
            
                
    except Exception:
        print "A user disconnected"
         

while True:
    conn, address = socket.accept()
    print 'Successfully connected to ' +address[0] +':' +str(address[1]) 
     
    start_new_thread(client_cmd_interpreter,(conn,))
    #start a new thread, allows multiple clients
