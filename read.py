import os

read_fd = os.getenv("read_fd")
read_file = os.fdopen(int(read_fd), mode='rt', encoding='utf-8')
msg = read_file.read()
read_file.close()
print("message from parent:", msg)
