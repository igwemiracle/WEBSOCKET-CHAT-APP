import logging
from fastapi import FastAPI, WebSocketDisconnect, WebSocket
from fastapi.staticfiles import StaticFiles
from manager import ConnectionManager
from Routes.users import user
from Authenticate.auth import authenticate_user, oauth2_scheme
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.include_router(user)
app.mount("/static",
          StaticFiles(directory="static"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

manager = ConnectionManager()
logger = logging.getLogger(__name__)


@app.websocket("/ws/{client_name}")
async def websocket_endpoint(websocket: WebSocket, client_name: str):
    logger.info(f"WebSocket connection established for {client_name}")

    try:
        await manager.connect(websocket)
        await manager.broadcast(f"{client_name} joined the chat")

        while True:
            data = await websocket.receive_text()
            logger.info(f"Received message from {client_name}: {data}")
            await manager.broadcast(f"{client_name}: {data}")
    except WebSocketDisconnect:
        logger.warning(f"WebSocket disconnected for {client_name}")
        manager.disconnect(websocket)
        await manager.broadcast(f"{client_name} left the chat")
    except Exception as e:
        logger.error(f"An error occurred for {client_name}: {str(e)}")
        manager.disconnect(websocket)
