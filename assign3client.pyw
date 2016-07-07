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
This program is a client. When run it can be used to connect
to the server. Contacts can be added and messages then sent
to said contacts instantly. In addition discussion notes can
be saved.
'''


import socket, json, threading, tkMessageBox
import Tkinter as tk 
from time import strftime





class Messagehandler(object):
    """A class responsible for managing and modifying messages.
    """

    def __init__(self):
        """
        Constructor: Messagehandler()
        """
        
        self._localmessagehistory=[]


    def update_localmessages(self, msgs):
        """Update the stored local messages.

        update_localmessages(list<str>) -> None
        """

        self._localmessagehistory = msgs


    def appendmessages(self, name, msg):
        """Appends the time and UI to each message sent.

        appendmessages(str,str) -> str
        """
           
        time = strftime("%H:%M")
        return(time+ '   ' + name + ': ' + msg)

        
    def displaymsgs(self):
        """Converts the message history to a layout formatted for display.

        displaymsgs() -> str
        """
               
        self._prettyview=''
        for i in self._localmessagehistory:
            self._prettyview += i+'\n'
        return self._prettyview



class Client(object):
    """A class which enables connection to the server socket.
    """

    def __init__(self, server_ip):
        """
        Constructor: Client(server_ip)
        """
        
        self._host = server_ip 
        self._port = 8888 
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._error = False
        try:
            self._s.connect((self._host, self._port))
        except:
            print "Unable to connect!"
            self._error = True
            return
        print 'Successfully connected to server, ' + server_ip 

     
    
class App(object):
    """The top-level class for the GUI, managing the friends list, managing chat
    and referencing other classes when needed.
    """
    
    def __init__(self, master):   
        """
        Constructor: App()
        """

        master.title("Instant Messenger v1.0")
        master.geometry("700x450")

        #Intialise variables
        self._msgs=Messagehandler()
        self._client = None
        self._listoffriends=[]
        self._lastselectedfriend=None
        self._current_chat_history=None
        self._validUI = False
        self._succesful_login=False
        self._connectionlost=False
        self._localnotes = None

        #---GUI---
            ##Leftmost frame, for connection details and friend list
        self._receiverdetails = tk.Frame(master)

        self._ui_title=tk.Label(self._receiverdetails, \
                                text='Unique Identifier:')
        self._ui_title.pack(side=tk.TOP)

        self._input_ui = tk.Entry(self._receiverdetails)
        self._input_ui.pack(side=tk.TOP)

        myip=socket.gethostbyname(socket.gethostname())
        self._myip=tk.Label(self._receiverdetails, text='My IP Address: '+myip)
        self._myip.pack(side=tk.TOP)
             
        self._serverip_title=tk.Label(self._receiverdetails,\
                                      text='Server IP Address:')
        self._serverip_title.pack(side=tk.TOP)

        self._input_serverip = tk.Entry(self._receiverdetails)
        self._input_serverip.pack(side=tk.TOP)

        self._login=tk.Button(self._receiverdetails, text='Login', \
                                 command = self.login) 
        self._login.pack(side=tk.TOP)    

        self._title=tk.Label(self._receiverdetails, text='Friend List:')
        self._title.pack(side=tk.TOP)

                ###Sub-frame for friend list and scrollbar 
        self._flist = tk.Frame(self._receiverdetails)
        
        scrollbar = tk.Scrollbar(self._flist)
        scrollbar.pack( side = tk.RIGHT, fill=tk.Y )

        self._friendlist = tk.Listbox(self._flist, \
                                      yscrollcommand = scrollbar.set )
        self._friendlist.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self._friendlist.bind("<<ListboxSelect>>", self.reacttoselection)

        scrollbar.config( command = self._friendlist.yview )
        
        self._flist.pack(fill=tk.Y, expand=True)
                ###Exit sub-frame

        self._name_title=tk.Label(self._receiverdetails,\
                                  text='Friend Unique Identifier:')
        self._name_title.pack(side=tk.TOP)

        self._inputfname = tk.Entry(self._receiverdetails)
        self._inputfname.pack(side=tk.TOP)
        self._inputfname.bind('<Return>', self.enterevent2)  

        self._addfriend=tk.Button(self._receiverdetails, text='Add Friend', \
                                 command = self.add_friend) 
        self._addfriend.pack(side=tk.TOP)      

        self._receiverdetails.pack(side=tk.LEFT, fill=tk.Y)
            ##exit leftmost frame



            ##Middle frame, for chat interface
        self._chatwindow = tk.Frame(master)

        self._title2=tk.Label(self._chatwindow, text='Chat Window')
        self._title2.pack(side=tk.TOP)        
        
                ###Sub-frame for chat window and scrollbar 
        self._frame_chat = tk.Frame(self._chatwindow)

        scrollbar2 = tk.Scrollbar(self._frame_chat)
        scrollbar2.pack( side = tk.RIGHT, fill=tk.Y, expand=False )
        
        self._chatdisplay= tk.Text(self._frame_chat, \
                        font=self._title2.cget("font"), bg = "white", bd=2,\
                                relief=tk.SUNKEN, width = 20, state="disabled")                                          
        self._chatdisplay.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        scrollbar2.config( command = self._chatdisplay.yview )

        self._frame_chat.pack(fill=tk.BOTH, expand=True)
                ###Exit sub-frame  

        self._texttosend =tk.Entry(self._chatwindow)
        self._texttosend.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._texttosend.bind('<Return>', self.enterevent)        

        self._send=tk.Button(self._chatwindow, text='Send', \
                                 command = self.add_message) 
        self._send.pack(side=tk.RIGHT)
        
        self._chatwindow.pack(side=tk.LEFT, expand = True, fill=tk.BOTH)
            ##exit middle frame

        

            ##Right frame, for note taking 
        self._notewindow=tk.Frame(master)

        self._title3=tk.Label(self._notewindow, text='Note Taking Window')
        self._title3.pack(side=tk.TOP)

        scrollbar3 = tk.Scrollbar(self._notewindow)
        scrollbar3.pack( side = tk.RIGHT, fill=tk.Y)
        
        self._notearea = tk.Text(self._notewindow, width = 30)
        self._notearea.pack(side=tk.TOP, expand = True, fill=tk.BOTH)

        scrollbar3.config(command = self._notearea.yview )

        self._notesend=tk.Button(self._notewindow, text='Save Notes', \
                                 command = self.add_notes) 
        self._notesend.pack(side=tk.TOP)
        
        self._notewindow.pack(side=tk.LEFT, expand = True, fill=tk.BOTH)
            ##exit right frame        



    def login(self): 
        """Runs when the user first logs in. Connects to server,
        downloads friends list and displays it.
        
        login() -> None
        Precondition: Unique Identifier entered is unique.
        """

        if len(self._input_ui.get()) == 0: #nothing entered as UI
            tkMessageBox.showerror('Error', "Invalid Login")     
            return
        
        if self._input_ui.get().isspace(): #spaces entered as UI
            tkMessageBox.showerror('Error', "Invalid Login")     
            return

        self._validUI = True
        
        server_ip=self._input_serverip.get()
        print 'Connecting to ' + server_ip 
        self._client = Client(server_ip)
        if self._client._error:
            tkMessageBox.showerror('Error', "Invalid Server IP")     
            return
        
        UI = self._input_ui.get()       
        msg=['download friends', UI]
        encoded = json.dumps(msg) 
        self._client._s.send(encoded)

        encoded2 = self._client._s.recv(4096)
        friendslist = json.loads(encoded2)
        if friendslist == 'None':
            friendslist = []
        self._listoffriends = friendslist
        self.listfriends()
        self._succesful_login=True
        self._input_ui.configure(state='disabled')
        self._input_serverip.configure(state='disabled')


    def listfriends(self):
        """Displays the friends list in the friends listbox.

        listfriends() -> None
        """
        
        self._friendlist.delete(0, tk.END)
        for i in self._listoffriends:
            self._friendlist.insert(tk.END, i)


    def add_friend(self): 
        """Messages the server with a command to update the UI's friend list.
        Returns a list of friends which is saved and displayed.
        
        add_friend() -> None
        """
        if self._succesful_login == False:
            return

        if len(self._inputfname.get()) == 0: #nothing entered as name
            tkMessageBox.showerror('Error', "Invalid Friend UI")     
            return
        
        if self._inputfname.get().isspace(): #spaces entered as name
            tkMessageBox.showerror('Error', "Invalid Friend UI")     
            return 
        
        UI = self._input_ui.get()
        friendname = self._inputfname.get()
        
        msg=['update friends', UI, friendname]
        encoded = json.dumps(msg)
        self._client._s.send(encoded)

        encoded2 = self._client._s.recv(4096)
        friendslist = json.loads(encoded2)
        self._listoffriends = friendslist
        self.listfriends()
        self._inputfname.delete(0, 'end')
        self._friendlist.see(tk.END)

    
    def reacttoselection(self,e):
        """When a friend is selected, displays their conversation and changes
        the window title to their name.
        
        reacttoselection(tk.event) -> None
        """
        
        if self._lastselectedfriend == None: #only initiates refreshing once
            self.refreshloop()

        if self._friendlist.size() == 0:
            return
                    
        self._lastselectedfriend=self._friendlist.get(\
            self._friendlist.curselection()[0])
        self._title2.config(text='Chatting with ' + self._lastselectedfriend)
        self.list_messages()
        self.download_notes()
        
              
    def refreshloop(self):
        """Repeatedly downloads the message history for the selected friend
        and displays it when it changes.

        refreshloop() -> None
        """

        try:
            threading.Timer(1.0, self.refreshloop).start()
            self.list_messages()
        except Exception:
            if not self._connectionlost:
                print "Connection lost. Please restart client and try again."
            self._connectionlost=True

                    
    def list_messages(self):
        """For the selected friend, sends a command to the server to download
        their chat history. The server returns a list that represents the
        chat history. This is displayed if it is different to that currently
        displayed.

        list_messages() -> None        
        """
        
        UI = self._input_ui.get()
        if self._lastselectedfriend == None:
            return 
        friendname = self._lastselectedfriend
        participants = [UI, friendname]
 
        msg=['download chat history', participants]
        encoded = json.dumps(msg) 
        self._client._s.send(encoded)

        encoded_chat = self._client._s.recv(4096)
        unencoded = json.loads(encoded_chat)
        if self._current_chat_history != unencoded:
            self._current_chat_history = unencoded
            self.show_chat()
            self._chatdisplay.see(tk.END)

        
    def show_chat(self):
        """Displays the saved message history.

        show_chat() -> None
        """
        
        self._chatdisplay.configure(state ='normal')
        self._chatdisplay.delete("1.0", tk.END)
        self._msgs.update_localmessages(self._current_chat_history)
        self._chatdisplay.insert(tk.END, self._msgs.displaymsgs())
        self._chatdisplay.configure(state="disabled")
            

    def add_message(self):
        """Messages the server to update the relevant conversation history
        with an appended user message. Also updates the local copy of the
        chat history and displays it.

        add_message() -> None
        """

        if self._succesful_login == False:
            return

        if self._lastselectedfriend == None:
            return
        
        UI = self._input_ui.get()
        friendname = self._lastselectedfriend
        participants = [UI, friendname]
        message = self._texttosend.get()
        if len(message) ==0:
            return
        message2 =self._msgs.appendmessages(UI, message)

        msg=['update chat history', participants, message2] 
        encoded = json.dumps(msg) 
        self._client._s.send(encoded)

        encoded_chat = self._client._s.recv(4096)
        unencoded = json.loads(encoded_chat)
        self._current_chat_history = unencoded
        self.show_chat()
        self._texttosend.delete(0, 'end')
        self._chatdisplay.see(tk.END)


    def enterevent(self,e):
        """When the 'enter' key is pressed, sends the message in the chat
        message box.
        
        enterevent(tk.event) -> None
        """
        
        self.add_message()

 
    def enterevent2(self,e):
        """When the 'enter' key is pressed, saves the friend to the list.
        
        enterevent(tk.event) -> None
        """
        
        self.add_friend()


    def add_notes(self):
        """Messages the server to update the notes for the UI and friend combo. 
        Also updates the local copy of the notes and displays it.

        add_notes() -> None
        """

        if self._succesful_login == False:
            return

        if self._lastselectedfriend == None:
            return
        
        UI = self._input_ui.get()
        friendname = self._lastselectedfriend
        participants = [UI, friendname]
        message = self._notearea.get("1.0",'end-1c')
        if len(message) ==0:
            return

        msg=['update notes', participants, message]
        encoded = json.dumps(msg) 
        self._client._s.send(encoded)

        encoded_chat = self._client._s.recv(4096)
        unencoded = json.loads(encoded_chat)
        self._localnotes = unencoded
        self._notearea.delete("1.0", tk.END)
        self._notearea.insert(tk.END, self._localnotes)
        self._notearea.see(tk.END)


    def download_notes(self):
        """Messages the server to send the notes for the UI and friend combo.
        Also updates the local copy of the notes and displays it.

        download_notes() -> None
        """
      
        UI = self._input_ui.get()
        friendname = self._lastselectedfriend
        participants = [UI, friendname]

        msg=['download notes', participants]
        encoded = json.dumps(msg) 
        self._client._s.send(encoded)

        encoded_chat = self._client._s.recv(4096)
        unencoded = json.loads(encoded_chat)
        self._localnotes = unencoded
        self._notearea.delete("1.0", tk.END)
        self._notearea.insert(tk.END, self._localnotes)
        self._notearea.see(tk.END)        

        
        
root = tk.Tk()
app = App(root)
root.mainloop()
