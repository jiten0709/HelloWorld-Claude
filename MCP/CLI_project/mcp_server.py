import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

from mcp.server.fastmcp import FastMCP
from pydantic import Field
from mcp.server.fastmcp.prompts import base

mcp = FastMCP(name="Document MCP", log_level="ERROR")
logger.info("Starting Document MCP server...")

DOCS = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}

# ======== tools ========

@mcp.tool(
    name="read_doc_contents",
    description="Read the contents of a document and return it as a string.",
)
def read_document(doc_id: str):
    logger.info(f"Reading document with ID: {doc_id}")
    if doc_id not in DOCS:
        raise ValueError(f"Document with id '{doc_id}' not found.")
    
    return DOCS[doc_id]

@mcp.tool(
    name="edit_document",
    description="Edit a document by replacing a string in the document's content with a new string.",
)
def edit_document(doc_id: str, old_str: str, new_str: str):
    logger.info(f"Editing document with ID: {doc_id}, replacing '{old_str}' with '{new_str}'")
    if doc_id not in DOCS:
        raise ValueError(f"Document with id '{doc_id}' not found.")
    
    DOCS[doc_id] = DOCS[doc_id].replace(old_str, new_str)

    return f"Document '{doc_id}' updated successfully."

# ======== resources ========

@mcp.resource(
        uri="docs://documents",
        mime_type="application/json",
)
def list_docs() -> list[str]:
    logger.info("Listing all document IDs.")

    return list(DOCS.keys())

@mcp.resource(
    uri="docs://documents/{doc_id}",
    mime_type="text/plain",
)
def fetch_doc(doc_id: str):
    logger.info(f"Fetching document with ID: {doc_id}")
    if doc_id not in DOCS:
        raise ValueError(f"Document with id '{doc_id}' not found.")
    
    return DOCS[doc_id]

# ======== prompts ========

@mcp.prompt(
    name="format_document",
    description="Rewrite the contents of the document in markdown format.",
)
def format_document(
    doc_id: str = Field()
) -> list[base.Message]:
    prompt = f"""
    Your goal is to reformat a document to be written with markdown syntax.

    The id of the document you need to reformat is:
    <document_id>
    {doc_id}
    </document_id>

    Add in headers, bullet points, tables, etc as necessary. Feel free to add in extra text, but don't change the meaning of the report.
    Use the 'edit_document' tool to edit the document. After the document has been edited, respond with the final version of the doc. Don't explain your changes.
    """
    logger.info(f"Formatting document with ID: {doc_id}")

    return [base.UserMessage(prompt)]

if __name__ == "__main__":
    mcp.run(transport="stdio")
