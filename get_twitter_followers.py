
# coding: utf-8

# In[1]:


import twitter, smtplib, pickle, json, datetime, os, time


# In[1]:


class TwitterInformer():
    def __init__(self):
        self.accounts = {}
        self.start = time.time()
        with open('config.env', 'r') as file:  
            config = json.load(file)
            
        self.filename = config["filename"]
        self.consumer_key = config["consumer_key"]
        self.consumer_secret = config["consumer_secret"]
        self.access_token = config["access_token"]
        self.access_token_secret = config["access_token_secret"]
        self.api = twitter.Api(consumer_key=self.consumer_key, 
                               consumer_secret=self.consumer_secret,
                               access_token_key=self.access_token,
                               access_token_secret=self.access_token_secret,
                               sleep_on_rate_limit=True
                              )
        self.gmail = config["gmail"]
        self.gmail_pass = config["gmail_pass"]
        self.recipient = config["recipient"]
        self.sleep = 300
        self.requested = []
        self.recent=[]
        self.load()
        self.get_friends()

        
    def get_friends(self):
        print ("Fetching friends")
        self.friends = [u.name for u in self.api.GetFriends()]
        for i in self.requested:
            if i in self.friends:
                print(i,"has approved your friend request")
                self.requested.remove(i)
        print()
        
    def add_account(self, account, save = True):
        if account in self.accounts:
            print ("Account is already added")
        else:
            following = self.get_following(account)
            if following:
                self.accounts[account]= following
                self.recent.append(account)
            if save:
                self.save(backup = False)
    
    def add_accounts(self, accounts):
        for account in accounts:
            if account not in stalker.accounts and account not in self.requested:
                print(account)
                stalker.add_account(account)   
                check = 0
        self.save()
        
    def get_following(self, account):
        
        if account not in self.requested:
            try:
                print ("Getting accounts followed by {}".format(account))
                following = self.api.GetFriends(screen_name=account)
                screen_names = []
                for user in following:
                    screen_names.append(user.screen_name)        

                time.sleep(self.sleep)
                return screen_names
            except:
                print("Couldnt fetch account probably due to protection. {} needs to approve friendship request".format(account))
                print("Befriending:",account)
                try:
                    self.api.CreateFriendship(screen_name=account, follow = False, retweets = False)
                    self.requested.append(account)
                except:
                    self.requested.append(account)
                print("Sent a friendship request and added to requested list")
                return None                
        else:
            print("Waiting for friendship acceptance")
            return None
        
        
#         if account not in self.friends and account not in self.requested:
#             print("Befriending:",account)
#             try:
#                 self.api.CreateFriendship(screen_name=account, follow = False, retweets = False)
#             except:
#                 self.requested.append(account)
#             print("Sent a friendship request")
#             return None
#         elif account in self.requested:
#             print("Couldnt fetch account probably due to protection. {} needs to approve friendship request".format(account))
#             return None
#         else:
#             following = self.api.GetFriends(screen_name=account)
#             screen_names = []
#             for user in following:
#                 screen_names.append(user.screen_name)        

#             time.sleep(self.sleep)
            return screen_names
        
    def save(self, filename = "", backup = True):
        if backup:
            self.backup()
        print("Saving accounts \n")
        
        if filename == "":
            filename = self.filename
            
        with open(filename, "wb") as handle:
            pickle.dump([self.accounts, self.requested], handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    def load(self):
        print("Loading saved accounts \n")
        if os.path.exists(self.filename):
            with open(self.filename, "rb") as handle:
                [self.accounts, self.requested] = pickle.load(handle)
        else:
            print("Couldnt find primary saved data")
#         self.backup()

    def backup(self):
        print ("Backing up account content \n" )
        if not os.path.isdir("backups"):
            os.mkdir("backups")
        
        backup_filename = "backup-"+datetime.datetime.now().strftime("%Y%m%d-%M-%S")+".pickle"
        backup_filepath = os.path.join("backups",backup_filename)
        
        self.save(filename=backup_filepath, backup = False)

    
    def update(self):
        print("Updating following lists..\n")
        new = {}
        for account in self.accounts.keys():
            if account in self.recent:
                continue
            friends = self.get_following(account)
            for friend in friends:
                if friend not in self.accounts[account]:
                    print("New friend:",friend)
                    
                    if account not in new.keys():
                        new[account]=[]
                    new[account].append(friend)
                    
#                     if friend in new.keys():
#                         new[friend].append(account)
#                     else:
#                         new[friend]=[account]
            print()
            self.accounts[account] = friends
#             time.sleep(self.sleep)
#         print("News:")
#         print(new)
        self.send_mail(new)
        self.save()
        
    def send_mail(self, news):
        print("Sending mail.. \n")
        if news:
            subject = "New Friends"
            text = "New Friends \n\n"
            for i in news.keys():
                text += i+" :\n"
                for j in news[i]:
                    text += "https://twitter.com/"+ j +"\n"
                text += "\n"
        else:
            subject = "Nada"
            text = "No new friends"
#         print("Text:")
#         print(text)
        text += "\nTook {:.2f} seconds".format(time.time()-self.start)
        message = 'From: {}\nTo: {}\nSubject: {}\n\n{}'.format(self.gmail, self.recipient, subject, text)
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(self.gmail, self.gmail_pass)
        server.sendmail(self.gmail, self.recipient, message)
        server.close()
        print("Mail content:")
        print ("\n-------\n")
        print (message)
        print ("\n-------\n")
        print ('Email sent!')


# In[ ]:


if __name__ == '__main__':
    print(datetime.datetime.now())
    stalker = TwitterInformer()
    p1 = ["JihanWu", "rogerkver"]
    p2 = ["marsmensch", "notsofast", "growdigi", "needacoin", "cryptomocho", "bitcoin_dad", "jiucrypto", "LowCapWizard"]
    p3 = ["cryptorangutang", "SalvaZenN", "CryptoCoyote", "SalvaZenN", "crypToBanger","Crypto_Twitt_r"]
    checklist = p1+p2+p3
    stalker.add_accounts(checklist)
    stalker.update()

