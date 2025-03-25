'use client';

import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown, { Components } from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vs } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { AnimatePresence, motion } from 'framer-motion';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  sources?: {
    source: string;
    score: number;
    chunk_size: number;
    chunk_overlap: number;
  }[];
  executedCommands?: {
    command: string;
    splunkLink: string;
    status: 'success' | 'error';
    output: string;
  }[];
}

interface ExecutionPopupProps {
  command: string;
  onClose: () => void;
}

interface ChatInterfaceProps {
  initialMessages?: Message[];
}

const handleExecuteCommand = async (command: string) => {
  // This will be set by the ChatInterface component
  if (window.handleExecuteCommand) {
    window.handleExecuteCommand(command);
  }
};

// Add type declaration for the global function
declare global {
  interface Window {
    handleExecuteCommand?: (command: string) => void;
  }
}

const markdownComponents: Components = {
  h1: ({ children }) => <h1 className="text-xl font-bold mb-4">{children}</h1>,
  h2: ({ children }) => <h2 className="text-lg font-semibold mb-3 mt-4">{children}</h2>,
  h3: ({ children }) => <h3 className="text-md font-semibold mb-2 mt-3">{children}</h3>,
  p: ({ children }) => <p className="mb-4">{children}</p>,
  ul: ({ children }) => <ul className="list-disc pl-6 mb-4">{children}</ul>,
  ol: ({ children }) => <ol className="list-decimal pl-6 mb-4">{children}</ol>,
  li: ({ children }) => <li className="mb-2">{children}</li>,
  a: ({ href, children }) => (
    <a 
      href={href}
      className="text-blue-500 hover:text-blue-600 underline"
      target="_blank"
      rel="noopener noreferrer"
    >
      {children}
    </a>
  ),
  code({ className, children, ...props }) {
    const match = /language-(\w+)/.exec(className || '');
    const codeContent = String(children).replace(/\n$/, '');
    
    // Check if this is a command block by looking for the "command:" prefix before the code block
    const isCommand = codeContent.startsWith('command:');
    const commandContent = isCommand ? codeContent.replace('command:', '').trim() : codeContent;

    return (
      <div className="relative group">
        <div className="rounded-md overflow-hidden mb-4">
          <SyntaxHighlighter
            style={vs}
            language={match?.[1] || 'text'}
            PreTag="div"
            className="text-sm"
          >
            {commandContent}
          </SyntaxHighlighter>
        </div>
        {isCommand && (
          <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            <button
              onClick={() => handleExecuteCommand(commandContent)}
              className="flex items-center space-x-2 px-3 py-1.5 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors shadow-md"
              title="Execute Command"
            >
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                className="h-4 w-4" 
                viewBox="0 0 20 20" 
                fill="currentColor"
              >
                <path 
                  fillRule="evenodd" 
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" 
                  clipRule="evenodd" 
                />
              </svg>
              <span className="text-sm">Run</span>
            </button>
          </div>
        )}
      </div>
    );
  },
  blockquote: ({ children }) => (
    <blockquote className="border-l-4 border-gray-200 pl-4 mb-4 italic">
      {children}
    </blockquote>
  ),
};

