import { useState } from 'react';
import { Switch, FormControlLabel, FormGroup, Typography } from '@mui/material';
import styled from 'styled-components'
import EnhancedChatBot from './components/enhanced_design/EnhancedChatBot';
import Header from './components/Header'
import Footer from './components/Footer'


const ToggleContainer = styled.div`
  margin-bottom: 1em;
  display: flex;
  flex-direction: column;
  align-items: center;
`;


const AppContainer = styled.div`
  display: flex;
  flex-direction: column;
  min-height: 100vh;
`

const MainContent = styled.main`
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px;
`

const ChatBotContainer = styled.div`
  width: 800px; /* Increased from default width */
  max-width: 90vw; /* Responsive - won't exceed 90% of viewport width */
`;


function App() {
  const [useDE, setUseDE] = useState(false);

  const handleToggleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setUseDE(event.target.checked);
  };


  return (
    
     <AppContainer>
        <Header />  
         <MainContent>
        <div style={{ display: 'flex', justifyContent: 'center' }}>
          <ChatBotContainer>
            <div style={{ marginBottom: '1em' }}>
            <ToggleContainer>
              <Typography variant="caption" color="textSecondary" gutterBottom>
                Use this toggle to allow this bot to leverage your corporate decision services.
              </Typography>
              <FormGroup>
                <FormControlLabel
                  control={
                    <Switch
                      checked={useDE}
                      onChange={handleToggleChange}
                      name="decisionServices"
                      color="primary"
                      size="small"
                    />
                  }
                  label={useDE ? "Use Decision Services" : "Do not use Decision Services"}
                />
              </FormGroup>
            </ToggleContainer>
            </div>
            <EnhancedChatBot useDE={useDE} />
          </ChatBotContainer>
        </div>
        </MainContent>
      <Footer />
      </AppContainer>
   
  );
}

export default App;
