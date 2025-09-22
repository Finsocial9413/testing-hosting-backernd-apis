import logging
import sys
import os
from fastapi import FastAPI, Request, Depends, HTTPException, Header, APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from typing import Optional
from HindAi_users.auth_api import router as auth_router
from user_credits.api import router as credit_router
from htmlgen.api import router as html_router
from chatApis.responses import router as chat_router
from chatApis.userchat_data import router
from chatApis.download_Files import router as downloadingfile
from platforms.api import router as platform_router
from platforms.llm_api_Test import router as test_platform_router
from platforms.add_api_model import router as add_api_model
from subscription.api import router as subscription_router
from subscription.add__user_sub import router as add_subscription_router
from gpt_models.api import router as personal_model_router
from gpt_models.api import router as personal_model_router
from enchance_Prompter.enchance_prompt import router as enchance_router
from payment_gateway.api import router as payment_gateway_router
from suggestion_prompt_generator.api import router as suggestion_router

# snaptrades api's 
from account_atteched_details.api import router as atteched_accounts_router
from accounts.api import router as snaptrade_user_account_router
from get_Charts.chart_endpoint import router as GET_Charts_router
from connection_portal.api import router as connection_portal_router
from Orders.Market_ordersEndpoint import router as Orders_router
from Orders.Limit_ordersEndpoint import router as Limit_Orders_router
from Orders.STOP_OrdersEndpoint import router as Stop_Orders_router
from Orders.STOPLIMIT_OrdersEndpoint import router as Stop_Limit_Orders_router
# finish snaptrade api's 

from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(dotenv_path=env_path)
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the API key security scheme
API_KEY = os.getenv("API_KEY")  # Load from .env file
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Get the current directory for template loading
current_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(current_dir, "templates")
templates = Jinja2Templates(directory=templates_dir)

# Function to verify API key
async def verify_api_key(api_key: Optional[str] = Depends(api_key_header)):
    if api_key is None or api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return api_key

# Create the FastAPI app instance (without docs)
app = FastAPI(
    title="HindAI API", 
    version="2.0.0",
    docs_url=None,  # Disable default docs
    )

# Create separate routers for HTTP and WebSocket endpoints
http_chat_router = APIRouter()
websocket_chat_router = APIRouter()

# Import individual endpoints from responses
from chatApis.responses import run_agent_endpoint, get_task_status, get_task_result, cancel_task, stream_task

# Add HTTP endpoints to the HTTP router
http_chat_router.add_api_route("/run-agent", run_agent_endpoint, methods=["POST"])
http_chat_router.add_api_route("/task/{task_id}/status", get_task_status, methods=["GET"])
http_chat_router.add_api_route("/task/{task_id}/result", get_task_result, methods=["GET"])
http_chat_router.add_api_route("/task/{task_id}/cancel", cancel_task, methods=["POST"])

# Add WebSocket endpoint to the WebSocket router (without authentication)
websocket_chat_router.add_api_websocket_route("/task/{task_id}/stream", stream_task)

# Include HTTP chat router with API key protection
app.include_router(
    http_chat_router,
    prefix="/chats",
    tags=["HindAI Chat"],
    responses={404: {"description": "Not found"}},
    # dependencies=[Depends(verify_api_key)]  # Apply API key verification to HTTP endpoints only
)
app.include_router(
    suggestion_router,
    prefix="/suggestion_router",
    tags=["suggestion Router"],
    responses={404: {"description": "Not found"}},
    # dependencies=[Depends(verify_api_key)]  # Apply API key verification to HTTP endpoints only
)
# app.include_router(
#     payment_gateway_router,
#     prefix="/payment_gateway",
#     tags=["HindAI Payment Gateway"],
#     responses={404: {"description": "Not found"}},
#     # dependencies=[Depends(verify_api_key)]  # Apply API key verification to HTTP endpoints only
# )
# app.include_router(
#     downloadingfile,
#     prefix="/download",
#     tags=["HindAI Chat"],
#     responses={404: {"description": "Not found"}},
#     # dependencies=[Depends(verify_api_key)]  # Apply API key verification to HTTP endpoints only
# )
# app.include_router(
#     enchance_router,
#     prefix="/enhance",
#     tags=["Enhance Prompt"],
#     responses={404: {"description": "Not found"}},
#     # dependencies=[Depends(verify_api_key)]  # Apply API key verification to HTTP endpoints only
# )
# app.include_router(
#     personal_model_router,
#     prefix="/personal-model-router",
#     tags=["Personal Model"],
#     responses={404: {"description": "Not found"}},
#     # dependencies=[Depends(verify_api_key)]  # Apply API key verification to HTTP endpoints only
# )

# app.include_router(
#     credit_router,
#     prefix="/Credits",
#     tags=["HindAI Credits"],
#     responses={404: {"description": "Not found"}},
#     # dependencies=[Depends(verify_api_key)]  # Apply API key verification to HTTP endpoints only
# )

# # Include WebSocket chat router without API key protection
# app.include_router(
#     websocket_chat_router,
#     prefix="/chats",
#     tags=["WebSocket Streaming"],
#     responses={404: {"description": "Not found"}},
#     # No dependencies here - WebSocket doesn't use API key authentication
# )

