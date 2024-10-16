import React from "react";
import { useState } from "react";
import styles from "../styles/Chat.module.css";

const ChatBot = (props) => {
  const [selectedOption, setSelectedOption] = useState(null);
  const [isChatStarted, setIsChatStarted] = useState(false);
  const [messages, setMessages] = useState([]);

  const options = [
    "What's your purpose?",
    "How can I get started?",
    "Tell me a joke!",
    "Help with documentation",
    "What are your features?",
  ];

  const startConversation = (option) => {
    setSelectedOption(option);
    setIsChatStarted(true);
    setMessages((prev) => [...prev, { type: "user", text: option }]);

    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        { type: "bot", text: `Bot: Received your message - "${option}"` },
      ]);
    }, 1000);
  };

  return (
    <div className={styles.chatContainer}>
      <div className={styles.chatBox}>
        {!isChatStarted ? (
          <div className={styles.options}>
            {options.map((option, index) => (
              <div
                key={index}
                className={`${styles.option} ${
                  selectedOption && selectedOption !== option
                    ? styles.fadeOut
                    : ""
                }`}
                onClick={() => startConversation(option)}
              >
                {option}
              </div>
            ))}
          </div>
        ) : null}

        <div className={styles.chatContent}>
          {messages.map((message, index) => (
            <div
              key={index}
              className={`${styles.message} ${
                message.type === "bot" ? styles.botMessage : styles.userMessage
              }`}
            >
              {message.text}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ChatBot;
