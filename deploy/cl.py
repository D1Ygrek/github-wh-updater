import docker
print('pomer ded')

client = docker.from_env()
print(client.containers.list())
for container in client.containers.list():
    print(container)