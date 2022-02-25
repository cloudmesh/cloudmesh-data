import os


def random_file(filename, size):
    """
    generate a binary with given size
    :param filename: the filename
    :param size: the size in bytes
    :return: void
    """
    s = get_real_size(size)
    with open(filename, 'wb') as f:
        f.write(os.urandom(s))
    print(f'Created random file of size: {size}')


def ascii_file(filename, size, c="0"):
    """
    generate an ascii file with given size that only contains the char c

    :param filename: the filename
    :type filename:
    :param size: the size in bytes
    :type size:
    :param c:
    :type c:
    :return: void
    :rtype: void
    """
    """
    
    """
    s = get_real_size(size)
    with open(filename, 'wb') as f:
        f.write(s * b'{c}')
    print(f'Created file with {c} of size: {size}')


def get_real_size(size):
    KB = int(1024)
    MB = int(KB ** 2)  # 1,048,576
    GB = int(KB ** 3)  # 1,073,741,824
    TB = int(KB ** 4)  # 1,099,511,627,776

    if "KB" in size:
        s = size.replace("KB", "")
        s = int(s) * KB
    elif "MB" in size:
        s = size.replace("MB", "")
        s = int(s) * MB
    elif "GB" in size:
        s = size.replace("GB", "")
        s = int(s) * GB
    elif "TB" in size:
        s = size.replace("TB", "")
        s = int(s) * TB
    else:
        s = int(size)
    return s
