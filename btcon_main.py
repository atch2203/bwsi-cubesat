from btcon import BTCon
import sys
import traceback
from git_push import commit_and_push 

type = sys.argv[1] 
other_pi = sys.argv[2]
first_time = sys.argv[3]
if type == "client":
    with open("/home/pi/log.txt", 'a') as f:
        f.write("before init")
        connection = BTCon(other_pi)
        if first_time == "True":
            connection.connect_as_host(1)
        connection.connect_repeat_as_client(1, 5)
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
    if first_time == "True":
        connection.connect_repeat_as_client(1, 5)
    connection.connect_as_host(1)
    print(connection.receive_string())
    connection.receive_image("test.jpg")
    connection.write_string("hi back")
    connection.close_all_connections()
    commit_and_push("test.jpg")
