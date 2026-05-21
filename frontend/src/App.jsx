import { useState } from 'react'
import './App.css'

function App() {
  const [file, setFile] = useState(null)
  const [videoUrl, setVideoUrl] = useState(null)
  const [tracks, setTracks] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const [percent, setPercent] = useState(0)

  async function handleSubmit(e) {
    e.preventDefault()
    if (!file) return
    setError(null)
    setVideoUrl(null)
    setTracks(null)
    setPercent(0)
    setLoading(true)

    try {
      const form = new FormData()
      form.append('video', file)
      const res = await fetch('http://localhost:8000/track', { method: 'POST', body: form })
      if (!res.ok) throw new Error(`Server error: ${res.status}`)

      await new Promise((resolve, reject) => {
        const interval = setInterval(async () => {
          try {
            const pollRes = await fetch('http://localhost:8000/track')
            const data = await pollRes.json()

            if (data.percent !== undefined) setPercent(data.percent)

            if (data.status === 'done') {
              clearInterval(interval)
              setVideoUrl(data.result.video_url)
              setTracks(data.result.tracks)
              resolve()
            } else if (data.status === 'error') {
              clearInterval(interval)
              reject(new Error(data.message || 'Processing failed'))
            }
          } catch (err) {
            clearInterval(interval)
            reject(err)
          }
        }, 500)
      })
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
      {loading && <progress value={percent} max={100} />}
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
