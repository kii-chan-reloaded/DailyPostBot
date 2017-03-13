#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  DailyThreadBot.py
#  
#  Copyright 2017 Keaton Brown <linux.keaton@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

########################################################################
#                                                                      #
#    Definitions                                                       #
#                                                                      #
########################################################################

#### Startup

def loadConfig(myPath):
    """
    loads the config file, if anything is empty, cause panic
    """
    print("Loading configuration from file...")
    creds = configparser.RawConfigParser()
    creds.optionxform = lambda option: option
    creds.read(myPath+"configuration.ini")
    print("Configuration file read. Checking for usable values.")
    if not creds.sections():
        print("No sections found in configuration file. Aborting!")
        raise Exception
    if sorted(creds.sections()) != sorted(configSections):
        print("Not all sections found. Aborting!")
        raise Exception
    print("Found sections. Checking for values...")
    for item in creds.sections():
        if not [thing[1] for thing in creds[item].items()]:
            print("No values found for section "+item+".")
            while True:
                confirm = input("Proceed anyway? Proceeding without "
                                "certain values might cause errors down "
                                "the road (y/n)\n==> ")
                if confirm.lower() == "y":
                    print("Ignoring empty section.")
                    break
                elif confirm.lower() == "n":
                    print("Aborting!")
                    raise Exception
                else:
                    print("Confirmation failed.Restarting entry.")
        print("Found values for section "+item)
    print("Configuration seems usable. Using "+myPath+"configuration.ini")
    return creds

def makeCreds(myPath):
    print("Either this is the first time this script is being run, or there "
          "was an error reading the config file. You will now be walked "
          "through obtaining all the credentials this bot needs in order "
          "to function.")
    config = configparser.ConfigParser()
    config.optionxform = lambda option: option
    ############################################################## Daily
    print("First, we will create the daily thread post body.")
    while True:
        try:
            with open(myPath+"dailyPost.md","r") as dailyPost:
                DP = dailyPost.read()
                if DP:
                    print("__________\n\n"+DP+"\n\n__________")
                    confirm = input("Is this the correct markdown for the daily post? "
                                    "(y/n)\n(No will erase the dailyPost.md file)\n==> ")
                    if confirm.lower() == "y":
                        print("Using the markdown from disk")
                        break
                    else:
                        print("Confirmation failed. Erasing and starting fresh.")
                        raise Exception
        except:
            input("Press enter to overwrite '"+myPath+"dailyPost.md' if it exists.")
            with open(myPath+"dailyPost.md","w") as dailyPost:
                dailyPost.write("")
            print("A blank file has been written at '"+myPath+"dailyPost.md'. "
                  "Open this file in any text editor, then type the markdown you "
                  "wish to use for the daily post.\n"
                  "Note: This should only be the post body. We will enter the post "
                  "title later.")
            input("Press enter when you have saved 'dailyPost.md'")
    ############################################################# Reddit
    print("Next, we will get the bot's Reddit information.")
    input("Press enter to continue... ")
    print(" 1) Go to https://www.reddit.com/prefs/apps and sign in with your "
          "bot account.\n"
          " 2) Press the 'create app' button, then enter the following :\n\n"
          "    Name: DailyThreadBot (or another name if you so wish)\n"
          "    App type: script\n"
          "    description: (leave this blank or enter whatever you wish)\n"
          "    about url: https://github.com/WolfgangAxel/DailyThreadBot\n"
          "    redirect url: http://127.0.0.1:65010/authorize_callback\n\n"
          " 3) Finally, press the 'create app' button.")
    input("Press enter to continue... ")
    print("Underneath the name of the app, there should be a string of letters and numbers.\n"
          "That is the bot's client-id.\n"
          "The bot's secret is displayed in the table.")
    redCreds = {}
    for short,thing in [["u","username"],["p","password"],["c","client-id"],["s","secret"]]:
        while True:
            value = input("Please enter the bot's "+thing+":\n==> ")
            confirm = input("Is '"+value+"' correct? (y/n)\n==> ")
            if confirm.lower() == "y":
                redCreds[short] = value
                break
            print("Confirmation failed. Restarting entry")
    ############################################################### Misc
    print("Almost done! Just a few more items to define.")
    input("Press enter to continue... ")
    mscCreds = {}
    for variable,question in [ ["mySub","Enter the name of your subreddit."],
                               ["botMaster","Enter your personal Reddit username. (This is used for Reddit's user-agent, nothing more)"],
                               ["title","Enter the title for your daily posts. (Add {DATE} to add the date in the format of 'weekday, month day')"],
                               ["sleepTime","How many seconds to wait between refreshing? (Use whole numbers like 300 or expressions like 5 * 60)"]
                             ]:
        while True:
            value = input(question+"\n==>")
            confirm = input("Is '"+value+"' correct? (y/n)\n==> ")
            if confirm.lower() == "y":
                mscCreds[variable] = value
                break
            print("Confirmation failed. Restarting entry.")
    
    config["R"] = redCreds
    config["M"] = mscCreds
    with open(myPath+"configuration.ini","w") as cfg:
        config.write(cfg)
    print("Config file written successfully")
    return config

