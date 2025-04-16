import styled from 'styled-components'
import backgroundImage from '../assets/ZinniaBackground.png'
import companyLogo from '../assets/Zinnialogo.png'

const HeaderContainer = styled.header`
  background-image: url(${backgroundImage});
  background-size: cover;
  background-position: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 16px 0;
`

const Nav = styled.nav`
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
`

const Logo = styled.div`
  font-size: 1.5rem;
  font-weight: bold;
  color: white; /* Text color changed to white for better contrast on orange background */
  display: flex;
  align-items: center;
  gap: 15px;
  
  span {
    color: white; /* Changed to white for better visibility */
  }
`

const LogoImage = styled.img`
  height: 40px;
  margin-right: 12px;
`

const Header: React.FC = () => {
  return (
    <HeaderContainer>
      <Nav>
        <Logo>
          <LogoImage src={companyLogo} alt="MAAS.AI Logo" />
          <span>MAAS.AI     </span> Form Validation System
        </Logo>
      </Nav>
    </HeaderContainer>
  )
}

export default Header