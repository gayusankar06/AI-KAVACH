import { useEffect, useRef, useState } from 'react'
import { apiChat, apiChatHistory } from '../api.js'

export default function AIChat({ user }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const bottomRef = useRef(null)

  useEffect(() => {
    apiChatHistory(user.id)
      .then((data) => setMessages(data.messages || []))
      .catch(() => setMessages([]))
  }, [user.id])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, busy])

  async function handleSend(e) {
    e.preventDefault()
    const text = input.trim()
    if (!text || busy) return
    setInput('')
    setError('')
    setBusy(true)
    setMessages((m) => [...m, { role: 'user', content: text }])
    try {
      const data = await apiChat(user.id, text)
      setMessages((m) => [...m, { role: 'assistant', content: data.reply }])
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <h1>AI Chatbox</h1>
        <p className="muted">
          Connected to Ollama — model{' '}
          <code>llama3.2:3b</code>. Ask questions and get AI-powered security
          insights.
        </p>
      </header>

      {error && <div className="error">{error}</div>}

      <section className="panel chat-panel">
        <div className="chat-log">
          {messages.length === 0 && (
            <p className="muted">
              Start a conversation below. History is saved to the database.
            </p>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`chat-msg ${m.role}`}>
              {m.content}
            </div>
          ))}
          {busy && <div className="chat-msg assistant">Thinking...</div>}
          <div ref={bottomRef} />
        </div>
        <form className="chat-form" onSubmit={handleSend}>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask the AI assistant..."
            disabled={busy}
          />
          <button type="submit" disabled={busy}>
            {busy ? 'Sending...' : 'Send'}
          </button>
        </form>
      </section>
    </div>
  )
}