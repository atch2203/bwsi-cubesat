from btcon import BTCon
import sys
import traceback

with open("/home/pi/test.txt", 'a') as f:
    f.write("It worked!")

print("connect as client or host")
type = sys.argv[1] 
print("what is the hostname of the other pi?")
other_pi = sys.argv[2]
if type == "client":
    with open("/home/pi/log.txt", 'a') as f:
        f.write("before init")
        connection = BTCon(other_pi)
        connection.connect_as_host(1)
        for i in range(5):
            f.write(f"take {i}")
            try:
                if connection.connect_as_client(1):
                    break
                print("not found")
            except:
                traceback.print_exc()
                print("error")
        f.write("done")
        connection.write_string("hi")
        f.write("wrote hi")
        print("wrote hi")
        connection.write_image("/home/pi/CHARMS/saturnpencil.jpg")
        f.write("wrote image")
        print(f"received {connection.receive_string()}")
        connection.close_all_connections()
else:
    connection = BTCon(other_pi)
    connection.connect_as_client(1)
    connection.connect_as_host(1)
    print(connection.receive_string())
    connection.receive_image("test.jpg")
    connection.write_string("hi back")
    connection.close_all_connections()
