import { Component, StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import LoginPage from './components/LoginPage.jsx'
import Home from './components/home.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>

   <Home></Home>
   
  </StrictMode>,
)
