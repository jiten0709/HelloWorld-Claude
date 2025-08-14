try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception as e:
    print(f"Error loading .env file: {e}")

import os
from anthropic import AsyncAnthropic
from mcp import StdioServerParameters, ClientSession
from mcp.types import (
    SamplingMessage,
    CreateMessageRequestParams,
    TextContent,
    CreateMessageResult,
)
from mcp.client.session import RequestContext
from mcp.client.stdio import stdio_client

anthropic_client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-3-5-haiku-20241022"

server_params = StdioServerParameters(
    command="uv",
    args=["run", "server.py"],
)

async def chat(input_messages: list[SamplingMessage], max_tokens=4000):
    messages = []
    for msg in input_messages:
        if msg.role == "user" and msg.content.type == "text":
            content = (
                msg.content.text
                if hasattr(msg.content, "text")
                else str(msg.content)
            )
            messages.append({"role": "user", "content": content})
        elif msg.role == "assistant" and msg.content.type == "text":
            content = (
                msg.content.text
                if hasattr(msg.content, "text")
                else str(msg.content)
            )
            messages.append({"role": "assistant", "content": content})

    response = await anthropic_client.messages.create(
        model=MODEL,
        messages=messages,
        max_tokens=max_tokens,
    )

    text = "".join([p.text for p in response.content if p.type == "text"])
    return text

async def sampling_callback(context: RequestContext, params: CreateMessageRequestParams):
    text = await chat(params.messages)

    return CreateMessageResult(
        role="assistant",
        model=MODEL,
        content=TextContent(type="text", text=text),
    )

async def run(doc):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read_stream=read, write_stream=write, sampling_callback=sampling_callback) as session:
            await session.initialize()
            
            result = await session.call_tool(
                name="summarize",
                arguments={"text_to_summarize": doc},
            )
            print(f"Result: {result.content}")

if __name__ == "__main__":
    import asyncio
    doc = """
    # [cite_start]Jiten Parmar [cite: 4]
    AI/ML Engineer | [cite_start]Backend Developer [cite: 5]
    [cite_start][parmar.jiten03@gmail.com](mailto:parmar.jiten03@gmail.com) [cite: 3] | [cite_start]+91 84528 84426 [cite: 1] | [cite_start]Mumbai, India [cite: 2] | [cite_start]LinkedIn [cite: 6] | [cite_start]GitHub [cite: 6]

    [cite_start]Results-driven AI/ML Engineer specializing in production-ready ML systems and intelligent applications with strong back-end development expertise[cite: 7]. [cite_start]Experienced in CNN models, RAG pipelines and generative Al solutions using TensorFlow, LangChain, and cloud platforms (GCP, AWS) to deliver enterprise-grade Al applications and scalable intelligent services[cite: 8].

    ---
    ### [cite_start]**SKILLS** [cite: 9]
    * [cite_start]**AI/ML & Data** [cite: 10][cite_start]: Al Agents, Generative AI, TensorFlow, PyTorch, Scikit-learn, LangChain, CNN, RAG, Vector Databases (FAISS, ChromaDB), NLP, LLMS, AI APIS [cite: 11]
    * [cite_start]**Backend & Cloud** [cite: 13][cite_start]: Python, Flask, Django, Node.js, JavaScript, TypeScript, GCP, AWS, Docker, Kubernetes [cite: 12]
    * [cite_start]**Data & Tools** [cite: 14][cite_start]: PostgreSQL, MongoDB, Version Control (Git), RESTful APIs, Microservices [cite: 12]

    ---
    ### [cite_start]**TECHNICAL EXPERIENCE** [cite: 15]

    [cite_start]**Google for Developers AI/ML (Virtual Internship)** [cite: 16] | [cite_start]All India Council For Technical Education [cite: 17]
    [cite_start]*Oct 2024 - Dec 2024* [cite: 23]
    * [cite_start]Engineered 3+ production-ready ML models using TensorFlow and AutoML on Google Cloud Platform[cite: 18].
    * [cite_start]Learned fundamental concepts of image classification, object detection, product image search[cite: 19].

    [cite_start]**Google Cloud services Generative AI (Virtual Internship)** [cite: 20] | [cite_start]All India Council For Technical Education [cite: 21]
    [cite_start]*July 2024 - Sept 2024* [cite: 24]
    * [cite_start]Built 4+ generative Al applications using Vertex Al and Gemini models[cite: 22].
    * [cite_start]Gained hands-on experience with GCP services for generative AI, such as Gemini and Vertex AI, including language models, image generation, and more[cite: 25].

    [cite_start]**Trainee Programmer** [cite: 26] | Chintan Systems Pvt. [cite_start]Ltd. [cite: 27]
    * [cite_start]Architected comprehensive API documentation covering 30+ endpoints, reducing integration time by 45%[cite: 28].
    * [cite_start]Defined payload specifications and response schemas that reduced integration time[cite: 29].

    ---
    ### [cite_start]**PROJECTS** [cite: 30]

    [cite_start]**TestRAGic** [cite: 31] | [cite_start]Al-Powered QA Automation Platform [cite: 32]
    *Dec 2023 - Jan 2024 | [cite_start]Mumbai, India* [cite: 33]
    * [cite_start]Developed intelligent test generation system using Python, LangChain, and OpenAI GPT-4 that automatically converts video content into executable test cases, reducing manual test creation time by 75%[cite: 34].
    * [cite_start]Implemented RAG pipeline with vector databases (FAISS/ChromaDB) [cite: 35] [cite_start]and integrated Playwright for multibrowser automation, enabling end-to-end testing workflow from content ingestion to comprehensive reporting[cite: 36].
    * [cite_start]**Technologies**: Python, LangChain, OpenAI GPT-4, RAG, FAISS, ChromaDB, Playwright, Streamlit, Plotly[cite: 37].

    [cite_start]**Dermalyse** [cite: 38] | [cite_start]AI-Powered Medical Diagnostic Tool [cite: 39]
    * [cite_start]Architected CNN model achieving 90% accuracy in classifying 15 categories of skin diseases[cite: 40]. [cite_start]ML pipeline engineered with TensorFlow for model training and inference optimization[cite: 41].
    * [cite_start]Reduced misdiagnosis rate by 35% compared to baseline models in preliminary tests[cite: 42].
    * [cite_start]**Technologies**: Python, TensorFlow, CNN, Flask API, ngrok, PostgreSQL[cite: 43].

    ---
    ### [cite_start]**EDUCATION** [cite: 44]

    **BTech. in Computer Engineering** | [cite_start]Shah & Anchor Kutchhi Engineering College - Secured CGPA: 8.17 [cite: 45]
    [cite_start]*2021 - 2025* [cite: 47]

    **HSC (12th)** | [cite_start]SVKM's Mithibai College HSC (12th) - Secured 82.33% [cite: 46]
    [cite_start]*2019 - 2021* [cite: 48]

    ---
    ### [cite_start]**CERTIFICATIONS** [cite: 6]
    [cite_start]*The resume indicates certifications are available and provides links to GitHub and LinkedIn.* [cite: 6]
    """
    asyncio.run(run(doc))
