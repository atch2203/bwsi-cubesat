from git import Repo

def commit_and_push(img_name):
    repo = Repo('/home/pi/CHARMS')
    repo.git.checkout('comms')
    repo.git.add('/home/pi/CHARMS/Data')
    repo.index.commit(f"Add {img_name}")
    print('made the commit')
    origin = repo.remote('origin')
    print('added remote')
    origin.push()
    print('pushed changes\n')
