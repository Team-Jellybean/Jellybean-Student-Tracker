from selenium import webdriver
from bs4 import BeautifulSoup
import csv
import time
import socket
import sys
import requests
driver= webdriver.Chrome()
class File:

    # Variables to store filename, old ratings and new ratings respectively 
    # for the File object created.
    def __init__(self,x):
        self.file_name = x
        self.old_ratings = []
        self.new_ratings = []

    ''' Function to fetch usernames from the CSV file and
        populate the 'old_ratings' list with lists of
        [Name, Username (handle), Old Rating].Opens
        the given 'file_name' if exists, otherwise
        throws a FileNotFoundError. If the file is
        present, all the usernames are appended to the
        'old_ratings' list. The dictionary 'usernames'
        is used to store the usernames and the corresponding
        ratings. Initially, it is assigned to 'None'
        and later it will be used to sort the ratings
        in descending order.'''
    def fetch_usernames(self):
        usernames = {}
        
        try:
            with open(self.file_name, 'r') as csvfile:
                csvreader = csv.reader(csvfile)
                
                for x in csvreader:
                    self.old_ratings.append(x)
                    usernames[x[1]] = None
        
        except FileNotFoundError:
            print('File does not exist!!')
            sys.exit(1)
        
        return usernames
    
    ''' This function populates the 'new_ratings' list.
        It sorts the 'new_ratings' dictioanry in descending
        order based on the value i.e. ratings. It then
        populates the 'new_ratings' list with lists of
        [Name, Username (handle), New Rating].'''
    def populate_new_ratings(self,new_ratings):
        sorted_ratings = sorted(new_ratings.items(),key = lambda kv:(kv[1],kv[0]))
        sorted_ratings.reverse()
        for user_name,new_rating in sorted_ratings:
            temp = []
            for old_rating in self.old_ratings:
                if user_name == old_rating[1]:
                    temp.append(old_rating[0])
                    temp.append(user_name)
                    temp.append(new_rating)
                continue
            self.new_ratings.append(temp)

    ''' This function writes the new ratings of the
        users sorted in descending order by ratings
        to the 'file_name'. It preserves the old order
        of Name, Username (handle), Rating in the CSV file.'''    
    def write_new_ratings(self):

        with open(self.file_name, 'w') as csv_file: 
            csvwriter = csv.writer(csv_file)
            csvwriter.writerows(self.new_ratings)

class Internet:
    
    # Variable to store the url of website.
    def __init__(self):
        self.url = 'www.codechef.com'
    
    def initial_setup(self):
        self.check_internet_connection()
        self.check_server_status()
    
    ''' This function is used to check if the computer is 
        connected to Internet. First, it creates a socket
        by using the URL provided. The try-except block
        is used to catch the gaierror and ConnectionRefusedError
        respectively.'''
    def check_internet_connection(self):
        
        try:
            host = socket.gethostbyname(self.url)
            s = socket.create_connection((host, 80), 2)
            s.close()
        
        except socket.gaierror:
            print("Check your Internet connection!!")
            sys.exit(0)
        
        except ConnectionRefusedError:
            print("Connection Refused!")
            sys.exit(1)
    
    ''' After checking if the computer is connected to internet,
        this function is used to check if the server responding
        to the requests.'''
    def check_server_status(self):

        try:
            final_url = 'http://' + self.url
            temp = requests.head(final_url).status_code

        except requests.exceptions.ConnectionError:
            print("Server is not up!!")
            sys.exit(1)

''' This function scrapes the website and gets the new ratings of
    the 'user_names' passed as a parameter. It creates an instance of 
    Chrome webdriver, then iterates through the user_names dictionary
    and fetches the corresponding profile page of the user, scrapes
    the webpage for the rating and populates it into the user_names
    dictioanry.'''
def get_new_ratings(user_names):
    browser = webdriver.Chrome()
    base_url = "http://www.codechef.com/users/"

    for user_name in user_names:
        final_url = base_url + user_name
        browser.get(final_url)

        try:
            soup = BeautifulSoup(browser.page_source,features="html.parser")
            div = soup.find('div',attrs = {'class':'rating-number'})
            user_names[user_name] = div.text
            time.sleep(2)
        
        except AttributeError:
            print("User {} does not exist!!".format(user_name))
            user_names[user_name] = "-1"
            continue
    
    return user_names

# Driver function.
if __name__ == '__main__':

    file_url = "Codechef-Ratings.csv"
    file = File(file_url)
    Internet.initial_setup(Internet())
    user_names = file.fetch_usernames()
    
    new_ratings = get_new_ratings(user_names)
    
    file.populate_new_ratings(new_ratings)
    file.write_new_ratings()