########################################################################
#                                                                      #
#    Script Startup                                                    #
#                                                                      #
########################################################################

try:
    mods = ["praw","re","configparser","time"]
    for mod in mods:
        print("Importing "+mod)
        exec("import "+mod)
except:
    exit(mod+" was not found. Install "+mod+" with pip to continue.")

# Flip the filepath backwards, look for the first non-alphanumeric character,
# grab the rest, then flip it forwards again. This theoretically gets the
# folder the script is in without using the os module.
myPath = re.search(r"[a-zA-Z0-9. ]*(.*)",__file__[::-1]).group(1)[::-1]

try:
    configSections = ["R","M"]
    creds = loadConfig(myPath)
    with open(myPath+"dailyPost.md","r") as dailyPost:
        DP = dailyPost.read()
except:
    creds = makeCreds(myPath)
    with open(myPath+"dailyPost.md","r") as dailyPost:
        DP = dailyPost.read()

## Normalize credentials
creds["R"]["u"] = creds["R"]["u"].replace("/u/","").replace("u/","")
creds["M"]["mySub"] = creds["M"]["mySub"].replace("/r/","").replace("r/","")
creds["M"]["botMaster"] = creds["M"]["botMaster"].replace("/u/","").replace("u/","")

## Reddit authentication
R = praw.Reddit(client_id = creds["R"]["c"],
                client_secret = creds["R"]["s"],
                password = creds["R"]["p"],
                user_agent = "DailyThreadBot, a bot for /r/"+creds["M"]["mySub"]+"; hosted by /u/"+creds["M"]["botMaster"],
                username = creds["R"]["u"])

print("Bot successfully loaded. Entering main loop.")

########################################################################
#                                                                      #
#    Script Actions                                                    #
#                                                                      #
########################################################################

while True:
    try:
        startTime = time.time()
        # Delete last post if it has 0 comments
        lastPost = R.redditor(creds["R"]["u"]).submissions.new().__next__()
        if len(lastPost.comments) == 0:
            print(lastPost.title,"had no comments. Deleting.")
            lastPost.delete()
        # Create a new post
        newPost = R.subreddit(creds["M"]["mySub"]).submit(creds["M"]["title"].replace("{DATE}",time.strftime("%A, %B %d")),selftext=DP)
        print("Made new post",newPost.title)
        endTime = time.time()
        # Sleep if we completed the job in under the refresh rate,
        # otherwise restart the loop immediately
        if eval(creds["M"]["sleepTime"]) - endTime + startTime > 0:
            time.sleep(eval(creds["M"]["sleepTime"]) - endTime + startTime)
    except Exception as e:
        i=1
        e=e
        while True:
            lastError = eval("e.__traceback__"+".tb_next"*i)
            if lastError == None:
                lineNumber = eval("e.__traceback__"+".tb_next"*(i-1)+".tb_lineno")
                break
            i += 1
        print("Error!\n\n  Line "+str(lineNumber)+" -> "+e.__str__()+"\n\nRetrying in one minute.")
        time.sleep(60)
