from imports_lib import MultiMCPTools, Agent, instructions_steps,  SqliteDb, generate_unique_id, asyncio
from agents.reasioning_agent import get_detailed_reasoning
from components.savingintoJson import save_message_to_json, update_json_entry
from components.google_search_tools import get_google_Search_tools
from datetime import datetime
from agents.llamaindexagent import DropboxTools
from agents.navigations_tool import NavigationTools
from agno.models.openrouter import OpenRouter
OPENROUTER_API_KEY= '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'
base_path_for_chat = "D:/finsocial/MCP LLMS/userChats"
GOOGLE_API_KEY = 'AIzaSyAx65YdFAZ--Uuf93oXHjA8kpiA7SNGb4g'
async def run_agent(message: str, username: str, chat_id: str, google_search: str, deep_google_search: str,current_time) -> None:
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
        
        get_reasonings = await get_detailed_reasoning(message, chat_id=chat_id, username=username,current_time=current_time,base_path =base_path_for_chat)
        print("it's done")
        # minimizing the reasioning  
        # show_res = await show_reasoning_finals(get_reasonings)
        # print("show_res"*20,)
        # print(show_res)
        # print("show_res"*20,)

        update_json_entry(
            username=username, 
            chat_id=chat_id, 
            response_id=get_the_first_response_id, 
            field="reasioning", 
            content=get_reasonings, 
            base_path=base_path_for_chat
        )

        # Create a new event loop for the async operations
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Use a single async context for all MCP tools
        async with MultiMCPTools(["npx -y @openbnb/mcp-server-airbnb --ignore-robots-txt  --port 3000"]) as mcp_tools:
            agent = Agent(
                model=OpenRouter(id="deepseek/deepseek-chat-v3-0324:free",api_key="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"),
                tools=[mcp_tools,DropboxTools(),NavigationTools()]+google_search_tool,
                
                session_id=chat_id,
                user_id=username,
                db=SqliteDb(
                    db_file=f"{base_path_for_chat}/{username}/SqlDB/{chat_id}.db",
                   
                ),
                add_history_to_context=True,
                read_chat_history=True,
                num_history_runs=100,
                stream_intermediate_steps=False,
                add_datetime_to_context=True,instructions=instructions_steps(reasoning_steps=get_reasonings,current_time=current_time),
            )
            
            response = await agent.arun(message)
            get_content = response.content
            update_json_entry(
                username=username, 
                chat_id=chat_id,
                response_id=get_the_first_response_id,
                field="AI Message", 
                content=get_content, 
                base_path=base_path_for_chat
            )
        
            return get_content

    except Exception as e:
        print(f"Error occurred: {e}")
        return f"An error occurred: {str(e)}"

if __name__ == "__main__":
    username = 'pawan'
    chat_id = input("Enter chat_id: ")
    google_search = 'y'
    deep_google_search = 'y'
    # google_search = input("Enter google search: enter y or n: ")
    # deep_google_search = input("Enter deep google search: enter y or n: ")
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Initialize variables
    flag_first_message = False
    chat_id_AVailable = True
    
    if len(chat_id) == 0:
        flag_first_message = True
        chat_id_AVailable = False

    # Create a single event loop for the entire application
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        while True:
            user_prompt = input("Enter your message: ")
            if user_prompt.lower() == "exit":
                break
                
            if not chat_id_AVailable:
                chat_id = generate_unique_id()
                chat_id =  chat_id
                chat_id_AVailable = True
                
            result = loop.run_until_complete(run_agent(user_prompt, username=username, chat_id=chat_id, google_search=google_search,deep_google_search=deep_google_search,current_time=current_time))
            print(result)
    finally:
        # Ensure proper cleanup
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
