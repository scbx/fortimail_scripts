import re
my_array = []
def extract_domains(entry, array):
    entry = entry.rsplit('\n')
    counter = 0
    for line in entry:
        line = re.sub(r'^.*\"@?(.*\..*)\"$', r'*@\1', line)
        if line in array:
            counter += 1
            print(line +' already in array')
            continue
        array.append(line)
    print('duplicates found in current list: ' + str(counter))
    print()


def build_email_address_groups(entries, group_name):
    print('config profile email-address-group')
    print('edit '+ group_name)
    print('config member')
    for entry in entries:
        print('edit '+entry)
        print('next')

f = open("fl.txt", "r")
f = f.read()

extract_domains(f, my_array)
build_email_address_groups(my_array, 'GovLink')
