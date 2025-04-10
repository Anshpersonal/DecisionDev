/* 
*
*  Copyright 2024 IBM Corp.
*
*  Licensed under the Apache License, Version 2.0 (the "License");
*  you may not use this file except in compliance with the License.
*  You may obtain a copy of the License at
*
*      http://www.apache.org/licenses/LICENSE-2.0
*
*  Unless required by applicable law or agreed to in writing, software
*  distributed under the License is distributed on an "AS IS" BASIS,
*  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
*  See the License for the specific language governing permissions and
*  limitations under the License. 
* 
*/

interface APIMessage {
  input: string,
  output: string,
  type: string,
  conversation_id?: string
}

let currentConversationId: string = '';

// Initialize the conversation
export async function initializeConversation(): Promise<string> {
  const baseUrl = import.meta.env.VITE_API_URL;
  const url = `${baseUrl}/rule-agent/start_conversation`;

  try {
    const response = await fetch(url, {
      mode: 'cors',
      headers: {
        'Access-Control-Allow-Origin': '*',
      },
    });

    const data = await response.json();
    currentConversationId = data.conversation_id;
    return currentConversationId;
  } catch (error) {
    console.error('Error initializing conversation:', error);
    // Generate a fallback ID if the API fails
    currentConversationId = `local-${Date.now()}`;
    return currentConversationId;
  }
}

export async function sendMessage(
  message: string,
  useDecisionEngine: boolean,
): Promise<APIMessage> {
  // Initialize conversation ID if not already set
  if (!currentConversationId) {
    await initializeConversation();
  }

  const endpoint = useDecisionEngine ? 'chat_with_tools' : 'chat_without_tools';
  const searchParams = new URLSearchParams({ 
    userMessage: message,
    conversationId: currentConversationId
  });
  const baseUrl = import.meta.env.VITE_API_URL;
  const url = `${baseUrl}/rule-agent/${endpoint}?${searchParams.toString()}`;

  const response = await fetch(url, {
    mode: 'cors',
    headers: {
      'Access-Control-Allow-Origin': '*',
    },
  });

  const data = (await response.json()) as APIMessage;
  
  // Update the conversation ID if it was returned
  if (data.conversation_id) {
    currentConversationId = data.conversation_id;
  }

  return data;
}

// Reset the conversation
export async function resetConversation(): Promise<void> {
  if (!currentConversationId) {
    // No active conversation to reset
    return;
  }
  
  const baseUrl = import.meta.env.VITE_API_URL;
  const url = `${baseUrl}/rule-agent/reset_memory?conversationId=${currentConversationId}`;
  
  try {
    await fetch(url, {
      method: 'POST',
      mode: 'cors',
      headers: {
        'Access-Control-Allow-Origin': '*',
      },
    });
    
    // Generate a new conversation ID
    await initializeConversation();
  } catch (error) {
    console.error('Error resetting conversation:', error);
    // If reset fails, just generate a new ID
    currentConversationId = `local-${Date.now()}`;
  }
}

// Inspect the memory for debugging
export async function inspectMemory(): Promise<any> {
  if (!currentConversationId) {
    console.error('No active conversation');
    return null;
  }
  
  const baseUrl = import.meta.env.VITE_API_URL;
  const url = `${baseUrl}/rule-agent/inspect_memory?conversationId=${currentConversationId}`;
  
  try {
    const response = await fetch(url, {
      mode: 'cors',
      headers: {
        'Access-Control-Allow-Origin': '*',
      },
    });
    
    return await response.json();
  } catch (error) {
    console.error('Error inspecting memory:', error);
    return null;
  }
}

export default {
  sendMessage,
  initializeConversation,
  resetConversation,
  inspectMemory,
};