import telnetlib
import time
import re
import threading

# ophalen bestand ip lijst
with open('ip.txt') as fh:
    fstring = fh.readlines()
pattern = re.compile(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")
items = []
for line in fstring:
    items.append(pattern.search(line)[0])
print(items)

# ophalen tftp server
with open('tftp.txt', 'r') as f:
    tftp = (f.read())
    print("Tftp server is: " + tftp)

user = "root"
password = ""
response = ""


def main():
    for ip in items:
        print("Current ip: " + ip)
        tn = telnetlib.Telnet(ip)

        # telnet verbinding inloggen
        tn.read_until(b"login: ")
        tn.write(user.encode('ascii') + b"\n")
        if password:
            tn.read_until(b"Password: ")
            tn.write(password.encode('ascii') + b"\n")
        time.sleep(1)
        ipdone.close()

        tn.write(b"tftp -gr  blup.sh " + tftp.encode('ascii') + b"\n")
        time.sleep(1)
        tn.write(b"chmod 0777 blup.sh\n")
        time.sleep(1)
        tn.write(b"echo tftphost=172.16.201.64 > /tmp/serverparams.conf\n")
        tn.read_sb_data().decode('ascii')
        time.sleep(1)
        tn.write(b"./blup.sh\n")
        time.sleep(1)
        print(tn.read_sb_data().decode('ascii'))
        tn.write(b"exit\n")
        tn.read_all()
        print(tn.read_all())  # .decode('ascii'))

    else:
        print(ip + " is al gedaan")


def process(items, start, end):
    print(items)
    for item in items[start:end]:
        try:
            main(item)
        except Exception:
            print('error with item')


def split_processing(items, num_splits=4):
    split_size = len(items) // num_splits
    threads = []
    for i in range(num_splits):
        start = i * split_size
        end = None if i + 1 == num_splits else (i + 1) * split_size
        threads.append(
            threading.Thread(target=process, args=(items, start, end)))
        threads[-1].start()

    for t in threads:
        t.join()
main()