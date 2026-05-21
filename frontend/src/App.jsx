import { useState } from 'react'
import './App.css'

function App() {
  const [file, setFile] = useState(null)
  const [videoUrl, setVideoUrl] = useState(null)
  const [tracks, setTracks] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    if (!file) return
    setError(null)
    setLoading(true)
    try {
      const form = new FormData()
      form.append('video', file)
      const res = await fetch('http://localhost:8000/track', { method: 'POST', body: form })
      if (!res.ok) throw new Error(`Server error: ${res.status}`)
      const data = await res.json()
      setVideoUrl(data.video_url)
      setTracks(data.tracks)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input type="file" accept="video/*" onChange={(e) => setFile(e.target.files[0])} />
        <button type="submit" disabled={!file || loading}>
          {loading ? 'Processing...' : 'Upload'}
        </button>
      </form>
      {loading && <p>Processing... this may take a minute.</p>}
      {error && <pre>Error: {error}</pre>}
      {videoUrl && <video src={videoUrl} controls />}
      {tracks && (
        <table>
          <thead>
            <tr>
              <th>Track ID</th>
              <th>Label</th>
              <th>Time on screen (s)</th>
            </tr>
          </thead>
          <tbody>
            {tracks.map((t) => (
              <tr key={t.track_id}>
                <td>{t.track_id}</td>
                <td>{t.label}</td>
                <td>{t.time_on_screen_s}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

export default App
