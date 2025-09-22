from imports_lib import MultiMCPTools, Agent, instructions_steps,  SqliteDb, generate_unique_id, asyncio,show_language_menu,LanguageTranslator
from agents.reasioning_agent import get_detailed_reasoning
from agno.models.sambanova import Sambanova
from agno.models.nebius import Nebius
from agno.models.mistral import MistralChat
from agno.models.nvidia import Nvidia
from components.savingintoJson import save_message_to_json, update_json_entry
from components.language_check import language_check
from components.translator import LanguageTranslator
from components.google_search_tools import get_google_Search_tools
from datetime import datetime
import os
from dotenv import load_dotenv
from agents.llamaindexagent import DropboxTools
from agents.navigations_tool import NavigationTools
from agents.email_tool import EmailTools
from agents.telegrambot import TelegramToolkit
from agents.click_tool import ClickTools
from agents.charts import ChartTools
from agents.Stocks_order import  place_stock_order

from agents.visualization import VisualizationTools
from agno.models.openrouter import OpenRouter
from agno.tools.tavily import TavilyTools

from agno.tools.openbb import OpenBBTools
# Load environment variables from .env file
load_dotenv()
# Replace the hardcoded base path with the environment variable
base_path_for_chat = os.getenv("BASE_PATH_FOR_CHAT", "D:/finsocial/Multi model adding for the trading/userChats")  # Default value as fallback
knowledge_base_file_path = os.getenv("knowledge_base_path", "D:/finsocial/MCP LLMS/userChats/knowledge_base.json")  # Default value as fallback
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyAx65YdFAZ--Uuf93oXHjA8kpiA7SNGb4g")

