import bluetooth
import subprocess
import socket
import os
import sys
import traceback
import time
# import rsa

class BTCon:
    """
    Bluetooth Connection class 

    Functionality:
        Connect to another bluetooth device
        Write or read data to/from the other pi
        Close connections    

    Attributes:
        other_name: hostname of the other pi (ie raspberrypi3 or raspberrypi4)
    """
    def __init__(self, other_name): #raises an AssertionError if the other_pi_name is this pi (you can't connect to yourself!)
        assert other_name != socket.gethostname() #check your other_pi_name!
        self.other_name = other_name
        self.other_addr = None
        self.send_sock = None
    
    def connect_as_host(self, port): #TODO change this to dynamic
        """
        Makes pi discoverable and waits for a connection to be made from the client
        The host can only receive data, but a pi can be both a host and a client

        Args:
            port: the port to connect on; must be the same as the client

        Returns:
            whether the connection was successful 

        Raises:
            None
        """
        subprocess.call(['sudo', 'hciconfig', 'hci0', 'piscan'])
        print("Set as discoverable")
        
        self.server_sock_receive= bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.server_sock_receive.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock_receive.bind(("",port))
        self.server_sock_receive.listen(port)

        self.client_sock_receive, other_info = self.server_sock_receive.accept()
        self.other_addr, port = other_info
        print(f"Accepted connection from {self.other_addr}")
        return True
    
    def connect_repeat_as_client(self, port, repeat):
        for i in range(repeat):
            try:
                if self.connect_as_client(port):
                    break
                print("not found")
            except:
                traceback.print_exc()
                print("error")  
    
    def connect_repeat_again_as_client(self, port, repeat):
        for i in range(repeat):
            try:
                time.sleep(0.5)
                if self.connect_again_as_client(port):
                    break
            except:
                traceback.print_exc()
                print("error")

    def connect_as_client(self, port): #TODO change to dynamic
        """
        Searches for discoverable devices and connects to any with a name matching other_name
        The client can only send data, but a pi can be both a host and a client

        Args:
            port: the port to connect on; must be the same as the host

        Returns:
            whether the connection was successful

        Raises:
            None
        """
        print("searching") 
        nearby_devices = bluetooth.discover_devices()
        print("Done searching")
        for addr in nearby_devices:
            print(f"Found address {addr} with name {bluetooth.lookup_name(addr)}")
            if self.other_name == bluetooth.lookup_name(addr) or bluetooth.lookup_name(addr) == None:#not good
                self.other_addr = addr
                break
       
        if self.other_addr is None:
            print(f"Could not find other device named {self.other_name}")#try again; this happens randomly sometimes
            return False 
        else:
            print(f"Found {self.other_name} with address {self.other_addr}")

        self.send_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.send_sock.connect(tuple((self.other_addr, port)))
        print(f"Connected send socket to {self.other_addr}")
        return True
    
    def connect_again_as_client(self, port):
        self.send_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.send_sock.connect(tuple((self.other_addr, port)))
        print(f"Connected send socket to {self.other_addr}")
        return True

    # def connect_and_gen_keys_host(self, port):
    #     self.connect_as_host(port)
    #     self.connect_as_client(port)
    #     self.pub_key, self.priv_key = rsa.newkeys(512)
    #     self.other_key = self.client_sock_receive.recv(512)
    #     self.send_sock.send(self.pub_key)
    #     print("established 2 way rsa connection as host")

    # def connect_and_gen_keys_client(self, port):
    #     self.connect_as_client(port)
    #     self.conenct_as_host(port)
    #     self.pub_key, self.priv_key = rsa.newkeys(512)
    #     self.send_sock.send(self.pub_key)
    #     self.other_key = self.client_sock_receive.recv(512)
    #     print("established 2 way rsa connection as client")
        
    def write_string(self, data):
        """
        Writes data to the host pi
        Can only be called if this pi has connected as a client
        Can be called before or after receive_string is called on the other pi

        Args:
            data: the string to send

        Returns:
            whether the string was successfully sent 

        Raises:
            AssertionError: raised if this pi has not established a connection as a client
        """
        assert self.send_sock is not None #connect before writing data
        size = sys.getsizeof(data)
        self.send_sock.send(size.to_bytes(64, "little"))
        self.send_sock.send(data)
        #print(f"wrote string with size {size}")
        return True

    def receive_string(self):
        """
        Recieves data from the client pi
        Can only be called if this pi has connected as a host
        Can be called before or after write_string is called on the other pi
        
        Args:
            None

        Returns:
            The written data as a string

        Raises:
            AssertionError: raised if this pi has not established a connection as a host
        """
        assert self.client_sock_receive is not None #connect before recieving data
        size = int.from_bytes(self.client_sock_receive.recv(1024), "little")
        data = self.client_sock_receive.recv(size)
        #print(f"received string of size {size}")
        return data.decode("UTF-8")
    
    def write_raw(self, data):
        assert self.send_sock is not None #connect before writing data
        self.send_sock.send(data)
        return True

    def receive_raw(self):
        assert self.client_sock_receive is not None #connect before receiving data
        return self.client_sock_receive.recv(1024).decode("UTF-8")

    def write_image(self, img_path):
        """
        Writes an image specified by img_path to the host pi
        Can only be called if this pi has connected as a client
        Can be called before or after receive_image is called on the other pi

        Args:
            img_path: The path of the image as a string; can be absolute or relative

        Returns:
            whether the image was successfully sent 

        Raises:
            AssertionError: raised if this pi has not established a connection as a client 
        """
        assert self.send_sock is not None #connect before writing data
        with open(img_path, "rb") as img:
            size = os.path.getsize(img_path)
            #print(f"writing image with size {size}")
            self.send_sock.send(size.to_bytes(16, "little"))
            self.send_sock.send(img.read(size))
            self.send_sock.send("done")
            self.send_sock.send("done2")#just in case
            img.close()
            print(f"sent image at {img_path}")
        return True

    def receive_image(self, img_path):
        """
        Recieves an image from the client pi
        Can only be called if this pi has connected as a host
        Can be called before or after write_image is called on the other pi
        
        Args:
            img_path: the path of where to write the received image to

        Returns:
            whether the image was successfully received 

        Raises:
            AssertionError: raised if this pi has not established a connection as a host
        """
        assert self.client_sock_receive is not None #connect before recieving data
        with open(img_path, "wb") as img:
            size = int.from_bytes(self.client_sock_receive.recv(1024), "little")
            buffer = self.client_sock_receive.recv(1024)
            data = buffer
            while buffer != "done".encode() or buffer != "done2".encode():
               buffer = self.client_sock_receive.recv(1024)#receives data in small chunks, it may be possible to do it all at once
               data += buffer
            if buffer == "done".encode()
                self.client_sock_receive.recv(1024)
            img.write(data)
            img.close()
            print(f"wrote image to {img_path}")
        return True

    def close_all_connections(self):
        """
        Closes both writing(client) and recieving(host) connections
        Can only be called if both a client and host connection has been made

        Args:
            None

        Returns:
            None

        Raises:
            AssertionError: raised if this pi has not established both a client and host connection
        """
        try:
            self.close_host()
        except:
            print("host not init")
        try:
            self.close_client()
        except:
            print("client not init")

    def close_host(self):
        """
        Closes the recieving(host) connection
        Can only be called if this pi has established a connection as a host

        Args:
            None

        Returns:
            None
        
        Raises:
            AssertionError: raised if this pi has not established a connection as a host
        """
        assert self.client_sock_receive is not None and self.server_sock_receive is not None #connect before closing
        self.server_sock_receive.close()
        self.client_sock_receive.close()

    def close_client(self):
        """
        Closes the writing(client) connection
        Can only be called if this pi has established a connection as a client

        Args:
            None

        Returns:
            None

        Raises:
            AssertionError: raised if this pi has not established a connection as a client
        """
        assert self.send_sock is not None #connect before closing 
        self.send_sock.close()
