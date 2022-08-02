from .btcon import BTCon
import sys
import traceback
import time

def bt_selftest(other_pi, first_time):
    with open("/home/pi/log.txt", 'a') as f:
        f.write("before init\n")
        connection = BTCon(other_pi)
        if first_time == "True":
            connection.connect_as_host(1)
        time.sleep(1)
        connection.connect_repeat_again_as_client(1, 5)
        f.write("done\n")
        connection.write_string("hi")
        f.write("wrote hi\n")
        if first_time == "True":
            f.write(f"received {connection.receive_string()}")
        return connection
   
if __name__ == "__main__":
    otherpi = sys.argv[1]
    firsttime = sys.argv[2]
    bt_selftest(otherpi, firsttime).close_all_connections()
