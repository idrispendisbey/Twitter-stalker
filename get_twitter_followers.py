
# coding: utf-8

# In[6]:


import twitter, smtplib, pickle, json, datetime, os, time


# In[9]:


class TwitterInformer():
    def __init__(self):
        self.accounts = {}
        
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
        self.sleep = 5
        self.load()
        
    def add_account(self, account, save = True):
        if account in self.accounts:
            print ("Account is already added")
        else:
            self.accounts[account]=self.get_following(account)
            if save:
                self.save(backup = False)
    
    def add_accounts(self, accounts):
        check = 1
        for account in accounts:
            if account not in stalker.accounts:
                print(account)
                stalker.add_account(account)   
                check = 0
        if not check:
            self.save()
        return check
        
    def get_following(self, account):
        print ("Getting accounts followed by {}\n".format(account))
        following = self.api.GetFriends(screen_name=account)
        screen_names = []
        for user in following:
            screen_names.append(user.screen_name)
        time.sleep(self.sleep)
        return screen_names
        
    def save(self, backup = True):
        self.backup()
        print("Saving accounts \n")
        with open(self.filename, "wb") as handle:
            pickle.dump(self.accounts, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    def load(self):
        print("Loading saved accounts \n")
        if os.path.exists(self.filename):
            with open(self.filename, "rb") as handle:
                self.accounts = pickle.load(handle)
        else:
            print("Couldnt find primary saved data")
#         self.backup()

    def backup(self):
        print ("Backing up account content \n" )
        if not os.path.isdir("backups"):
            os.mkdir("backups")
        
        backup_filename = "backup-"+datetime.datetime.now().strftime("%Y%m%d-%M-%S")+".pickle"
        backup_filepath = os.path.join("backups",backup_filename)
        with open(backup_filepath, "wb") as handle:
            pickle.dump(self.accounts, handle, protocol=pickle.HIGHEST_PROTOCOL)

    
    def update(self):
        print("Updating following lists..\n")
        new = {}
        for account in self.accounts.keys():
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
    
    stalker = TwitterInformer()
    p1 = ["JihanWu", "rogerkver"]
    p2 = ["marsmensch", "notsofast", "growdigi", "needacoin", "cryptomocho"]
    p3 = ["cryptorangutang", "SalvaZenN", "CryptoCoyote", "SalvaZenN", "crypToBanger","Crypto_Twitt_r"]
    checklist = p1+p2+p3
    check = stalker.add_accounts(checklist)
    if check:
        stalker.update()

