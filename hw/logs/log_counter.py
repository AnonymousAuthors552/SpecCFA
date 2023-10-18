import os
import sys

def main():
    direct = sys.argv[1]
    log_size_dict = dict()
    total_size = 0
    
    os.chdir(direct)
    directory = os.listdir()
    for entry in directory:
        if (os.path.isfile(entry)):
            fp = open(entry, "r")
            lines = fp.readlines()
            addrs = lines[-1]
            print(addrs)
            addrs = addrs.strip()
            total_size += int(addrs)
            log_size_dict[entry] = addrs
    
    # print(log_size_dict)
    print(direct+": "+str(total_size))
        

if __name__ == "__main__":
    main()
