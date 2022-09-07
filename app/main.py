# import boto3

from ws_blaster.blasting import Blaster
from mangum import Mangum
from fastapi import FastAPI
from app.config import get_settings

settings = get_settings()
root_path = "/" if settings.STAGE == 'local' else f"/{settings.STAGE}/"
app = FastAPI(title=f"{settings.PROJECT_NAME} ({settings.STAGE.upper()})",
              root_path=root_path,
              description="""An API Service created to blast promotional 
                            messages to prospective clients using Whats App.""")
handler = Mangum(app)


@ app.get("/", status_code=200)
def get_index():
    return {'title': settings.PROJECT_NAME,
            'authors': ["Ahilan Ashwin", "Ammar Azman"],
            'version': "0.1.1",
            'stage': settings.STAGE}


@ app.get('/ping', status_code=200)
def healthcheck():
    return {'status': "Success"}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8080,
                log_level="debug", reload=True)
