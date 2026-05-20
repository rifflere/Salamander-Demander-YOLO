import { useEffect, useState } from 'react'

function App() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch('http://localhost:8000/')
      .then(res => res.json())
      .then(setData)
      .catch(err => setError(err.message))
  }, [])

  if (error) return <pre>Error: {error}</pre>
  if (!data) return <pre>Loading...</pre>

  return <pre>{JSON.stringify(data, null, 2)}</pre>
}

export default App
