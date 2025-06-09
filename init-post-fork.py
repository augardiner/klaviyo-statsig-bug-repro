import os
import sys
import time

from statsig_python_core import Statsig, StatsigOptions

def initialize_statsig():
    options = StatsigOptions()
    # Use a dummy key and local mode to avoid network
    options.disable_network = True
    client = Statsig.new_shared("dummy-key", options)
    client.initialize().wait()

def main():
    print("Forking...")
    pid = os.fork()
    if pid == 0:
        # Child process
        print("Initializing Statsig in child...")
        initialize_statsig()
        print("In child process, sleeping...")
        time.sleep(3)
        print("Child done.")
        sys.exit(0)
    else:
        # Parent process
        print("In parent process, waiting for child...")
        os.waitpid(pid, 0)
        print("Parent done.")

if __name__ == "__main__":
    main()
    print("\nScript complete.")
