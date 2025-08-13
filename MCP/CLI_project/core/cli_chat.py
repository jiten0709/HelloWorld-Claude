from core.chat import Chat
from mcp_client import MCP_Client
from core.claude import Claude
from mcp.types import Prompt, PromptMessage
from typing import Tuple, List
from anthropic.types import MessageParam

class CliChat(Chat):
    def __init__(self, doc_client: MCP_Client, clients: dict[str, MCP_Client], claude_service: Claude):
        super().__init__(claude_service=claude_service, clients=clients)
        self.doc_client: MCP_Client = doc_client

    async def list_prompts(self) -> List[Prompt]:
        """Lists all available prompts from the document client."""
        return await self.doc_client.list_prompts()
    
    async def list_docs_ids(self) -> List[str]:
        """Lists all document IDs available in the document client."""
        return await self.doc_client.read_resource("docs://documents")
    
    async def get_doc_content(self, doc_id: str) -> str:
        """Retrieves the content of a specific document by its ID."""
        return await self.doc_client.read_resource(f"docs://documents/{doc_id}")
    
    async def get_prompt(self, command: str, doc_id: str) -> List[PromptMessage]:
        """Retrieves a specific prompt based on the command and document ID."""
        return await self.doc_client.get_prompt(command, {"doc_id": doc_id})
    
    async def _extract_resources(self, query: str) -> str:
        """Extracts document resources mentioned in the query."""
        mentions = [word[-1] for word in query.split() if word.startswith("@")]
        doc_ids = await self.list_docs_ids()
        mentioned_docs: List[Tuple[str, str]] = []
        for doc_id in doc_ids:
            if doc_id in mentions:
                content = await self.get_doc_content(doc_id)
                mentioned_docs.append((doc_id, content))

        return "".join(
            f'\n<document id="{doc_id}>\n{content}\n</document>\n'
            for doc_id, content in mentioned_docs
        )
    
    async def _process_command(self, query: str) -> bool:
        """Processes commands in the query that start with a slash."""
        if not query.startswith("/"):
            return False
        
        words = query.split()
        command = words[0].replace("/", "")
        
        messages = await self.doc_client.get_prompt(command, {"doc_id": words[1]})
        self.messages += convert_prompt_messages_to_message_params(messages)
        
        return True
    
    async def _process_query(self, query: str):
        """Processes the user query, extracting resources and handling commands."""
        if await self._process_command(query):
            return
        
        resources = await self._extract_resources(query)
        prompt = f"""
        The user has a question:
        <query>
        {query}
        </query>

        The following context may be useful in answering their question:
        <context>
        {resources}
        </context>

        Note the user's query might contain references to documents like "@report.docx". The "@" is only
        included as a way of mentioning the doc. The actual name of the document would be "report.docx".
        If the document content is included in this prompt, you don't need to use an additional tool to read the document.
        Answer the user's question directly and concisely. Start with the exact information they need. 
        Don't refer to or mention the provided context in any way - just use it to inform your answer.
        """

        self.messages.append({"role": "user", "content": prompt})
    
def convert_prompt_messages_to_message_param(prompt_message: "PromptMessage") -> MessageParam:
    """Converts a PromptMessage to a MessageParam."""
    role = 'user' if prompt_message.role == 'user' else 'assistant'
    content = prompt_message.content

    if isinstance(content, dict) or hasattr(content, '__dict__'):
        content_type = (content.get('type') if isinstance(content, dict) else getattr(content, 'type', None))
        if content_type == 'text':
            content_text = content.get('text') if isinstance(content, dict) else getattr(content, 'text', '')

            return {"role": role, "content": content_text}
    
    if isinstance(content, list):
        text_blocks = []
        for item in content:
            if isinstance(item, dict) or hasattr(item, '__dict__'):
                item_type = (item.get('type') if isinstance(item, dict) else getattr(item, 'type', None))
                if item_type == 'text':
                    item_text = item.get('text') if isinstance(item, dict) else getattr(item, 'text', '')
                    text_blocks.append({"type": "text", "text": item_text})

        if text_blocks:
            return {"role": role, "content": text_blocks}
        
    return {"role": role, "content": ''}

def convert_prompt_messages_to_message_params(
    prompt_messages: List[PromptMessage],
) -> List[MessageParam]:
    return [
        convert_prompt_messages_to_message_param(msg) for msg in prompt_messages
    ]
