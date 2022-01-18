import git
import docker


async def update_repo(repo_path):
    print(repo_path)
    repo = git.Repo(repo_path)
    print(repo)
    for branch in repo.branches:
        print(branch)
    repo.remotes.origin.pull()

async def update_image(repo_path, version):
    await update_repo(repo_path)
    client = docker.from_env()
    for line in client.images.build(path=repo_path, rm=True, tag = version):
        print(line)
    #for image in client.images.list():
    #    print(image)
    #    print(image.id)
    #    print(image.tags)
    #    print(image.attrs)
    #    print(image.labels)