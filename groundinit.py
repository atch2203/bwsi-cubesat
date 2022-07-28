from btcon import BTCon
import sys
import traceback
from git_push import commit_and_push 
import time

def main():
    start_time = time.time()
    other_pi = sys.argv[1]
    first_time = sys.argv[2]
    connection = BTCon(other_pi)
    if first_time == "True":
        connection.connect_repeat_as_client(1, 5)
    connection.connect_as_host(1)
    print(connection.receive_string())
    if first_time == "True":
        connection.write_string("hi back")
    connection.close_all_connections()
    print(time.time() - start_time)

if __name__ == "__main__":
    main()
