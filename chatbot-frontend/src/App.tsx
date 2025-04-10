import { useState } from 'react';

import {
  Header, SkipToContent, HeaderName, Content, Theme, Toggle,
} from '@carbon/react';

import ChatBot from './components/ChatBot/ChatBot';

function App() {
  const [useDE, setUseDE] = useState(false);

  return (
    <>
      <Theme theme="g100">
        <Header aria-label="Chatbot">
          <SkipToContent />
          <HeaderName href="#" prefix="">
            Zinnia Rule Validation ChatBot
          </HeaderName>
        </Header>
      </Theme>
      <Content>
        <div style={{ display: 'flex', justifyContent: 'center' }}>
          <div>
            <div style={{ marginBottom: '1em' }}>
              <Toggle
                id="de-toggle"
                labelA="Do not use Decision Services"
                labelB="Use Decision Services"
                labelText="Use this toggle to allow this bot to leverage your corporate decision services."
                size="sm"
                onToggle={(checked) => setUseDE(checked)}
              />
            </div>
            <ChatBot useDE={useDE} />
          </div>
        </div>
      </Content>
    </>
  );
}

export default App;
