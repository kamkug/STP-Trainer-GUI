#!/usr/bin/python3.6



from tkinter import *
#import numpy as np
import json
import logging
from classes.randomizer import randomDomain
from classes.utils import STPUtils
from classes.stpTrainer import STPTrainer

logging.basicConfig(format='%(message)s', level=logging.INFO)

text="""
Author : Kamil Kugler

This software has been created in the will to help others to learn 
STP in a quick and effective manner. There are about 6 different 
pre-programmed STP Domains with 29 possible topologies to play with, 
without having to edit anything at all.

To have another topology loaded for you just come back to this main screen
and press the button at the bottom of it to have another topology
created for you that you can test your skills on.

You could always edit the files and add some of your own topologies
but I would only suggest you to try and change particular links
costs and do not change number of switches in topologies. However
you are free to add links between switches in 4, 5, 6 switches 
topologies if you are willing to test yourself even further.

One thing that this version does not provide is multiple links to
neighboring switches, at the moment I do not have established plans
to implement that feature and possibly never will (but it is rather
simple to define those ports anyway).

I have always considered the biggest challenge being to calculate 
all of the proper costs and figure out which ports belong to :
    
    - Blocking ports
    - Designated ports
    - Root ports

This is the functionality you get here. In according to this, your task
is to define which ports belong to which of aforementioned groups and than
press the button to see whether you were successful or not :)

The process can be a bit daunting at the start but as you get better it
will feel great to see that positive mark at the bottom of the screen
and will make you much more confident about your skills as well.

I hope you are going to enjoy it as much as I did while creating it,
so without further do just press the button below to start all of the fun.
"""


