from btcon import BTCon
import sys

with open("/home/pi/test.txt", 'a') as f:
    f.write("It worked!")

print("connect as client or host")
type = sys.argv[1] 
print("what is the hostname of the other pi?")
other_pi = sys.argv[2]
if type == "client":
    connection = BTCon(other_pi)
    for i in range(5):
        try:
            connection.connect_as_client(1)
            break
        except:
            print("error")
    connection.write_string("hi")
    connection.write_image("saturnpencil.jpg")
    connection.connect_as_host(1)
#    print(f"received {connection.receive_string()}")
    connection.close_all_connections()
else:
    connection = BTCon(other_pi)
    connection.connect_as_host(1)
#    print(connection.receive_string())
#    connection.receive_image("test.jpg")
    connection.connect_as_client(1)
    connection.write_string("hi back")
    connection.close_all_connections()
