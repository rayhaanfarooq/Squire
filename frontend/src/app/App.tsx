import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { router } from './router'
import Layout from '../components/Layout'

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          {router.map((route) => (
            <Route
              key={route.path}
              path={route.path}
              element={<route.component />}
            />
          ))}
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}

export default App

