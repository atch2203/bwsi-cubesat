from git import Repo

def commit_and_push(message):
    try:
        repo = Repo('/home/pi/CHARMS')
        repo.git.add('--all')
        repo.index.commit(f"-Automatic push- {message}")
        print('made the commit')
        origin = repo.remote('origin')
        print('added remote')
        origin.push()
        print('pushed changes\n')
    except:
        print("error in pushing")

def pull():
    try:
        repo = Repo('/home/pi/CHARMS')
        origin = repo.remote('origin')
        origin.pull()
        print('pulled')
    except:
        print('error in pulling')