const ExecutionPopup: React.FC<ExecutionPopupProps> = ({ command, onClose }) => {
  const [status, setStatus] = useState<'executing' | 'completed'>('executing');
  const [splunkLink, setSplunkLink] = useState<string>('');

  useEffect(() => {
    // Simulate command execution
    const timer = setTimeout(() => {
      setStatus('completed');
      setSplunkLink(`https://splunk.example.com/search?q=search%20command%3D${encodeURIComponent(command)}&earliest=-1h&latest=now`);
    }, 2000);

    return () => clearTimeout(timer);
  }, [command]);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">Command Execution</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div className="space-y-4">
          <div>
            <p className="text-sm text-gray-600 mb-1">Command:</p>
            <code className="block bg-gray-100 rounded p-2 text-sm">{command}</code>
          </div>

          {status === 'executing' ? (
            <div className="flex items-center space-x-2 text-blue-600">
              <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>Executing command...</span>
            </div>
          ) : (
            <div className="space-y-2">
              <div className="flex items-center space-x-2 text-green-600">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span>Command executed successfully</span>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Execution Logs:</p>
                <a
                  href={splunkLink}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 text-sm flex items-center"
                >
                  View logs in Splunk
                  <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </a>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ initialMessages = [] }) => {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  const [executionPopup, setExecutionPopup] = useState<{ show: boolean; command: string }>({ show: false, command: '' });
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Set up the global handler when component mounts
  useEffect(() => {
    window.handleExecuteCommand = (command: string) => {
      setExecutionPopup({ show: true, command });
    };
    return () => {
      delete window.handleExecuteCommand;
    };
  }, []);

  // Load messages from localStorage on client-side only
  useEffect(() => {
    const savedMessages = localStorage.getItem('chatMessages');
    if (savedMessages) {
      setMessages(JSON.parse(savedMessages));
    }
  }, []);

  // Save messages to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('chatMessages', JSON.stringify(messages));
  }, [messages]);

  const handleClearChat = () => {
    setMessages([]);
    localStorage.removeItem('chatMessages');
    setShowClearConfirm(false);
  };

  // Auto-scroll to bottom on new messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Auto-resize textarea
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      inputRef.current.style.height = `${inputRef.current.scrollHeight}px`;
    }
  }, [input]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const newMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input.trim(),
    };

    setMessages(prev => [...prev, newMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:8000/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: newMessage.content }),
      });

      const data = await response.json();
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: data.result,
        sources: data.sources,
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: 'Sorry, there was an error processing your request.',
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-4 py-3 flex justify-between items-center">
        <h1 className="text-xl font-semibold text-gray-800">Platform Support AI</h1>
        <button
          onClick={() => setShowClearConfirm(true)}
          className="px-3 py-1 text-sm text-red-600 hover:text-red-700 hover:bg-red-50 rounded-md transition-colors"
        >
          Clear Chat
        </button>
      </header>

      {/* Confirmation Modal */}
      {showClearConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-sm w-full mx-4">
            <h2 className="text-lg font-semibold mb-4">Clear Chat History</h2>
            <p className="text-gray-600 mb-6">Are you sure you want to clear all chat messages? This action cannot be undone.</p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowClearConfirm(false)}
                className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-md transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleClearChat}
                className="px-4 py-2 text-sm text-white bg-red-600 hover:bg-red-700 rounded-md transition-colors"
              >
                Clear Chat
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Execution Popup */}
      {executionPopup.show && (
        <ExecutionPopup
          command={executionPopup.command}
          onClose={() => setExecutionPopup({ show: false, command: '' })}
        />
      )}

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6">
        <AnimatePresence>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-3xl rounded-lg px-4 py-3 ${
                  message.type === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white border border-gray-200'
                }`}
              >
                <ReactMarkdown components={markdownComponents}>
                  {message.content}
                </ReactMarkdown>

                {message.executedCommands && message.executedCommands.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-gray-200">
                    <h4 className="font-medium mb-2">Command Execution Results:</h4>
                    {message.executedCommands.map((exec, index) => (
                      <div key={index} className="mb-3">
                        <div className="flex items-center justify-between mb-1">
                          <code className="text-sm bg-gray-100 rounded px-2 py-1">{exec.command}</code>
                          <span className={`px-2 py-1 rounded text-xs ${
                            exec.status === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                          }`}>
                            {exec.status}
                          </span>
                        </div>
                        {exec.splunkLink && (
                          <a
                            href={exec.splunkLink}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sm text-blue-600 hover:text-blue-800"
                          >
                            View execution logs in Splunk →
                          </a>
                        )}
                        <pre className="mt-2 text-sm bg-gray-50 rounded p-2 overflow-x-auto">
                          {exec.output}
                        </pre>
                      </div>
                    ))}
                  </div>
                )}

                {/* Sources */}
                {message.sources && (
                  <div className="mt-4 pt-3 border-t border-gray-200 text-sm text-gray-500">
                    <p className="font-medium mb-2">Sources:</p>
                    <ul className="space-y-2">
                      {message.sources.map((source, index) => (
                        <li key={index} className="flex items-center">
                          <span className="mr-2">📄</span>
                          <span>{source.source}</span>
                          <span className="ml-2 px-2 py-1 bg-gray-100 rounded text-xs">
                            relevance: {source.score.toFixed(2)}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <form onSubmit={handleSubmit} className="border-t border-gray-200 bg-white px-4 py-4">
        <div className="flex items-end space-x-4">
          <div className="flex-1">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your question here..."
              className="w-full resize-none rounded-lg border border-gray-300 px-4 py-3 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
              rows={1}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
            />
          </div>
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className={`rounded-lg px-6 py-3 font-medium text-white ${
              isLoading || !input.trim()
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {isLoading ? 'Thinking...' : 'Send'}
          </button>
        </div>
      </form>
    </div>
  );
}; 