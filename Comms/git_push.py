from git import Repo

def commit_and_push(message):
    repo = Repo('/home/pi/CHARMS')
    repo.git.checkout('comms')
    repo.git.add('--all')
    repo.index.commit(f"-Automatic push- {message}")
    print('made the commit')
    origin = repo.remote('origin')
    print('added remote')
    origin.push()
    print('pushed changes\n')

def pull():
    repo = Repo('/home/pi/CHARMS')
    origin = repo.remote('origin')
    origin.pull()
    print('pulled')
