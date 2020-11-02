import os, sys, re
import xml.etree.ElementTree as ET
import xml.dom.minidom as xmd

# Example Datamodel
# domains = {'test.local':[{'user1':
#                                  [{'whitelist':['domain1@test','domain2@test']},{'blacklist':['domain3@test','domain4@test']}],
#                              'user2':
#                                  [{'whitelist': ['domain1@test', 'domain2@test']},
#                                   {'blacklist': ['domain3@test', 'domain4@test']}],
#                              }],
#             'domain2.test':[{'user1':
#                                  [{'whitelist':['domain1@test','domain2@test']},{'blacklist':['domain3@test','domain4@test']}],
#                              'user2':
#                                  [{'whitelist': ['domain1@test', 'domain2@test']},
#                                   {'blacklist': ['domain3@test', 'domain4@test']}],
#                              }],
#            'dom1.test': [{'user1':
#                                  [{'whitelist': []},
#                                   {'blacklist': []}],
#                              'user2':
#                                  [{'whitelist': []},
#                                   {'blacklist': ['domain3@test', 'domain4@test']}],
#                              }],
#            }


### Base Variable Statements
base_dir = 'ssh_development/'
xml_config = base_dir + 'config_desc.xml'
pref_src = 'pref.txt'
csv_file = 'dummy_data.csv'
domains = {} #DECLARE DOMAINS VARIABLE
### End Base Variable Statements

with open(csv_file, 'r') as csv:
    #import csv file of users
    csv_lines = csv.readlines()
    #iterate over lines
    for line in csv_lines:
        #remove returns
        line = line.rstrip()
        line = line.lower()
        #split line into array/ three entries
        entries = line.split(',')
        #extract whitelist and convert to array
        whitelist = entries[0].split(';')
        #create blacklist and convert to array
        blacklist = entries[1].split(';')
        #extract user email
        whole_email = entries[2]
        #strip domain from user email for domain creation
        target_domain = re.sub(r'^.*@(.*\..*)$', r'\1', entries[2])
        #strip username from email
        username = re.sub(r'(^.*)@.*\..*$', r'\1', whole_email)
        #If the target domain isn't in the current domain array, create it
        if target_domain not in domains:
            domains[target_domain] = [{}]
        #Append user to domain
        domains[target_domain][0].update({username:[{}]})
        #append whitelist to user
        domains[target_domain][0][username][0].update({'whitelist': whitelist})
        #append blacklist to user
        domains[target_domain][0][username][0].update({'blacklist': blacklist})

#print(domains)

#Start building user database
#Try make the base user directory and define a config base directory
try:
    os.mkdir(base_dir + 'user_conf')
    conf_dir = base_dir + 'user_conf/'
#If the directory already exists;
except OSError:
    conf_dir = base_dir + 'user_conf/'
    print('dir exists')
#For each domain within the datamodel
for domain in domains:
    # Try make a directory for the domain and define a base domain_dir
    try:
        domain_dir = conf_dir + domain + '/'
        os.mkdir(conf_dir + domain)
    #Directory already exists, define variable and continue
    except OSError:
        domain_dir = conf_dir + domain +'/'
        domain_dir = str(domain_dir)
        pass
        #print('dir exists')
    #For the userlist within the domain
    for userlist in domains[domain]:
        #For the individual user within the list of users
        for user in userlist:
            #define user dir variable
            user_dir = domain_dir + user +'/'
            #Try create the user dir directory
            try:
                os.mkdir(user_dir)
            #User Dir might already exist
            except OSError:
                pass
                # print('couldnt make user dir')
            #define the preference file variable
            preffile = user_dir + 'pref'
            #Read the contents of the example preference file
            with open(pref_src, "r") as f:
                #Read all lines
                lines = f.readlines()
                #Open user preference file
                with open(preffile, "w") as f1:
                    #Write contents of example preference file into new preference file
                    f1.writelines(lines)

            #iterate over all the lists on the users
            for lists in userlist[user]:
                #print(lists)
                #For each list within the lists
                for entry in lists:
                    listfile = user_dir + entry
                    #refresh file as next iteration appends
                    f = open(listfile, "w")
                    #write nothing
                    f.write("")
                    #close file
                    f.close()
                    #iterate over list entry and write content
                    if entry == 'whitelist':
                        for item in lists['whitelist']:
                            f = open(listfile, "a")
                            #write new line as well
                            f.write(item + "\n")
                            #close file
                            f.close()
                    if entry == 'blacklist':
                        for item in lists['blacklist']:
                            f = open(listfile, "a")
                            #write new line as well
                            f.write(item + "\n")
                            #close file
                            f.close()


### Define XML variables
version_major_arg = '6'
version_minor_arg = '4'
custom_number_arg = 'FW'
build_number_arg = '0427'
branch_point_arg = '427'
patch_number_arg = '2'
device_model_arg = 'FE-VMW'
### End Defining XML Variables

#Start building the Build Info declaration Section
data = ET.Element('fm_config')
data.set('version', '1.0')
data.set('name', 'fortimail')

buildinfo = ET.SubElement(data, 'buildinfo')

version_major = ET.SubElement(buildinfo, 'version_major')
version_major.text = version_major_arg

version_minor = ET.SubElement(buildinfo, 'version_minor')
version_minor.text = version_minor_arg

custom_number = ET.SubElement(buildinfo, 'custom_number')
custom_number.text = custom_number_arg

build_number = ET.SubElement(buildinfo, 'build_number')
build_number.text = build_number_arg

branch_point = ET.SubElement(buildinfo, 'branch_point')
branch_point.text = branch_point_arg

patch_number = ET.SubElement(buildinfo, 'patch_number')
patch_number.text = patch_number_arg

device_model = ET.SubElement(buildinfo, 'device_model')
device_model.text = device_model_arg
#End building the Build info Declaration Section

#
config = ET.SubElement(data, 'config')
config.set('name', 'user_conf')
for entry in domains:
    domain = ET.SubElement(config, 'domain')
    domain.set('name', entry)
    for userlist in domains[entry]:
        for user in userlist:
            item1 = ET.SubElement(domain, 'item')
            item1.set('name', 'user-blacklist')
            item1.set('type', 'user')
            item1.set('user', user)
            item2 = ET.SubElement(domain, 'item')
            item2.set('name', 'user-whitelist')
            item2.set('type', 'user')
            item2.set('user', user)
            item3 = ET.SubElement(domain, 'item')
            item3.set('name', 'user-preference')
            item3.set('type', 'user')
            item3.set('user', user)

mydata = ET.tostring(data)
mydatastr = mydata.decode('ascii')
#import to file as xml parser take file as argument
myfile = open('temp_file', "wt")
myfile.write(mydatastr)
myfile.close()

dom = xmd.parse('temp_file')
pretty_xml = dom.toprettyxml()

myfile = open(xml_config, "wt")
myfile.write(pretty_xml)
myfile.close()
