from btcon import BTCon
import sys
import traceback

def main():
    other_pi = sys.argv[1]
    first_time = sys.argv[2]
    with open("/home/pi/log.txt", 'a') as f:
        f.write("before init\n")
        connection = BTCon(other_pi)
        if first_time == "True":
            connection.connect_as_host(1)
        connection.connect_repeat_as_client(1, 5)
        f.write("done\n")
        connection.write_string("hi")
        f.write("wrote hi\n")
        f.write(f"received {connection.receive_string()}")
        connection.close_all_connections()

if __name__ == "__main__":
    main()
