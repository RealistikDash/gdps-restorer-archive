# Made by RealistikDash from VPS Dev Team

from colorama import init, Fore, Back; init()
from pyfiglet import figlet_format
import json
import mysql.connector
from datetime import datetime
import random
from os import path
import os
import time
import progressbar

__VERSION__ = "0.1.0"

# Aliases
ColRes = Fore.RESET + Back.RESET

# Logger
def FormattedTime(DateTimeObject = None) -> str:
    """Returns a formatted time string."""
    if DateTimeObject == None:
        DateTimeObject = datetime.now()
    return DateTimeObject.strftime("%H:%M:%S")

def Log(Text):
    """Logs a thing in console."""
    print(f"{Fore.BLUE}[Restorer] {Fore.MAGENTA} [{FormattedTime()}] {Text} {Fore.RESET}")

def Success(Text):
    """Logs a good thing in console."""
    print(f"{Fore.BLUE}[Restorer] {Fore.GREEN}  [{FormattedTime()}] {Text} {Fore.RESET}")

def Fail(Text):
    """Logs a bad thing in console."""
    print(f"{Fore.BLUE}[Restorer] {Fore.RED}  [{FormattedTime()}] {Text} {Fore.RESET}")

def Warn(Text):
    """Warns about a bad thing in console."""
    print(f"{Fore.YELLOW}[Restorer] {Fore.RED}  [{FormattedTime()}] {Text} {Fore.RESET}")

# Configuration
DefaultConfig = {
    "SQLHost"     : "localhost",
    "SQLUser"     : "root",
    "SQLPassword" : "",
    "LiveDB" : "gdps",
    "BackupDB" : "backup",
    "LevelDir" : "/var/www/vgdps.ussr.pl/levels",
    "RestoreKeys" : {}
}

class JsonFile:
    @classmethod
    def SaveDict(self, Dict, File):
        """Saves a dict as a file."""
        with open(File, 'w') as json_file:
            json.dump(Dict, json_file, indent=4)

    @classmethod
    def GetDict(self, file):
        """Returns a dict from file name."""
        if not path.exists(file):
            return {}
        else:
            with open(file) as f:
                data = json.load(f)
            return data

UserConfig = JsonFile.GetDict("config.json")
# Configuration check
if UserConfig == {}:
    Log("No config found! Generating!"+Fore.RESET)
    JsonFile.SaveDict(DefaultConfig, "config.json")
    Success("Config created! It is named config.json. Edit it accordingly and start the server again!")
    exit()

else:
    # Check & update config
    AllGood = True
    NeedSet = []
    for key in list(DefaultConfig.keys()):
        if key not in list(UserConfig.keys()):
            AllGood = False
            NeedSet.append(key)

    if AllGood:
        Success("Configuration loaded successfully! Loading..." + Fore.RESET)
    else:
        #fixes config
        print("Updating config..." + Fore.RESET)
        for Key in NeedSet:
            UserConfig[Key] = DefaultConfig[Key]
            Log(f"Option {Key} added to config. Set default to '{DefaultConfig[Key]}'." + Fore.RESET)
        Success("Config updated! Please edit the new values to your liking." + Fore.RESET)
        JsonFile.SaveDict(UserConfig, "config.json")
        exit()

#mysql thing
print("Connecting to SQL... ", end="")
try:
    mydb = mysql.connector.connect(
        host=UserConfig["SQLHost"],
        user=UserConfig["SQLUser"],
        passwd=UserConfig["SQLPassword"],
    ) #connects to database
    print(f"Success!")
except Exception as e:
    print(f"{e}")
    exit()

#Constant Variables
Quotes = [
    "10K STARS OMG OMG OMG OMG OMG JESUS!!!!!!",
    "vps is good",
    "Imagine having your competitor's name in your website",
    "Dude dont ping"
]

Colours = [
    Fore.YELLOW,
    Fore.BLUE,
    Fore.MAGENTA,
    Fore.RESET,
    Fore.GREEN,
    Fore.CYAN
]

