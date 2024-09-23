"use client";

import React, { useState, useEffect, useRef } from 'react';
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Skeleton } from "@/components/ui/skeleton"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

// Dummy conversation data
const dummyConversation = [
  { role: 'assistant', content: 'Hello! How can I assist you today?' },
  { role: 'user', content: 'I have a question about my contract.' },
  { role: 'assistant', content: 'Of course! I\'d be happy to help. What specific aspect of your contract would you like to discuss?' },
  { role: 'user', content: 'I\'m not sure about the credit period mentioned in the contract.' },
  { role: 'assistant', content: 'I understand. The credit period typically refers to the time frame within which payment is due after the delivery of goods or services. In your contract, you can usually find this information in the payment terms section. Could you please check that section and let me know what it says?' },
  { role: 'user', content: "It says Net 30, but I'm not sure what that means." },
  { role: 'assistant', content: 'Ah, I see. "Net 30" is a common term in business contracts. It means that the full payment is due within 30 days of the invoice date. So, if you receive an invoice on July 1st, the payment would be due by July 31st. Is there anything else about the credit period youd like to know?' },
];

// Frequently asked questions
const faqs = [
  "What does the SOW value include?",
  "How is the COLA (Cost of Living Adjustment) calculated?",
  "Can you explain the sub-contract clause?",
  "What's the difference between inclusive and exclusive GST?"
];

export default function ChatPage() {
  const [conversation, setConversation] = useState(dummyConversation);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showFAQs, setShowFAQs] = useState(true);
  
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [conversation]);

  const handleSendMessage = () => {
    if (inputMessage.trim() === '') return;

    setConversation(prev => [...prev, { role: 'user', content: inputMessage }]);
    setInputMessage('');
    setIsLoading(true);
    setShowFAQs(false);

    // Simulate API call
    setTimeout(() => {
      setConversation(prev => [...prev, { role: 'assistant', content: "Thank you for your question. I'm processing it and will respond shortly." }]);
      setIsLoading(false);
    }, 1500);
  };

  const handleNewConversation = () => {
    setConversation([]);
    setShowFAQs(true);
  };

  const handleFAQClick = (question: string) => {
    setConversation([{ role: 'user', content: question }]);
    setShowFAQs(false);
    setIsLoading(true);

    // Simulate API call
    setTimeout(() => {
      setConversation(prev => [...prev, { role: 'assistant', content: `Here's some information about "${question}". [Detailed answer would be provided here]` }]);
      setIsLoading(false);
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <span className="text-2xl font-bold text-gray-900">Contract Assistant</span>
              </div>
            </div>
            <div className="flex items-center">
              <Button onClick={handleNewConversation}>New Conversation</Button>
            </div>
          </div>
        </div>
      </nav>

      <main className="flex-grow container mx-auto py-6 sm:px-6 lg:px-8">
        <div className="bg-white shadow-xl rounded-lg overflow-hidden flex flex-col h-[calc(100vh-7rem)]">
          <ScrollArea className="flex-grow p-4" ref={scrollAreaRef}>
            {showFAQs ? (
              <div className="space-y-4">
                <h2 className="text-xl font-semibold">Frequently Asked Questions</h2>
                {faqs.map((faq, index) => (
                  <Button 
                    key={index} 
                    variant="outline" 
                    className="w-full justify-start text-left h-auto py-2"
                    onClick={() => handleFAQClick(faq)}
                  >
                    {faq}
                  </Button>
                ))}
              </div>
            ) : (
              conversation.map((message, index) => (
                <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} mb-4`}>
                  <div className={`flex items-start ${message.role === 'user' ? 'flex-row-reverse' : ''}`}>
                    <Avatar className="w-8 h-8">
                      <AvatarImage src={message.role === 'user' ? "/user-avatar.png" : "/assistant-avatar.png"} />
                      <AvatarFallback>{message.role === 'user' ? 'U' : 'A'}</AvatarFallback>
                    </Avatar>
                    <div className={`mx-2 p-3 rounded-lg ${message.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}>
                      {message.content}
                    </div>
                  </div>
                </div>
              ))
            )}
            {isLoading && (
              <div className="flex justify-start mb-4">
                <div className="flex items-start">
                  <Avatar className="w-8 h-8">
                    <AvatarImage src="/assistant-avatar.png" />
                    <AvatarFallback>A</AvatarFallback>
                  </Avatar>
                  <Skeleton className="h-10 w-40 mx-2" />
                </div>
              </div>
            )}
          </ScrollArea>
          <div className="p-4 border-t">
            <form onSubmit={(e) => { e.preventDefault(); handleSendMessage(); }} className="flex space-x-2">
              <Input 
                value={inputMessage} 
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Type your message here..."
                className="flex-grow"
              />
              <Button type="submit">Send</Button>
            </form>
          </div>
        </div>
      </main>
    </div>
  );
}