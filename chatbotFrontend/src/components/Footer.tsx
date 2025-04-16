import styled from 'styled-components'

const FooterContainer = styled.footer`
  background-color: #f8f9fa;
  padding: 16px 0;
  border-top: 1px solid #dee2e6;
  text-align: center;
`

const FooterContent = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  color: #6c757d;
`

const Footer: React.FC = () => {
  return (
    <FooterContainer>
      <FooterContent>
        <p>© 2025 MAAS.AI Form Validation System</p>
      </FooterContent>
    </FooterContainer>
  )
}

export default Footer