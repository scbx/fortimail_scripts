import os, sys, re, csv
import xml.etree.ElementTree as ET
import xml.dom.minidom as xmd



#regular arguments
##directory to write database into
base_dir = 'testing/'
##location of the csv user data file
user_csv = 'config/dummy_data.csv'
##location of the user preference file
pref_file = 'config/pref'
##location of where to write the xml file
xml_config_name = base_dir + 'config_desc.xml'
#end regular arguments

#xml arguments
##defined as array
xml_dict = { 'version_major':'6',
'version_minor':'4',
'custom_number':'FW',
'build_number':'0427',
'branch_point':'427',
'patch_number':'2',
'device_model':'FE-VMW', }
#end xml arguments

def csv_data_parser(csv_file):
    '''
    takes in a CSV and returns a datamodel for later use

    :param csv_file: 
    Input a CSV file in the following format
    ---CONTENTS---
    whitelist,blacklist,mail
    sFEEFhfg@jnFDEdnf.com;sdFSDWEnrbg@fuhueh.com,uFDSfuhg@jGFERGu.com,user1@domain1.com
    suheruhfg@jnfhbdnf.com;sdjgfnrbg@fuhueh.com,ugfuhg@jugu.com,user2@domain2.com
    ---END CONTENTS---

    :return: 
    returns a dictionary data model for later use to build the fortimail database
    Will look similar to this
    ---CONTENT---
    domains = {'test.local':[{'user1':
                                  [{'whitelist':['domain1@test','domain2@test']},{'blacklist':['domain3@test','domain4@test']}],
                              'user2':
                                 [{'whitelist': ['domain1@test', 'domain2@test']},
                                  {'blacklist': ['domain3@test', 'domain4@test']}],
                             }],
            'domain2.test':[{'user1':
                                 [{'whitelist':['domain1@test','domain2@test']},{'blacklist':['domain3@test','domain4@test']}],
                             'user2':
                                 [{'whitelist': ['domain1@test', 'domain2@test']},
                                  {'blacklist': ['domain3@test', 'domain4@test']}],
                             }],
           'dom1.test': [{'user1':
                                 [{'whitelist': []},
                                  {'blacklist': []}],
                             'user2':
                                 [{'whitelist': []},
                                  {'blacklist': ['domain3@test', 'domain4@test']}],
                             }],
           }
    ---END CONTENT
    '''
    domains = {}
    try:
        with open(csv_file) as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames
            for row in reader:
                #extract whitelist
                whitelist = row[headers[0]].lower().split(';')
                #extract blacklist
                blacklist = row[headers[1]].lower().split(';')
                #extract mail domain
                target_domain = re.sub(r'^.*@(.*\..*)$', r'\1', row[headers[2]].lower())
                #extract username
                username = re.sub(r'(^.*)@.*\..*$', r'\1', row[headers[2]].lower())
                if target_domain not in domains:
                    #if domain isn't in datamodel then add
                    domains[target_domain] = [{}]
                #add user to domain
                domains[target_domain][0].update({username: [{}]})
                # append whitelist to user
                domains[target_domain][0][username][0].update({'whitelist': whitelist})
                # append blacklist to user
                domains[target_domain][0][username][0].update({'blacklist': blacklist})
        #return datamodel
        return domains
    except OSError:
        print('csv file may not exist')
        exit(1)
        
def build_fortimail_db(base_dir, domains, pref_file):
    '''
    Takes in a base directory, an array of user data and a preference file to generate a database for fortimail

    :param base_dir:
    This will be the base directory to build the database in
    :param domains:
    This will be the dictionary file returned by the function csv_data_parser
    :param pref_file:
    This will be the preference file that will be used for generating the user config
    :return:
    Builds a database in the specified base_dir directory
    '''
    try:
        os.mkdir(base_dir + 'user_conf')
        conf_dir = base_dir + 'user_conf/'
    except OSError:
        conf_dir = base_dir + 'user_conf/'
    for domain in domains:
        # Try make a directory for the domain and define a base domain_dir
        try:
            domain_dir = conf_dir + domain + '/'
            os.mkdir(conf_dir + domain)
        # Directory already exists, define variable and continue
        except OSError:
            domain_dir = conf_dir + domain + '/'
            domain_dir = str(domain_dir)
            pass
        for userlist in domains[domain]:
            # For the individual user within the list of users
            for user in userlist:
                # define user dir variable
                user_dir = domain_dir + user + '/'
                # Try create the user dir directory
                try:
                    os.mkdir(user_dir)
                # User Dir might already exist
                except OSError:
                    pass
                    # print('couldnt make user dir')
                # define the preference file variable
                preffile = user_dir + 'pref'
                # Read the contents of the example preference file
                with open(pref_file, "r") as f:
                    # Read all lines
                    lines = f.readlines()
                    # Open user preference file
                    with open(preffile, "w") as f1:
                        # Write contents of example preference file into new preference file
                        f1.writelines(lines)

                # iterate over all the lists on the users
                for lists in userlist[user]:
                    # print(lists)
                    # For each list within the lists
                    for entry in lists:
                        listfile = user_dir + entry
                        # refresh file as next iteration appends
                        f = open(listfile, "w")
                        # write nothing
                        f.write("")
                        # close file
                        f.close()
                        # iterate over list entry and write content
                        if entry == 'whitelist':
                            for item in lists['whitelist']:
                                f = open(listfile, "a")
                                # write new line as well
                                f.write(item + "\n")
                                # close file
                                f.close()
                        if entry == 'blacklist':
                            for item in lists['blacklist']:
                                f = open(listfile, "a")
                                # write new line as well
                                f.write(item + "\n")
                                # close file
                                f.close()


def build_fortimail_xml_config(domains, input_dict):
    '''
    Takes in domains dictionary variable and xml config dictionary variable to generate an XML config declaraction file
    for the fortimail user db

    :param domains:
    input the domains dictionary generated by the csv_data_parser function
    :param input_dict:
    dictionary variables defined to generate XML config based of fortimail model
    :return:
    returns XML data as a single string variable
    '''
    data = ET.Element('fm_config')
    data.set('version', '1.0')
    data.set('name', 'fortimail')
    buildinfo = ET.SubElement(data, 'buildinfo')
    for i in input_dict:
        entry = ET.SubElement(buildinfo, i)
        entry.text = input_dict[i]
    # End building the Build info Declaration Section
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
    return data


def write_fortimail_xml_config(xml_config, xml_config_name):
    '''
    takes in an xml configuration variable, makes the xml config pretty then
        writes the xml configuration to a file

    :param xml_config:
    xml configuration of the fortimail user database - config_desc.xml

    :param xml_config_name:
    file name of where to write the xml configuration
    :return:
    '''
    mydata = ET.tostring(xml_config)
    mydatastr = mydata.decode('ascii')
    # import to file as xml parser take file as argument
    myfile = open('temp_file', "wt")
    myfile.write(mydatastr)
    myfile.close()

    dom = xmd.parse('temp_file')
    pretty_xml = dom.toprettyxml()

    myfile = open(xml_config_name, "wt")
    myfile.write(pretty_xml)
    myfile.close()
    # remove the temp file
    os.remove('temp_file')

if __name__ == '__main__':
    #build domains - domain - user - whitelist & blacklist array and return data as variable
    domains = csv_data_parser(user_csv)

    #Use domain array to build database
    build_fortimail_db(base_dir, domains, pref_file)

    #use domain array and xml dictionary variables to generate xml configuration and return xml configuration as variable
    xml_config = build_fortimail_xml_config(domains, xml_dict)
    #write xml variable t
    write_fortimail_xml_config(xml_config, xml_config_name)
