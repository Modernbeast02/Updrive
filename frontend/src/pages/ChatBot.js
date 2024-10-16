import React, { useState, useRef, useEffect } from "react";
import { FaUser, FaPaperPlane } from "react-icons/fa";

const ChatBot = (props) => {
  const initialMessages = [
    {
      id: 1,
      user: "Alice",
      text: "Hey team, how's the website deployment going?",
      timestamp: "10:00 AM",
    },
    {
      id: 2,
      user: "Bob",
      text: "We're making progress. The backend is up and running.",
      timestamp: "10:05 AM",
    },
    {
      id: 3,
      user: "Charlie",
      text: "Frontend is almost ready. Just fixing some responsive issues.",
      timestamp: "10:10 AM",
    },
    {
      id: 4,
      user: "Diana",
      text: "Great! I'll start preparing the documentation.",
      timestamp: "10:15 AM",
    },
  ];

  const [messages, setMessages] = useState(initialMessages);
  const [inputMessage, setInputMessage] = useState("");
  const [error, setError] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleInputChange = (e) => {
    setInputMessage(e.target.value);
    setError("");
    setIsTyping(true);
    setTimeout(() => setIsTyping(false), 1000);
  };

  const handleSendMessage = () => {
    if (inputMessage.trim() === "") {
      setError("Please enter a message");
      return;
    }
    const newMessage = {
      id: messages.length + 1,
      user: "You",
      text: inputMessage,
      timestamp: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };
    setMessages([...messages, newMessage]);
    setInputMessage("");
    setError("");
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      handleSendMessage();
    }
  };

  const handleOptionClick = (id, option) => {
    if (option === "Reply") {
      const messageToReply = messages.find((msg) => msg.id === id);
      setInputMessage(`@${messageToReply.user} `);
    } else if (option === "Delete") {
      setMessages(messages.filter((msg) => msg.id !== id));
    }
  };

  return (
    <>
      <div className="flex justify-center items-center -mb-16 mt-12 text-lg">
        {props.fileName} Ankur.pdf
      </div>
      <div className=" p-4 bg-[#0A1B2E] rounded-lg shadow-lg mt-20 mr-20 ml-20">
        <div className="bg-[#0A1B2E] rounded-lg shadow-inner p-4 overflow-y-auto">
          {messages.map((message) => (
            <div key={message.id} className={`mb-4 animate-fade-in`}>
              <div
                className={`flex ${
                  message.user === "You" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`flex ${
                    message.user === "You" ? "flex-row-reverse" : "flex-row"
                  } items-end`}
                >
                  <div className="w-8 h-8 rounded-full bg-[#0A1B2E] flex items-center justify-center text-[#5A82B8] mr-2">
                    <FaUser />
                  </div>
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      message.user === "You"
                        ? "bg-[#104E8B] text-[#E0F2F1]"
                        : "bg-[#10294D] text-[#C6DCE8] border-[#5A82B8] border"
                    }`}
                  >
                    <p className="font-semibold">{message.user}</p>
                    <p>{message.text}</p>
                    <p className="text-xs text-right mt-1 opacity-75">
                      {message.timestamp}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>
        <div className="mt-4">
          <div className="flex items-center">
            <input
              type="text"
              value={inputMessage}
              onChange={handleInputChange}
              onKeyPress={handleKeyPress}
              className="flex-grow p-2 rounded-l-lg bg-[#0A1B2E] text-[#E0F2F1] border border-[#5A82B8] focus:outline-none focus:ring-2 focus:ring-[#5A82B8]"
              placeholder="Type your message..."
              aria-label="Chat message input"
            />
            <button
              onClick={handleSendMessage}
              className="bg-[#104E8B] text-white p-2 rounded-r-lg hover:bg-[#085B9D] focus:outline-none focus:ring-2 focus:ring-[#5A82B8] ml-2"
              aria-label="Send message"
            >
              <FaPaperPlane />
            </button>
          </div>
          {error && <p className="text-red-500 mt-2">{error}</p>}
        </div>
      </div>
    </>
  );
};

export default ChatBot;