# # Include the HTML generation router
# app.include_router(
#     router,
#     prefix="/userchats",
#     tags=["Chats History"],
#     responses={404: {"description": "Not found"}},
#     # dependencies=[Depends(verify_api_key)]  # Apply API key verification to all endpoints

# )
# # Include the HTML generation router
# app.include_router(
#     html_router,
#     prefix="/html",
#     tags=["HTML Generation"],
#     responses={404: {"description": "Not found"}},
#     dependencies=[Depends(verify_api_key)]  # Apply API key verification to all endpoints

# )

# # Include the auth router immediately after app creation
# app.include_router(
#     auth_router,
#     prefix="/auth",
#     tags=["User Profiles"],
#     responses={404: {"description": "Not found"}},
#     dependencies=[Depends(verify_api_key)]  # Apply API key verification to all endpoints

# )
# # Include the auth router immediately after app creation
# app.include_router(
#     platform_router,
#     prefix="/platform_router",
#     tags=["Platforms"],
#     responses={404: {"description": "Not found"}},
#     # dependencies=[Depends(verify_api_key)]  # Apply API key verification to all endpoints

# )


# app.include_router(
#     test_platform_router,
#     prefix="/test_platform_API",
#     tags=["Testing Api's"],
#     responses={404: {"description": "Not found"}},
#     # dependencies=[Depends(verify_api_key)]  # Apply API key verification to all endpoints
# )
# app.include_router(
#     add_api_model,
#     prefix="/add_platform_model",
#     tags=["Add Platform Model"],
#     responses={404: {"description": "Not found"}},
#     # dependencies=[Depends(verify_api_key)]  # Apply API key verification to all endpoints
# )


# app.include_router(
#     subscription_router,
#     prefix="/subscription",
#     tags=["Subscriptions Details"],
#     responses={404: {"description": "Not found"}},
#     # dependencies=[Depends(verify_api_key)]  # Apply API key verification to all endpoints

# )
# app.include_router(
#     add_subscription_router,
#     prefix="/add-subscription",
#     tags=["Subscriptions Add"],
#     responses={404: {"description": "Not found"}},
#     # dependencies=[Depends(verify_api_key)]  # Apply API key verification to all endpoints

# )
app.include_router(
    atteched_accounts_router,
    prefix="/attached-accounts",
    tags=["Attached Accounts"],
    responses={404: {"description": "Not found"}},
    # dependencies=[Depends(verify_api_key)]  # Apply API key verification to all endpoints

)
app.include_router(
    snaptrade_user_account_router,
    prefix="/snaptrade-user-accounts",
    tags=["Snaptrade User Accounts"],
    responses={404: {"description": "Not found"}},
    # dependencies=[Depends(verify_api_key)]  # Apply API key verification to all endpoints

)
app.include_router(
    connection_portal_router,
    prefix="/connection-portal",
    tags=["Connection Portal"],
    responses={404: {"description": "Not found"}},
    # dependencies=[Depends(verify_api_key)]  # Apply API key verification to all endpoints

)
app.include_router(
    Orders_router,
    prefix="/orders",
    tags=["Market Orders"],
    responses={404: {"description": "Not found"}},
    # dependencies=[Depends(verify_api_key)]  # Apply API key verification to all endpoints

)
app.include_router(
    Orders_router,
    prefix="/orders",
    tags=["Market Orders"],
    responses={404: {"description": "Not found"}},
    # dependencies=[Depends(verify_api_key)]  # Apply API key verification to all endpoints

)
app.include_router(
    Limit_Orders_router,
    prefix="/limit-orders",
    tags=["Limit Orders"],
    responses={404: {"description": "Not found"}},
    # dependencies=[Depends(verify_api_key)]  # Apply API key verification to all endpoints

)
app.include_router(
    Stop_Orders_router,
    prefix="/stop-orders",
    tags=["Stop Orders"],
    responses={404: {"description": "Not found"}},
    # dependencies=[Depends(verify_api_key)]  # Apply API key verification to all endpoints

)
app.include_router(
    Stop_Limit_Orders_router,
    prefix="/stop-limit-orders",
    tags=["Stop Limit Orders"],
    responses={404: {"description": "Not found"}},
    # dependencies=[Depends(verify_api_key)]  # Apply API key verification to all endpoints

)
app.include_router(
    GET_Charts_router,
    prefix="/get-charts",
    tags=["Get Charts"],
    responses={404: {"description": "Not found"}},
    # dependencies=[Depends(verify_api_key)]  # Apply API key verification to all endpoints

)



@app.get("/")
async def root():
    return {"message": "HindAI API is running"}


# Custom Swagger UI endpoint
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui(request: Request):
    return templates.TemplateResponse(
        "custom_swagger_ui.html",
        {
            "request": request,
            "openapi_url": app.openapi_url
        }
    )


# Add CORS middleware to FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5174",
        "http://127.0.0.1:5500",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:9000",
        "https://hindai.finsocial.tech",
        "https://mcp.codewizzz.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "X-Requested-With",
        "X-CSRFTOKEN",
        "X-API-Key"  # Add the API key header to allowed headers
    ],
)

# Mount static file directories after app creation
app.mount("/media", StaticFiles(directory="media"), name="media")
