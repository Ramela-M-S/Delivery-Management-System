from time import perf_counter

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference
from contextlib import asynccontextmanager

from rich import panel
from app.database.session import create_db_tables


from app.api.router import master_router
from app.worker.tasks import add_log



@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    print(panel.Panel("Server started...",border_style = "green"))

    await create_db_tables()
    yield

    print(panel.Panel("Server stopped...",border_style = "red"))


description ="""
Delivery Management System for sellers and delivery agents

### Seller
-Submit shipment effortlessly
-Share tracking links with customers


### Delivery Agent
-Auto accept shipments
-Track and update shipment status
-Email and SMS notifications

"""


app = FastAPI(lifespan = lifespan_handler,
              title="FastShip",
              description=description,)
app.include_router(master_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500"],
)

@app.middleware("http")
async def custom_middleware (request: Request, call_next):
    start = perf_counter()
    response: Response = await call_next(request)
    end = perf_counter()
    time_taken = round(end-start, 2)

    add_log(f"{request.method} {request.url} ({response.status_code}) {time_taken} s")
    return response


@app.get("/scalar", include_in_schema=False)
async def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API",
    )
