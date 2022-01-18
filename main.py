from sys import version
import uvicorn

from fastapi import FastAPI, Request, HTTPException, status

from pydantic import BaseSettings

from supply.token_check import create_hash
from supply.commit_check import check_commit

from deploy.updater_class import UpdaterMain


class Settings(BaseSettings):
    app_secret: str
    docker_repo: str
    class Config:
        env_file = ".env"

settings = Settings()

updater = UpdaterMain()


app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await updater.updater_start(settings)

@app.post('/github_webhook/assistant')
async def recieve_update(request: Request):
    x_hub_signature_256 = request.headers.get("X-Hub-Signature-256")
    #print(x_hub_signature_256)
    message_body = await request.body()
    print(message_body)
    if x_hub_signature_256!=create_hash(message_body, settings):
        raise HTTPException(
            status_code = status.HTTP_406_NOT_ACCEPTABLE,
            detail = "Wrong hash"
        )
    else:
        data = await request.json()
        is_deploy, version = check_commit(data['head_commit']['message'])
        if is_deploy:
            print(f'starting assistant deploy {version}')
            await updater.start_update('../assistant/ir-assistant-production', version, 'assistant')
        else:
            print('non-deploy commit to asssistant')

    return {'ok'}

@app.post('/github_webhook/ir-master-web')
async def irmw_update(request: Request):
    x_hub_signature_256 = request.headers.get("X-Hub-Signature-256")
    message_body = await request.body()
    if x_hub_signature_256!=create_hash(message_body, settings):
        raise HTTPException(
            status_code = status.HTTP_406_NOT_ACCEPTABLE,
            detail = "Wrong hash"
        )
    else:
        data = await request.json()
        is_deploy, version = check_commit(data['head_commit']['message'])
        if is_deploy:
            print(f'starting irm-w deploy {version}')
            await updater.start_update('../irm-web', version, 'ir-master-web')
        else:
            print('non-deploy commit to irmw')
    return {'ok'}

@app.post('/github_webhook/ir-charts')
async def irmw_update(request: Request):
    x_hub_signature_256 = request.headers.get("X-Hub-Signature-256")
    message_body = await request.body()
    if x_hub_signature_256!=create_hash(message_body, settings):
        raise HTTPException(
            status_code = status.HTTP_406_NOT_ACCEPTABLE,
            detail = "Wrong hash"
        )
    else:
        data = await request.json()
        is_deploy, version = check_commit(data['head_commit']['message'])
        if is_deploy:
            print(f'starting ir-charts deploy {version}')
            await updater.start_update('../chart_sup_app', version, 'ir-charts')
        else:
            print('non-deploy commit to ir-charts')
    return {'ok'}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=3333, reload=False)
