import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Bot, User, Sparkles, Loader2, AlertCircle } from 'lucide-react';
import '../styles.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const RAGPanel = ({ ticker }) => {
    const [messages, setMessages] = useState([
        {
            role: 'assistant',
            text: `Hello! I'm your AI analyst for ${ticker}. Ask me anything about the latest news, sentiment, or risks.`
        }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim() || loading) return;

        const userMsg = { role: 'user', text: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        try {
            const response = await fetch(`${API_BASE_URL}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    ticker: ticker,
                    message: userMsg.text
                })
            });

            const data = await response.json();

            if (!response.ok) throw new Error(data.detail || 'Failed to get response');

            setMessages(prev => [...prev, {
                role: 'assistant',
                text: data.response,
                sources: data.sources
            }]);
        } catch (error) {
            setMessages(prev => [...prev, {
                role: 'error',
                text: "Sorry, I encountered an error analyzing the data via RAG. Please check back later."
            }]);
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="rag-chat-container">
            <div className="chat-header">
                <Sparkles size={18} className="text-purple" />
                <h3>AI Market Analyst</h3>
                <span className="badge-pro">BETA</span>
            </div>

            <div className="chat-messages">
                <AnimatePresence>
                    {messages.map((msg, idx) => (
                        <motion.div
                            key={idx}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className={`message-wrapper ${msg.role}`}
                        >
                            <div className="message-icon">
                                {msg.role === 'assistant' ? <Bot size={16} /> : msg.role === 'user' ? <User size={16} /> : <AlertCircle size={16} />}
                            </div>
                            <div className="message-content">
                                <p>{msg.text}</p>
                                {msg.sources && msg.sources.length > 0 && (
                                    <div className="message-sources">
                                        <span>Sources:</span>
                                        {msg.sources.map((source, i) => (
                                            <a key={i} href={source.link} target="_blank" rel="noopener noreferrer" className="source-link">
                                                {source.source || 'News'}
                                            </a>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </motion.div>
                    ))}
                    {loading && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="message-wrapper assistant"
                        >
                            <div className="message-icon"><Bot size={16} /></div>
                            <div className="message-content typing">
                                <Loader2 size={16} className="animate-spin" />
                                Analyzing live market data...
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
                <div ref={messagesEndRef} />
            </div>

            <form onSubmit={handleSend} className="chat-input-area">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder={`Ask about ${ticker}...`}
                    disabled={loading}
                />
                <button type="submit" disabled={!input.trim() || loading} className="send-btn">
                    <Send size={18} />
                </button>
            </form>
        </div>
    );
};

export default RAGPanel;
