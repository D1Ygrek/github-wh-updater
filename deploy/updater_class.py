import git
import docker
import asyncio
import time
import os

class UpdaterMain():
    update_queue = []
    is_busy = False
    working_thread = None
    settings = None

    def __init__(self) -> None:
        pass
    
    async def thread_joiner(self):
        while True:
            if self.is_busy:
                await self.working_thread
                print(self.working_thread.result())
                self.is_busy = False
                self.working_thread = None
            else:
                await asyncio.sleep(30)

    async def updater_start(self, settings):
        self.settings = settings
        asyncio.create_task(self.thread_joiner())

    def update_git(self, repo_path):
        print('started git update')
        repo = git.Repo(repo_path)
        repo.remotes.origin.pull()
    
    def update_image(self, repo_path, version, service_name):
        print('started image update')
        client = docker.from_env()
        image_name = f'{self.settings.docker_repo}/{service_name}:{version}'
        image, logs = client.images.build(path=repo_path, rm=True, tag = image_name)
        print(image)
        print(logs)
        print('finished building')
        self.push_to_repo(image_name, client)
        self.service_update(image_name, service_name)
    
    def push_to_repo(self, image_name, cli):
        print("started pushing")
        cli.images.push(image_name)
        print("finished pushing")
    
    def service_update(self, image_name, service_name):
        bashCommand = f"sudo docker service update --force --image {image_name} --update-order start-first --replicas=2 {service_name}"
        print(bashCommand)
        os.system (bashCommand)
    
    def updater_main(self):
        print('started main update')
        while len(self.update_queue) != 0:
            now_updating =self.update_queue.pop(0)
            self.update_git(now_updating['repo'])
            self.update_image(now_updating['repo'],
                                    now_updating['v'],
                                    now_updating['service'])
            #update service
            time.sleep(30)
            print('finished update')




    async def start_update(self, repo_path, version, service_name):
        self.update_queue.append({'service':service_name,
                                    'repo':repo_path,
                                    'v':version}) 
        if self.working_thread is None:
            self.working_thread = asyncio.create_task(asyncio.to_thread(self.updater_main))
        if not self.is_busy:
            self.is_busy = True
        return True