class STPGui():

    def __init__(self):
        #self.domainName = randomizer.randomDomain('stp_domains/text')
        #self.utils = STPUtils()
        #self.stp_domain = self.utils.getInfile(self.domainName, True)
        #self.stpDomainObject = STPTrainer(self.stp_domain, 0, gui=True)
        #self.stpDomain = self.stpDomainObject.domain
        #self.domain = self.stpDomain
        # define a root window and its top level child
        self.root = Tk()
        self.child = Toplevel(self.root)

        # setting up some window characteristics
        self.window_width = 530
        self.window_height = 770
        self.pos_X = int(self.root.winfo_screenwidth() / 2 - self.window_width / 2) # 250 because window is going to be 500 in size 
        self.pos_Y = int(self.root.winfo_screenheight() / 2 - self.window_height / 2) # ^^^^^

        # provide all of required images
        self.question_img = PhotoImage(file="img/question.png")
        self.failure_img = PhotoImage(file="img/failure_mark.png")
        self.success_img = PhotoImage(file="img/success_mark.png")
        self.image = PhotoImage(file="img/switch.png")

        # root create a start of game button
        self.random_stp_btn = Button(self.root, text="Get domain", command=self.raise_child)
        self.random_stp_btn.place(x=200,y=730)

        # create a holder for the root window text
        self.msg = Message(self.root, text=text, background="silver")
        self.msg.place(x=10,y=10)

        # define a self.child window postion 
        self.child.title("STP domain")
        self.child.geometry(f"+{self.root.winfo_x()+740}+{self.root.winfo_y()+200}")
        self.child.resizable(0,0)

        # define a self.root window position
        self.root.title("STP Trainer")
        self.root.geometry(f"{self.window_width}x{self.window_height}+{self.pos_X}+{self.pos_Y}")
        self.root.resizable(0,0)
        self.root.mainloop()


    def add_switch(self, device_name, switch_xPos, switch_yPos, label_xPos, label_yPos, entry_field=None, radio=None):
        """
        Function automates the process of creating an interactive switch and labeling it
        """
        # create a switch as a button
        switch = Button(self.child, text=f"SW{device_name[1]}", image=self.image, command=lambda  device_name=device_name, field=entry_field, radio=radio: self.get_info(device_name, field, radio))
        switch.place(x=switch_xPos, y=switch_yPos)
        # label the switch
        label = Label(self.child, text=f"SW{device_name[1]}")
        label.place(x=label_xPos, y=label_yPos)

    def get_info(self, device_name, field, radio):
        """
        Function collects and display requested information to the user
        """
        option = radio.get()    # collect a chosen option
        field.delete(1.0, END)  # empty an output field

        # just display requested results inside of a given field
        if option == "bridgeID":
            field.insert(END,f"SW{device_name[1]}'s bridge ID is: {self.stpDomainObject.getSwitchBridgeID(device_name)}")
        elif option == "lowest":
            if self.domain[device_name]["lowest"] != '':
                field.insert(END,f"SW{device_name[1]}'s lowest cost is: {self.domain[device_name][self.domain[device_name]['lowest']][1]}\n")
                field.insert(END,f"SW{device_name[1]}'s best next hop is: {self.domain[device_name]['lowest']}")
            else:
                field.insert(END,f"SW{device_name[1]}'s lowest cost is: 0")
        elif option == "role":
            field.insert(END,f"SW{device_name[1]}'s role is: {self.stpDomainObject.getSwitchRole(device_name)}")
        elif option == "ports":
            for key in self.domain[device_name]:
                if key.startswith('s'):
                    field.insert(END, f"SW{device_name}'s port to {key} costs: {self.domain[device_name][key][0]}\n")


    def check_results(self, label, blocking, designated, root ,img1, img2):
        """
        Function is here to check the users input and provide further guidance
        """
        valid = self.stpDomainObject.getSwitchPortRoles()     # collect all of the correct port roles
        self.answers_guide.delete(1.0, END)                   # clear the answers guidance box
        self.info_box.delete(0, END)                          # clear the info box
        
        # try to collect and process users inputs
        try:
            bp = [ self.links_dictionary[int(item)] for item in blocking.get().split(',')]          # create three lists
            dp = [ self.links_dictionary[int(item)] for item in designated.get().split(',')]        # one for each port role 
            rp = [ self.links_dictionary[int(item)] for item in root.get().split(',')]
            
            tests = {                                                                          # create a dictionary holding
                        "Blocking":blocking,                                                   # actual GUI displayer port values
                        "Designated": designated,
                        "Root": root
                    }
            
            port_roles = {                                                                     # create a dictionary of results
                            "Blocking": bp,                                                    # using all of port roles lists
                            "Designated": dp, 
                            "Root": rp
                         }
            counter = 0     # specify a counter to verify the results at the later time

            total_number_of_ports = len(self.links_dictionary)                # hold the count of actual ports
            total_number_of_given_ports = len(bp) + len(dp) + len(rp)    # hold the count of ports that user has assigned to different roles

            for port_role in port_roles:                                            # go over each port role list
                sorted_port_role_items = sorted(port_roles[port_role])              # make sure that both : valid and given results are of the same form
                valid[port_role] = sorted(valid[port_role])                         # do that by sorting them
                
                if sorted(sorted_port_role_items, key=lambda x: x[1]) == sorted(valid[port_role], key=lambda x: x[1]):     # if there is a match increment the counter
                    counter += 1
                else:                                                                                                      # else inform the user about a mismatched port
                    for item in tests[port_role].get().split(','):
                        if self.links_dictionary[int(item)] not in valid[port_role]:
                            logging.info(f"[-] Port {item} is not {(port_role).lower()}")
                            self.answers_guide.insert(END,f"Port {item} is not {(port_role).lower()}\n")
            
            if counter == 3 :                                                       # if there was a full match, congratulate the user
                logging.info("[+] You got it")
                self.info_box.insert(END, "[+] You got it")
                label.config(image=img1)
            elif total_number_of_ports != total_number_of_given_ports:              # if used omitted some ports from his input, make her/him aware
                logging.info("[-] Please assign a role to every port")
                self.info_box.insert(END, "[-] Please assign a role to every existing port (ex. not their duplicates)")
                label.config(image=img2)
            else:                                                                   # if the results are not matchin, inform the user
                logging.info("[-] Please try again")
                self.info_box.insert(END, "[-] Please try again")
                label.config(image=img2)
            
        except KeyError:                                                                          # make the user aware if any of the provided ports are outside of range
            logging.info("[-] This port number is not inside of range")                
            self.info_box.insert(END, "[-] Some of given port numbers are not inside of range")
            return 1
        except ValueError:                                                                        #  make the user aware if a typo was made
            logging.info("[-] Please provide port number using a ',' as a separator.")
            self.info_box.insert(END, "[-] Please provide port numbers using a ',' as a separator.")
            label.config(image=img2)
            return 2

    
    def domains(self, child, devices, image):
        
        """
        Function is a meet and butter of everything,
        it dynamically draws the whole topology , by design itshould work best with 3,4,5 and 6 switches
        and any number of links between them (as long as they connect to their direct neighbors only)
        
        """
    
        # provides required information
        devices_count = len(devices)
        created_links = []
        xPos = 50
        yPos = 20
        odd_counter = 0
        port_id = 0
        even_counter = 0
        times = 0
        counter = 1
        colors = {
                    "4": "#34eb7d",
                    "19": "yellow",
                    "62":  "red",
                    "64":  "red"
                 }
        self.links_dictionary = {}
        canvas = Canvas(child, width = 550, height = 750)
        canvas.pack()

        # create a legend to explain the links coloring
        legend1 = Label(child, bg="#34eb7d", text="04")
        legend2 = Label(child, bg="yellow", text="19")
        legend3 = Label(child, bg="#eb3434", text="62")
        legend1.place(x=5, y=100)
        legend2.place(x=5, y=120)
        legend3.place(x=5, y=140)
       
       
        # create a button that takes us back to a starting page
        go_back = Button(child, text="Go back", command=self.lower_child)
        go_back.place(x=20, y=600) 
        #print(links_dictionary)

        # create a radio button to allow selection of what is meant to display
        options = StringVar()
        options.set("bridgeID")
        radio1 = Radiobutton(child, indicatoro=1, text="Bridge ID", value="bridgeID", variable=options)
        radio1.place(x = 110, y = 600)
        radio2 = Radiobutton(child, indicatoron=1, text="Switch role", value="role", variable=options)
        radio2.place(x = 110, y = 620)
        ports = Radiobutton(child, indicatoro=1, text="Ports", value="ports", variable=options)
        ports.place(x = 110, y = 640)
        lowest = Radiobutton(child, indicatoro=1, text="Lowest", value="lowest", variable=options)
        lowest.place(x = 110, y = 660)
        
        # add an answer field
        textfield_label = Label(child, text="Click on any switch to get the answers")
        textfield_label.place(x = 240, y=580)
        textfield = Text(child, width=30, height=5)
        textfield.place(x = 240, y=600)
        
        # add a blocking ports Entry 
        blocking_label = Label(child, text="Blocking ports: ")
        blocking_label.place(x = 110, y = 480)
        blocking = Entry(child, width=20)
        blocking.place(x = 240, y=480)
        
        # add a designated ports Entry
        designated_label = Label(child, text="Designated ports: ")
        designated_label.place(x = 110, y = 505)
        designated = Entry(child, width=20)
        designated.place(x = 240, y=505)
        
        # add a blocking ports Entry
        root_label = Label(child, text="Root ports: ")
        root_label.place(x = 110, y = 530)
        root = Entry(child, width=20)
        root.place(x = 240, y=530) 
        
        # create an info box
        self.info_box = Entry(child, width=60)
        self.info_box.place(x=50,y=720)
        info_box_label = Label(child, text="Info:")
        info_box_label.place(x=10, y=720)

        # create an answers guide Entry field
        answers_guide_label = Label(child, text="Bad answers")
        answers_guide_label.place(x=360, y=20)
        self.answers_guide = Text(child, width = 25, height=20)
        self.answers_guide.place(x=320, y = 40)
        
        # create a check results button
        result_label = Label(child, text="Try me")
        result_label.place(x = 430, y = 530)
        question_btn = Button(child, text="ask a question", image=self.question_img, command=lambda label=result_label, blocking=blocking, designated=designated, root=root,\
                            img1=self.success_img, img2=self.failure_img: self.check_results(label, blocking, designated, root, img1, img2))
        question_btn.place(x=420, y = 480)
        

        
        if devices_count % 2 == 0:  # if the given domain has an even amount of devices in it
            for device_name in self.domain:    # look up each device
                device = self.domain[device_name]       # make nice name easy to refer to
                if int(device_name[1]) % 2 == 1:  # if device is on the left hand side
                    self.add_switch(device_name, xPos, yPos + 200 * odd_counter, xPos + 5, yPos - 20 + 200 * odd_counter, textfield, options)
                    for key in device:   # find all links
                        if key.startswith('s'):
                            if device[key][4] in created_links:     # skip the process if that link has already been drawn 
                                continue
                            elif int(key[1]) - int(device_name[1]) == 1:  # deal with links to devices on the right hand side to the local device
                                port_id = self.mark_Ports(device,  device_name, key, port_id, xPos + 55,\
                                                    yPos + 15 + 200 * odd_counter, xPos + 200, yPos + 15 + 200 * odd_counter )         # mark ports
                                canvas.create_line(xPos + 40, yPos + 25 + 200 * odd_counter, xPos + 260, yPos+25 + 200 * odd_counter, smooth=1, fill=colors[str(device[key][0])] ,width=2.0)
                                created_links.append(device[key][4])     # ensure this link is recorded as created
                            elif int(key[1]) - int(device_name[1]) == 2: # deal with links to devices that are below the local device
                                port_id = self.mark_Ports(device,  device_name, key, port_id, xPos + 20, \
                                                    yPos + 55 + 200 * odd_counter, xPos + 20, yPos + 150 + 200 * odd_counter )         # mark ports                                                                 
                                canvas.create_line(xPos + 25, yPos + 200 * odd_counter, xPos + 25, yPos + 200 + 200 * odd_counter, smooth=1, fill=colors[str(device[key][0])], width=2.0)
                                created_links.append(device[key][4])   # ensure this link is recorded as created
                            elif int(key[1]) - int(device_name[1]) == 3: # deal with links to devices that are diagonally to the right off the local device
                                port_id = self.mark_Ports(device, device_name, key, port_id, xPos + 50, \
                                                    yPos + 45 + 200 * odd_counter, xPos + 200, yPos + 180 + 200 * odd_counter )     # mark ports

                                canvas.create_line(xPos + 40, yPos + 40 + 200 * odd_counter, xPos + 220, yPos + 200 +200 * odd_counter, smooth=1, fill=colors[str(device[key][0])], width=2.0)
                                created_links.append(device[key][4])   # ensure this link is recorded as created
                    odd_counter += 1    # increment the counter for odd numbered switches, to know the level we are at 
                elif int(device_name[1]) % 2 == 0 :  # deal with devices on the right hand side of the topology
                    
                    self.add_switch(device_name, xPos + 220, yPos + 200 * even_counter, xPos + 225, yPos - 20 + 200 * even_counter, textfield, options)
                    
                    for key in device:  # find all links
                        if key.startswith('s'):
                            if device[key][4] in created_links:         # just continue if that line has already been drawn
                                continue
                            if int(key[1]) - int(device_name[1]) == 1:    # if the neighbor is diagonally to the left
                                port_id = self.mark_Ports(device,  device_name, key, port_id, xPos + 195, \
                                                    yPos + 45 + 200 * even_counter, xPos + 45, yPos + 180 + 200 * even_counter )       # mark ports

                                canvas.create_line(xPos + 220, yPos + 40 + 200 * even_counter, xPos + 40, yPos + 200 + 200 * even_counter, smooth=1, fill=colors[str(device[key][0])], width=2.0)
                                created_links.append(device[key][4])   # remember the link
                            elif int(key[1]) - int(device_name[1]) == 2:  # draw the line downwards
                                port_id = self.mark_Ports(device,  device_name, key, port_id, xPos + 235, \
                                                     yPos + 55 + 200 * even_counter, xPos + 235, yPos + 150 + 200 * even_counter )      # mark ports
                                canvas.create_line(xPos + 220 + 25, yPos + 200 * even_counter, xPos + 220 + 25, yPos + 200 + 200 * even_counter, \
                                                    smooth=1, fill=colors[str(device[key][0])], width=2.0)
                                created_links.append(device[key][4])   # remember the link
                    
                    even_counter += 1  # increment the counter for even numbered switches, to know the level we are at right now
        elif devices_count % 2 == 1: # if there is an odd number of devices involved (the process is pretty much the same)
            for device_name in devices:  # go over each device
                device = devices[device_name] # create a simple variable name
                if int(device_name[1]) % 3 == 1:  # for all switches on the left hand side 

                    self.add_switch(device_name, xPos, yPos + 200 * odd_counter, xPos + 5, yPos - 20 + 200 * odd_counter, textfield, options)
                    for key in device:
                        if key.startswith('s'):
                            if device[key][4] in created_links:             
                                continue
                            if int(key[1]) - int(device_name[1]) == 1:                  # draw the line to the neighbors on the right
                                
                                port_id = self.mark_Ports(device, device_name, key, port_id, xPos + 55,\
                                                    yPos + 15 + 200 * odd_counter, xPos + 160, yPos + 15 + 200 * odd_counter  )    # mark ports
                                
                                canvas.create_line(xPos + 40, yPos + 25 + 200 * odd_counter, xPos + 220, yPos + 25 + 200 * odd_counter, smooth=1, fill=colors[str(device[key][0])] ,width=2.0)
                                created_links.append(device[key][4])                    
                            elif int(key[1]) - int(device_name[1]) == 2:            # draw the line to diagonally placed switches that are to the right hand side
                                
                                port_id = self.mark_Ports(device, device_name, key, port_id, xPos + 40,\
                                                    yPos + 55 + 200 * odd_counter, xPos + 75, yPos + 170 + 200 * odd_counter  )     # mark ports  

                                canvas.create_line(xPos + 40, yPos + 40 + 200 * odd_counter, xPos + 110 - 20, yPos + 200 + 200 * odd_counter, smooth=1, fill=colors[str(device[key][0])], width=2.0)
                                created_links.append(device[key][4])                    # draw the line to switches that are directly below us
                            elif int(key[1]) - int(device_name[1]) == 3:
                                
                                port_id = self.mark_Ports(device, device_name, key, port_id, xPos + 15,\
                                                    yPos + 55 + 400 * odd_counter, xPos + 15, yPos + 350 + 400 * odd_counter  )     # mark ports

                                canvas.create_line(xPos + 25, yPos + 40 + 200 * odd_counter, xPos + 25, yPos + 400 + 200 * odd_counter, smooth=1, fill=colors[str(device[key][0])], width=2.0)
                                created_links.append(device[key][4])
                    odd_counter +=1
                elif int(device_name[1]) % 3 == 0:   # for all switches in the middle 

                    self.add_switch(device_name, xPos + 90, yPos + 200 * odd_counter, xPos + 95, yPos - 20 + 200 * odd_counter, textfield, options)     #<--here
                    for key in device:
                        if key.startswith('s'):
                            if device[key][4] in created_links:
                                continue
                            elif int(key[1]) - int(device_name[1]) == 1:            # draw the line to diagonally placed switches that are to the left


                                port_id = self.mark_Ports(device, device_name, key, port_id, xPos + 80,\
                                                    yPos + 55 + 200 * odd_counter, xPos + 45, yPos + 170 + 200 * odd_counter  )     # mark ports

                                canvas.create_line(xPos + 95, yPos + 40 + 200 * odd_counter, xPos + 45, yPos + 200 + 200 * odd_counter, smooth=1, fill=colors[str(device[key][0])], width=2.0)
                                created_links.append(device[key][4])                # draw the line to diagonally placed switches that are to the right
                            elif int(key[1]) - int(device_name[1]) == 2:
                                

                                port_id = self.mark_Ports(device, device_name, key, port_id, xPos + 133,\
                                                    yPos  + 55 + 200 * odd_counter, xPos + 160, yPos + 170 + 200 * odd_counter )     # mark ports
                                
                                canvas.create_line(xPos + 130, yPos + 40 + 200 * odd_counter, xPos + 120 + 60 , yPos + 200 + 200 * odd_counter, smooth=1, fill=colors[str(device[key][0])], width=2.0)
                                created_links.append(device[key][4])
                    odd_counter +=1
                elif int(device_name[1]) % 3 == 2:   # for all switches on the right hand side

                    self.add_switch(device_name, xPos + 180, yPos + 200 * even_counter, xPos + 185, yPos - 20 + 200 * even_counter, textfield, options)    #<--here
                    for key in device:
                        if key.startswith('s'):
                            if device[key][4] in created_links:
                                continue
                            if int(key[1]) - int(device_name[1]) == 1:              # draw the line to diagonally placed switches that are to the left
                                 
                                port_id = self.mark_Ports(device, device_name, key, port_id, xPos + 175,\
                                                    yPos + 55 + 400 * even_counter, xPos + 135, yPos + 170 + 400 * even_counter )     # mark ports  <---here

                                canvas.create_line(xPos + 185, yPos + 40 + 200 * even_counter, xPos + 135, yPos + 200 + 200 * even_counter, smooth=1, fill=colors[str(device[key][0])], width=2.0)   #<--here
                                created_links.append(device[key][4])     
                            elif int(key[1]) - int(device_name[1]) == 3:            # draw the line to the switches that are direclty below us
                                

                                port_id = self.mark_Ports(device, device_name, key, port_id, xPos + 200,\
                                                    yPos  + 60 + 400 * even_counter, xPos + 200, yPos + 350 + 400 * even_counter )     # mark ports   <--messed here
                                
                                canvas.create_line(xPos + 205, yPos +  40 +  200 * even_counter, xPos + 205 , yPos + 400 + 200 * even_counter, smooth=1, fill=colors[str(device[key][0])], width=2.0)
                                created_links.append(device[key][4])
                    even_counter +=2

    def mark_Ports(self, device, device_name, key, port_id, x_local, y_local, x_neighbor, y_neighbor ):
        """
        Function serves the purpose of marking ports
        """
        port_id += 1                                                # increment a port id for local side port          
        port_num_local = Label(self.child, text=f"{port_id}")                  
        port_num_local.place(x=x_local, y=y_local) 
        self.links_dictionary[port_id] = [device[key][4],device_name]          # create and hold the mapping
        port_id +=1
        port_num_neighbor = Label(self.child, text=f"{port_id}")                 # id neighbors port
        port_num_neighbor.place(x=x_neighbor, y=y_neighbor)
        self.links_dictionary[port_id] = [device[key][4],key]                    # create and hold the mapping
        
        return port_id

    def raise_child(self):
        # update a self.child object and show it again, than lift it 
        # above the self.root and withdraw the self.root
        self.child.update()
        self.child.deiconify()
        self.child.lift()
        self.root.withdraw()
        
        # select a domain to work with and load it
            
        self.domainName = randomDomain('stp_domains/text')
        self.utils = STPUtils()
        self.stp_domain = self.utils.getInfile(self.domainName, True)
        self.stpDomainObject = STPTrainer(self.stp_domain, 0, gui=True)
        self.stpDomain = self.stpDomainObject.domain
        self.domain = self.stpDomain
        self.domains(self.child, self.domain, self.image)

    def lower_child(self):
        # update self.root before bringing it back
        self.root.update()
        self.root.deiconify()
        # lower a self.child object and than make it invisible
        self.child.lower()
        self.child.withdraw()

        # get all of the self.childs objects
        widgets = self.child.winfo_children()
        # clean the self.child object 
        for widget in widgets:
            widget.destroy()