Options = f"""{Back.BLUE}{Fore.WHITE}>>>[OPTIONS AVAILABLE]<<<{ColRes}
{Fore.BLUE}[1]{ColRes} Restore Reuploaded Level Ratings
{Fore.BLUE}[2]{ColRes} Fix File Level IDs
{Fore.BLUE}[3]{ColRes} Delete Local Levels not in DB
{Fore.BLUE}[4]{ColRes} Bot Cleanup (Accounts)
{Fore.BLUE}[5]{ColRes} Bot Cleanup (Users)
{Fore.BLUE}[6]{ColRes} Realistik™ Total Bot Cleanup (SLOW)
{Fore.BLUE}[7]{ColRes} Ban restore from backup
{Fore.BLUE}[8]{ColRes} Restore levels from backup
{Fore.BLUE}[9]{ColRes} About GDPSRestorer
{Fore.BLUE}[0]{ColRes} Exit GDPSRestorer
"""

Credits = f"""      {Back.BLUE}{Fore.WHITE}>>>[CREDITS]<<<{ColRes}
GDPSRestorer v{__VERSION__}

########## VPS DEV MEMBERS ##########
{random.choice(Colours)} RealistikDash - Majority of the coding.
"""

AllowedOptions = [1, 9, 0, 2, 3,4,5,6,7,8]

WelcomeText = f"""{random.choice(Colours)} {figlet_format("Restorer")}
\t“{random.choice(Quotes)}”"""

Thing1CompleteScreen = f"{Back.BLUE}{Fore.WHITE}>>>[TASK COMPLETE]<<<{ColRes}" + """

Levels Affected
>> {}
Fetching time taken
>> {}s
Restoring time taken
>> {}s
Total time taken
>> {}s
"""

# helper functions
def time_to_ms(time1: float, time2: float):
    """Substracts times and rounds and adds a ms"""
    return f"{round((time1-time2)*1000,2)}ms"

# Functions
def RestoreReuploadedLevels():
    """Restores the rating status"""
    Log("Starting to restore the rating of reuploaded levels!")
    StartTime = round(time.time(), 2)
    BackupCursor = mydb.cursor() #cursor for the backup database
    BackupCursor.execute(f"USE {UserConfig['BackupDB']}") #remember kids, donnt use formats in real applications. here we trust the input
    #this is where we fetch all the data
    BackupCursor.execute("SELECT levelID, starDemon, starAuto, starStars, starCoins, starFeatured, starHall, starEpic, starDemonDiff, starDifficulty FROM levels WHERE userName = 'Reupload' OR userID = 388 OR userName = 'Reuploadbot'")
    ReuploadedLevels = BackupCursor.fetchall()
    BackupCursor.close() #we are done with the backup db

    #some info things
    LevelsToBeModified = len(ReuploadedLevels)
    FetchFinishTime = round(time.time(), 2)
    Log(f"Fetching levels from backup DB finished! Took {FetchFinishTime - StartTime}s and got {LevelsToBeModified} levels.")

    #now we start interfacing with real db
    Log("Starting to move the data to live db.")
    mycursor = mydb.cursor()
    mycursor.execute(f"USE {UserConfig['LiveDB']}")
    for Level in ReuploadedLevels:
        #there is prob a faster way to do this but eh
        Log(f"Restoring status to level with id of {Level[0]}")
        mycursor.execute("UPDATE levels SET starDemon = %s, starAuto = %s, starStars = %s, starCoins = %s, starFeatured = %s, starHall = %s, starEpic = %s, starDemonDiff = %s, starDifficulty = %s WHERE levelID = %s LIMIT 1",
        (
            Level[1], Level[2], Level[3], Level[4], Level[5], Level[6], Level[7], Level[8], Level[9], Level[0]
        ))
    mydb.commit() #applies all changes
    EndTime = round(time.time(), 2)
    Success("Restoring Statuses done!")
    print(Thing1CompleteScreen.format(LevelsToBeModified, FetchFinishTime - StartTime, EndTime - FetchFinishTime, EndTime - StartTime))

def RenameFiles():
    """Uses restore keys to change local file level ids."""
    RestoreKeys = UserConfig["RestoreKeys"]
    Kyes = list(RestoreKeys.keys())
    os.chdir(UserConfig["LevelDir"])
    for OldId in Kyes:
        NewId = str(RestoreKeys[OldId])
        OldId = str(OldId)
        if not os.path.exists(OldId):
            Log(f"OldId {OldId} not found!")
        else:
            Log(f"OdlId {OldId} found!")
            if os.path.exists(NewId):
                Log(f"File with levelID {NewId} found! Deleting.")
                os.remove(NewId)
            os.rename(OldId, NewId)
            Success(f"Moved {OldId} to {NewId}")

