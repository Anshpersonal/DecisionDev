
interface APIMessage {
  input: string,
  output: string,
  type: string,
  message:string,
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

export async function uploadPdf(file: File, prompt?: string): Promise<any> {
  // Initialize conversation ID if not already set
  if (!currentConversationId) {
    await initializeConversation();
  }
  console.log("0.1")
  const baseUrl = import.meta.env.VITE_API_URL;
  let url = `${baseUrl}/rule-agent/upload_pdf?conversationId=${currentConversationId}`;
  console.log("0.3")
  // Add prompt to the URL if provided
  if (prompt && prompt.trim()) {
    url += `&prompt=${encodeURIComponent(prompt.trim())}`;
  }
  
  const formData = new FormData();
  // Change 'file' to 'form_file' to match what the backend expects
  formData.append('form_file', file);
  console.log(url)
  try {
    const response = await fetch(url, {
      method: 'POST',
      mode: 'cors',
      // Remove this header - it should be set by the server, not the client
      // headers: {
      //   'Access-Control-Allow-Origin': '*',
      // },
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error(`Upload failed with status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error uploading PDF:', error);
    throw error;
  }
}