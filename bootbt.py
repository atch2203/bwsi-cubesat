from btcon import BTCon
import sys
import traceback

other_pi = sys.argv[1]
first_time = sys.argv[2]
with open("/home/pi/log.txt", 'a') as f:
    f.write("before init")
    connection = BTCon(other_pi)
    if first_time == "True":
        connection.connect_as_host(1)
    connection.connect_repeat_as_client(1, 5)
    f.write("done")
    connection.write_string("hi")
    f.write("wrote hi")
    f.write("wrote image")
    f.write(f"received {connection.receive_string()}")
    connection.close_all_connections()