def DeleteNotInDB():
    """Deletes levels not in database."""
    StartTime = time.time()
    os.chdir(UserConfig["LevelDir"])
    mycursor = mydb.cursor()
    mycursor.execute(f"USE {UserConfig['LiveDB']}")
    mycursor.execute("SELECT levelID FROM levels")
    IdsToDelete = [f for f in os.listdir(UserConfig["LevelDir"]) if path.isfile(path.join(UserConfig["LevelDir"], f))] # list of local files
    for i in range(0, len(IdsToDelete)):
        try: #make sure the filenams are ints
            IdsToDelete[i] = int(IdsToDelete[i])
        except ValueError:
            IdsToDelete[i] = 0
    
    for Level in mycursor.fetchall():
        try:
            IdsToDelete.remove(Level[0])
        except ValueError:
            Log(f"Level {Level} not in IdsToDelete list! This could signify incorrect bounds.")
    LevelList = ""
    for Level in IdsToDelete:
        LevelList += str(Level) + " "
    print(f"Fetching levels to remove done! Took {round((time.time() - StartTime)*1000,2)}ms")
    print(f"Levels {LevelList}are going to be deleted locally ({len(IdsToDelete)} levels)! Are you sure you want to do that?")
    a = input("y/N> ")
    if a.lower() == "y":
        StartTime = time.time()
        for ID in IdsToDelete:
            Log(f"Deleting local level {ID}!")
            os.remove(str(ID))
        print(f"Finished deleting all invalid levels! Took {round((time.time() - StartTime)*1000,2)}ms")

def CleanupBotAccounts():
    """Deletes bot accounts."""
    Log("Beginning bot account cleanup!")
    try:
        AccID = int(input("Enter the newest real user's AccountID> "))
    except ValueError:
        Fail("Not a valid Account ID!")
        return
    mycursor = mydb.cursor() #create cursor
    mycursor.execute(f"USE {UserConfig['LiveDB']}")
    mycursor.execute("SELECT COUNT(*) FROM accounts WHERE accountID > %s", (AccID,))
    DelCount = mycursor.fetchone()[0]
    print(f"Are you sure you want to delete {DelCount} accounts? (y/N)")
    a = input(" ")
    if a.lower() != "y":
        Fail("Aborted by user.")
        return
    Log("Beginning user deletion.")
    StartTime = time.time()
    Log("Deleting users...")
    mycursor.execute("DELETE FROM accounts WHERE accountID > %s", (AccID,))
    #fix IDs
    Log("Fixing IDs...")
    mycursor.execute("ALTER TABLE accounts AUTO_INCREMENT = %s" , (AccID + 1,))
    mydb.commit()
    mycursor.close()
    Log(f"Cleanup finished! {DelCount} accounts deleted in {round((time.time() - StartTime) * 1000, 2)}ms")

def CleanupBotUsers():
    """Deletes bot users."""
    Log("Beginning bot user cleanup!")
    try:
        AccID = int(input("Enter the newest real user's UserID> "))
    except ValueError:
        Fail("Not a valid Account ID!")
        return
    mycursor = mydb.cursor() #create cursor
    mycursor.execute(f"USE {UserConfig['LiveDB']}")
    mycursor.execute("SELECT COUNT(*) FROM users WHERE userID > %s", (AccID,))
    DelCount = mycursor.fetchone()[0]
    print(f"Are you sure you want to delete {DelCount} users? (y/N)")
    a = input(" ")
    if a.lower() != "y":
        Fail("Aborted by user.")
        return
    Log("Beginning user deletion.")
    StartTime = time.time()
    Log("Deleting users...")
    mycursor.execute("DELETE FROM users WHERE userID > %s", (AccID,))
    #fix IDs
    Log("Fixing IDs...")
    mycursor.execute("ALTER TABLE users AUTO_INCREMENT = %s" , (AccID + 1,))
    mydb.commit()
    mycursor.close()
    Log(f"Cleanup finished! {DelCount} users deleted in {round((time.time() - StartTime) * 1000, 2)}ms")

