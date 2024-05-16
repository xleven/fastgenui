import * as hub from "langchain/hub";
import { Client } from "langsmith";
import { LangChainTracer } from "langchain/callbacks";
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { ChatOpenAI } from "@langchain/openai";


export async function onRequestPost(context) {
  try {
    const tracer = new LangChainTracer(
      {
        client: new Client({ apiKey: context.env.LANGCHAIN_API_KEY }),
        projectName: context.env.LANGCHAIN_PROJECT,
      }
    );
    const prompt = await hub.pull<ChatPromptTemplate>("xleven/fastgenui");
    const llm = new ChatOpenAI(
      {
        model: "llama3-70b-8192",
        temperature: 0.2,
        apiKey: context.env.OPENAI_API_KEY,
      },
      {
        baseURL: context.env.OPENAI_API_BASE,
      }
    );
    const body = await context.request.formData();
    const message = body.get("message");
    const resp = await prompt.pipe(llm).invoke(
      {
        "message": message
      },
      {
        callbacks: [tracer],
      }
    );
    const match = resp.content.toString().match(new RegExp("<htmlresponse>(.*?)<\/htmlresponse>", "s"));
    const snippet = match ? match[0] : "";
    const html = `<div class="bg-gray-200 rounded-lg p-3 self-start max-w-[75%]">${snippet}</div>`
    return new Response(html);
  } catch (error) {
    return new Response(`<div class="bg-gray-200 rounded-lg p-3 self-start max-w-[75%]">${error}</div>`);
  }
}