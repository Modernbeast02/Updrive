import React, { useState, useRef, useEffect } from "react";
import { FaUser, FaPaperPlane } from "react-icons/fa";
import { useRouter } from "next/router";
const ChatBot = (props) => {
  const [processedString, setProcessedString] = useState("");
  const initialMessages = [
    {
      id: 1,
      user: "Bot",
      text: "Hey! Ask me a question.",
      timestamp: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
    },
  ];
  const startingButtons = [
    {
      id: 1,
      text: "Ask me about PDFs",
      user: "Bot",
    },
    {
      id: 2,
      text: "What is a Smart PDF Companion?",
      user: "Bot",
    },
    {
      id: 3,
      text: "How to upload a PDF? just writing this random msg to increase length hehe",
      user: "Bot",
    },
    {
      id: 4,
      text: "PDF features",
      user: "Bot",
    },
    {
      id: 5,
      text: "Need help with a question",
      user: "Bot",
    },
  ];

  const router = useRouter();
  const { query } = router;
  const param1 = query.name;
  const [messages, setMessages] = useState(initialMessages);
  const [inputMessage, setInputMessage] = useState("");
  const [error, setError] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const chatEndRef = useRef(null);

  const fetchProcessedString = async () => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/query?input_string=${inputMessage}`);
      const data = await response.json();
      setProcessedString(data.result);

      // Add the processed string as a new message from the Bot
      const botResponseMessage = {
        id: messages.length + 1,
        user: "Bot",
        text: data.result,
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
        citations:['Yes', 'No']
      };
      setMessages((prevMessages) => [...prevMessages, botResponseMessage]);
    } catch (error) {
      console.error('Error fetching processed string:', error);
    }
  };
  const fetchCitations = async () => {
    // try {
    //   const response = await fetch(`http://127.0.0.1:5000/citation`);
    // } catch (error) {
    //   console.error('Error fetching processed string:', error);
    // }
      try {
        const response = await fetch('http://127.0.0.1:5000/citation');

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        // Get the response as a Blob
        const blob = await response.blob();

        // Create a link element
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = 'citation.pdf'; // specify the desired file name

        // Append to the body (needed for Firefox)
        document.body.appendChild(link);

        // Trigger the download
        link.click();

        // Clean up and remove the link
        document.body.removeChild(link);
        URL.revokeObjectURL(link.href); // free up memory
    } catch (error) {
        console.error('There was a problem with the fetch operation:', error);
    }
  };

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

  const handleSendMessage = async () => {
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
    await fetchProcessedString();
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
        {param1}
      </div>

      <div className=" p-4 bg-[#0A1B2E] rounded-lg shadow-lg mt-20 mr-20 ml-20">
        <div className="bg-[#0A1B2E] rounded-lg shadow-inner p-4 min-h-[500px] overflow-y-auto">
          {initialMessages.map((message) => (
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
              {message.citations && (
                <div className="flex justify-start mt-2">
                  <p className="text-md text- white text-right mt-1 mr-2 opacity-75">
                    Do You want Citations?
                  </p>
                  <button
                    className="bg-green-500 text-white rounded px-4 py-1 mr-2"
                    onClick={fetchCitations}
                  >
                    Yes
                  </button>
                  <button className="bg-red-500 text-white rounded px-4 py-1">
                    No
                  </button>
                </div>
              )}
            </div>
          ))}
          <div className="flex-col  mb-4">
            {startingButtons.map((button) => (
              <div className="ml-10 mb-4 w-[450px]">
                <button
                  key={button.id}
                  onClick={() => handleButtonClick(button.text)}
                  className="bg-[#0A1B2E] w-[450px] text-[#5A82B8] border-[#5A82B8] border px-4 py-2 rounded-lg hover:scale-[1.05] duration-300"
                >
                  {button.text}
                </button>
              </div>
            ))}
          </div>
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