def total_bot_cleanup(): #snake case as yes
    """Realistik style total bot cleanup ;)"""
    Log("Beginning bot massacare.")
    try:
        account_id = int(input("Enter the newest real user's AccountID> "))
    except ValueError:
        Fail("Not a valid Account ID!")
        return
    mycursor = mydb.cursor()
    mycursor.execute(f"USE {UserConfig['LiveDB']}")
    mycursor.execute("SELECT COUNT(*) FROM accounts WHERE accountID > %s", (account_id,))
    users_affected = mycursor.fetchone()[0]
    if users_affected == 0:
        Log("No one found!")
        return
    Warn("############BEFORE YOU DO ANYTHING############")
    Warn("PLEASE MAKE SURE YOU HAVE BACKED UP EVERYTHING")
    Warn("BEFORE RUNNING THIS COMMAND. ANY MISTAKE IN")
    Warn("YOUR INPUT CAN LITERALLY KILL YOUR GDPS. BE")
    Warn("SMART AND BACKUP YOUR DATABASE NOW BEFORE YOU")
    Warn("DO SOMETHING STUPID. THIS IS YOUR TIME TO BACK")
    Warn("OUT.")
    Warn("##############################################")
    Warn(f"This action will affect approximately {users_affected} users. Are you sure you want yo continue? (y/N)")
    a = input("")
    if a.lower() != "y":
        mycursor.close()
        Fail("Cancelled by user.")
        return
    Warn("ARE YOU SURE?? (y/N)")
    a = input("")
    if a.lower() != "y":
        mycursor.close()
        Fail("Cancelled by user.")
        return
    Log("Beginning to plunge all bots into the depths of hell.")
    start_time = time.time()
    start_accid = account_id
    mycursor.execute("SELECT accountID FROM accounts WHERE accountID > %s", (account_id,))
    actions = 2
    for user in progressbar.progressbar(mycursor.fetchall()):
        account_id = user[0]
        user_id = 0
        #getting user id
        mycursor.execute("SELECT userID FROM users WHERE extID = %s LIMIT 1", (account_id,))
        db_result = mycursor.fetchone()
        if db_result is not None: #in case userID wasnt created
            user_id = db_result[0]
        mycursor.execute("DELETE FROM users WHERE extID = %s LIMIT 1", (str(account_id),))
        mycursor.execute("DELETE FROM accounts WHERE accountID = %s LIMIT 1", (account_id,))
        mycursor.execute("DELETE FROM comments WHERE userID = %s", (user_id,))
        mycursor.execute("DELETE FROM friendreqs WHERE accountID = %s OR toAccountID = %s", (account_id, account_id))
        mycursor.execute("DELETE FROM blocks WHERE person1 = %s OR person2 = %s", (account_id, account_id))
        mycursor.execute("DELETE FROM levels WHERE extID = %s", (str(account_id),)) #i may make it also delete the levels from storage but there is alreaady a cleanup for that
        mycursor.execute("DELETE FROM levelscores WHERE accountID = %s", (account_id,))
        mycursor.execute("DELETE FROM messages WHERE accID = %s",(account_id,))
        actions += 9 #sql query count for stats
    Log("Fixing IDs...")
    mycursor.execute("ALTER TABLE accounts AUTO_INCREMENT = %s" , (start_accid + 1,))
    mycursor.execute("SELECT userID FROM users ORDER BY userID DESC LIMIT 1")
    lastest_userid = mycursor.fetchone()[0]
    mycursor.execute("ALTER TABLE users AUTO_INCREMENT = %s" , (lastest_userid + 1,))
    mydb.commit()
    Log(f"Done! Took {time_to_ms(time.time(),start_time)} with {actions} SQL queries executed and {users_affected} users wiped off the face of this earth.")

def restore_bans():
    """restore bans.""" #i just banned the whole server!
    Log("Beginning to restore bans.")
    _ = input("Are you sure you want to restore bans from backup database? (y/N) ")
    if _.lower() != "y":
        Fail("Aborted by user.")
        return
    #fetching data from old db
    start_time = time.time()
    backup_cursor = mydb.cursor() #cursor for the backup database
    backup_cursor.execute(f"USE {UserConfig['BackupDB']}")
    backup_cursor.execute("SELECT userID FROM users WHERE isBanned = 1")
    banned = backup_cursor.fetchall()
    backup_cursor.close()
    Log(f"Fetched {len(banned)} users to re-ban! Took {time_to_ms(time.time(), start_time)}")

    mycursor = mydb.cursor()
    mycursor.execute(f"USE {UserConfig['LiveDB']}")
    for i in progressbar.progressbar(banned):
        banned_id = i[0]
        mycursor.execute("UPDATE users SET isBanned = 1 WHERE userID = %s LIMIT 1", (banned_id,))
    mydb.commit()
    mycursor.close()
    Log(f"Done! Re-banned {len(banned)} users! Took {time_to_ms(time.time(),start_time)}")