async def run_agent(model_name:str,message: str, username: str, chat_id: str, language:str, language_code:str, translator, google_search: str, deep_google_search: str,current_time,get_reasonings,get_trans_reasonings,get_reasoning_status,api,
                                model_config, task_id) -> None:
    try:
        if google_search == 'y':
            google_search_tool = get_google_Search_tools(google_search)
        else :
            google_search_tool = []
        get_the_first_response_id = save_message_to_json(
            username=username, 
            chat_id=chat_id, 
            message=message, 
            base_path=base_path_for_chat
        )
        check_code =language_check(language_code)
        
        update_json_entry(
                    username=username, 
                    chat_id=chat_id, 
                    response_id=get_the_first_response_id, 
                    field="task_id", 
                    content=task_id, 
                    base_path=base_path_for_chat,
                    
        )
        
        if check_code == False:
            try:
                message = await translator.translate_text_async(text=message, source_lang=language_code, target_lang='eng_Latn')
                print(f'message translated from {language} to eng_Latn: {message}')
                update_json_entry(
                    username=username, 
                    chat_id=chat_id, 
                    response_id=get_the_first_response_id, 
                    field="Translated user message", 
                    content=message, 
                    base_path=base_path_for_chat,
                    
                )
            except Exception as e:
                print(f"Error in translation: {e}")

    

        # saving the main reasoning into the json file both the reasonings and the translated reasonings
        if get_reasoning_status == True:
            update_json_entry(
                username=username, 
                chat_id=chat_id, 
                response_id=get_the_first_response_id, 
                field="Main_reasoning", 
                content=get_reasonings, 
                base_path=base_path_for_chat
            )
            update_json_entry(
                username=username, 
                chat_id=chat_id, 
                response_id=get_the_first_response_id, 
                field="Main_reasoning_translated", 
                content=get_trans_reasonings, 
                base_path=base_path_for_chat
            )
        else:
            update_json_entry(
                username=username, 
                chat_id=chat_id, 
                response_id=get_the_first_response_id, 
                field="Main_reasoning", 
                content='', 
                base_path=base_path_for_chat
            )
            update_json_entry(
                username=username, 
                chat_id=chat_id, 
                response_id=get_the_first_response_id, 
                field="Main_reasoning_translated", 
                content='', 
                base_path=base_path_for_chat
            )
        # Create a new event loop for the async operations
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        MCP_TOOL_USE = False
        # Use a single async context for all MCP tools with timeout handling
        # try:
        
  
        if MCP_TOOL_USE == True:
            async with MultiMCPTools(["npx -y @openbnb/mcp-server-airbnb --ignore-robots-txt",]) as mcp_tools:
                agent = Agent(
                    model=OpenRouter(id=model_name,api_key=os.getenv("OPENROUTER_API_KEY"),
        max_tokens=1024) if api =='no' else model_config,
        
                    tools=[ 
                        place_stock_order,
                        OpenBBTools(stock_price=True, search_symbols=True, company_news=True, company_profile=True, price_targets=True),
                        VisualizationTools(output_dir="D:/finsocial/Multi model adding for the trading/agents/charts/", enable_all=True),
                        TavilyTools(api_key='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'),ChartTools(),TelegramToolkit(),EmailTools(),mcp_tools,DropboxTools(),NavigationTools(),ClickTools()]+google_search_tool,
                    
                    session_id=chat_id,
                    user_id=username,
                    db=SqliteDb(
                        db_file=f"{base_path_for_chat}/{username}/SqlDB/{chat_id}.db",
                    ),
                    add_history_to_context=True,
                    read_chat_history=True,
                    num_history_runs=100,
                    stream_intermediate_steps=False,
                    add_datetime_to_context=True,
                    instructions=instructions_steps(reasoning_steps=get_reasonings,current_time=current_time,reasoning_status=get_reasoning_status),
                 
                )
                
                response = await agent.arun(message)
                
                get_content =  response.content
                
        else:
            print("MCP tools are not used, running agent without them")
        # except Exception as mcp_error:
            # print(f"Error with MCP tools: {mcp_error}")
            # Fallback: run agent without MCP tools

            agent = Agent(
                model=OpenRouter(id=model_name,api_key=os.getenv("OPENROUTER_API_KEY"),
        max_tokens=1024) if api =='no' else model_config,

                tools=[ 
                    place_stock_order,
                    OpenBBTools(enable_get_stock_price=True, enable_search_company_symbol=True, enable_get_company_news=True, enable_get_company_profile=True, enable_get_price_targets=True,all=True),
                    VisualizationTools(output_dir="D:/finsocial/Multi model adding for the trading/agents/charts/", enable_all=True),
                    TavilyTools(api_key='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'),
                    ChartTools(),
                    TelegramToolkit(),
                    EmailTools(),
                    DropboxTools(),
                    NavigationTools(),
                    ClickTools()]+google_search_tool,
               
                session_id=chat_id,
                user_id=username,
                db=SqliteDb(
                    db_file=f"{base_path_for_chat}/{username}/SqlDB/{chat_id}.db",
                  
                ),
                add_history_to_context=True,
                read_chat_history=True,
                num_history_runs=100,
                stream_intermediate_steps=False,
                add_datetime_to_context=True,
                instructions=instructions_steps(reasoning_steps=get_reasonings,current_time=current_time,reasoning_status=get_reasoning_status),
             
            )
            try:
                response = await agent.arun(message)
                get_content =  response.content
            except Exception as e:
                error_msg = str(e).lower()
                if 'no auth credentials found'.lower() in error_msg:
                    get_content = "Provided API is not correct check your api again_secretkey_to_remove_anyother_type_of_the_confusion123454645451215451545"
                print(f"Error loading knowledge: {e}")


        # Update JSON with AI response
        if get_content == "Provided API is not correct check your api again_secretkey_to_remove_anyother_type_of_the_confusion123454645451215451545":
            get_content = 'Provided API is not correct check your api again'
            update_json_entry(
                username=username, 
                chat_id=chat_id,
                response_id=get_the_first_response_id,
                field="AI Message", 
                content='Provided API is not correct check your api ', 
                base_path=base_path_for_chat
            )
            
            # Handle response translation if needed
            if check_code == False:
                try:
                    translated_response = await translator.translate_text_async(
                        text='Provided API is not correct check your api ', 
                        source_lang='eng_Latn', 
                        target_lang=language_code
                    )
                    # Update with translated response
                    update_json_entry(
                        username=username, 
                        chat_id=chat_id,
                        response_id=get_the_first_response_id,
                        field="Translated AI Message", 
                        content=translated_response, 
                        base_path=base_path_for_chat
                    )
                    return {'response':translated_response,
                            'original_response':get_content}
                except Exception as e:
                    print(f"Error translating response: {e}")
                    return 'Provided API is not correct check your api '
            else:
                update_json_entry(
                        username=username, 
                        chat_id=chat_id,
                        response_id=get_the_first_response_id,
                        field="Translated AI Message", 
                        content='', 
                        base_path=base_path_for_chat
                    )
                return {'response':get_content,
                            'original_response':get_content}

        update_json_entry(
            username=username, 
            chat_id=chat_id,
            response_id=get_the_first_response_id,
            field="AI Message", 
            content=get_content, 
            base_path=base_path_for_chat
        )
        
        # Handle response translation if needed
        if check_code == False:
            try:
                translated_response = await translator.translate_text_async(
                    text=get_content, 
                    source_lang='eng_Latn', 
                    target_lang=language_code
                )
                # Update with translated response
                update_json_entry(
                    username=username, 
                    chat_id=chat_id,
                    response_id=get_the_first_response_id,
                    field="Translated AI Message", 
                    content=translated_response, 
                    base_path=base_path_for_chat
                )
                return {'response':translated_response,
                        'original_response':get_content}
            except Exception as e:
                print(f"Error translating response: {e}")
                return get_content
        else:
            update_json_entry(
                    username=username, 
                    chat_id=chat_id,
                    response_id=get_the_first_response_id,
                    field="Translated AI Message", 
                    content='', 
                    base_path=base_path_for_chat
                )
            return {'response':get_content,
                        'original_response':get_content}

    except Exception as e:
        error_msg = str(e)
        print(f"Error occurred: {error_msg}")
        
        # Return a user-friendly error message
        if "timeout" in error_msg.lower() or "clientrequest" in error_msg.lower():
            return "I apologize, but I'm experiencing some technical difficulties with external tools. Please try your request again in a moment."
        else:
            return f"I encountered an issue while processing your request. Please try again."