def restore_levels():
    """Restores level db rows from backup db."""
    backup_cursor = mydb.cursor() #cursor for the backup database
    #mycursor = mydb.cursor()
    #mycursor.execute(f"USE `{UserConfig['LiveDB']}`")
    backup_cursor.execute(f"USE `{UserConfig['BackupDB']}`")

    backup_cursor.execute("SELECT levelID FROM levels")
    levelids = [i[0] for i in backup_cursor.fetchall()]

    backup_cursor.execute(f"USE `{UserConfig['LiveDB']}`")
    # Now we check if each level exists. If not, add it to a list.
    print("Checking which levels exist...")
    not_existing_levels = []

    for level in levelids:
        backup_cursor.execute("SELECT COUNT(*) FROM levels WHERE levelID = %s", (level,))
        if not backup_cursor.fetchone()[0]: # It does not exist
            not_existing_levels.append(level)
    
    print(f"Restoring {len(not_existing_levels)} levels...")

    # Fetch levels from backup db
    backup_cursor.execute(f"USE `{UserConfig['BackupDB']}`")
    backup_levels = []
    for level in not_existing_levels:
        backup_cursor.execute("""
        SELECT
            gameVersion,
            binaryVersion,
            userName,
            levelID,
            levelName,
            levelDesc,
            levelVersion,
            levelLength,
            audioTrack,
            auto,
            password,
            original,
            twoPlayer,
            songID,
            objects,
            coins,
            requestedStars,
            extraString,
            levelInfo,
            secret,
            starDifficulty,
            downloads,
            likes,
            starDemon,
            starAuto,
            starStars,
            uploadDate,
            updateDate,
            starCoins,
            starFeatured,
            starEpic,
            starDemonDiff,
            userID,
            extID
        FROM
            levels
        WHERE
            levelID = %s
        LIMIT 1
        """, (level,))
        level_db = backup_cursor.fetchone()
        if level_db is not None:
            backup_levels.append(level_db)
    
    # FINALLY add them.
    print("Adding levels.")
    backup_cursor.execute(f"USE `{UserConfig['LiveDB']}`")
    for level in backup_levels:
        print(f"Adding level: {level[4]} by {level[2]} ({level[3]})")
        backup_cursor.execute("""
        INSERT INTO levels
            (
                gameVersion,
                binaryVersion,
                userName,
                levelID,
                levelName,
                levelDesc,
                levelVersion,
                levelLength,
                audioTrack,
                auto,
                password,
                original,
                twoPlayer,
                songID,
                objects,
                coins,
                requestedStars,
                extraString,
                levelInfo,
                secret,
                starDifficulty,
                downloads,
                likes,
                starDemon,
                starAuto,
                starStars,
                uploadDate,
                updateDate,
                starCoins,
                starFeatured,
                starEpic,
                starDemonDiff,
                userID,
                extID,
                unlisted,
                hostname
            ) VALUES
            (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, 0, 'realistikdash was here :))')
        """, level)
    
    mydb.commit()

    
if __name__ == "__main__":
    Success(f"GDPS Restorer {__VERSION__} loaded successfully!")
    while True:
        print(Options)
        Option = input("GDPSRestorer> ")
        try:
            Option = int(Option)
            Faild = False
        except:
            Fail("Invalid option!")
            Faild = True
        
        if not Faild:
            #last check
            if Option not in AllowedOptions:
                Fail("Non-existant option!")
            else:
                #ok lets start the actions...
                #still wish there were switch statements in python
                if Option == 0: #exit
                    exit()
                elif Option == 9: #credits
                    print(Credits)
                elif Option == 1:
                    RestoreReuploadedLevels()
                elif Option == 2:
                    RenameFiles()
                elif Option == 3:
                    DeleteNotInDB()
                elif Option == 4:
                    CleanupBotAccounts()
                elif Option == 5:
                    CleanupBotUsers()
                elif Option == 6:
                    total_bot_cleanup()
                elif Option == 7:
                    restore_bans()
                elif Option == 8:
                    restore_levels()
