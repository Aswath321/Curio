import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, Mail, Calendar, Bell, Image, Github, ShoppingCart, Globe, Search, Newspaper, Linkedin, Youtube, Coffee } from 'lucide-react';

const cards = [
  { icon: Mail, title: "Email Management", description: "Send emails and retrieve mails", prompt: "Give me last 5 unread mails" },
  { icon: Calendar, title: "Schedule Management", description: "Schedule meetings and view events", prompt: "Schedule a team meeting for next Monday at 2 PM" },
  { icon: Bell, title: "Reminders", description: "Add and view reminders with priority levels", prompt: "Add a high priority reminder for project deadline on Friday" },
  { icon: Image, title: "Image Analysis", description: "Ask questions about shared photos", prompt: "Analyze this image and tell me what you see" },
  { icon: Github, title: "GitHub Management", description: "Manage your GitHub account and repositories", prompt: "Create a new GitHub repo named 'my-project'" },
  { icon: ShoppingCart, title: "Amazon Web Scraping", description: "Get product info from Amazon", prompt: "Get info on the latest iPhone model from Amazon" },
  { icon: Globe, title: "Web Scraping", description: "Scrape and search websites", prompt: "Scrape today's headlines from CNN.com" },
  { icon: Search, title: "Web Searching", description: "Get up-to-date information", prompt: "What are the latest developments in AI?" },
  { icon: Newspaper, title: "News Updates", description: "Get news based on categories", prompt: "Give me the latest technology news" },
  { icon: Linkedin, title: "LinkedIn Automation", description: "Automate content posting on LinkedIn", prompt: "Draft a LinkedIn post about our new product launch" },
  { icon: Youtube, title: "YouTube Search", description: "Search videos and get transcripts", prompt: "Get a summary of the latest TED Talk" },
  { icon: Coffee, title: "Recipe Finder", description: "Get recipes for dishes", prompt: "What's the recipe for chocolate chip cookies?" }
];

const WelcomeSection = () => {
  const [startIndex, setStartIndex] = useState(0);
  const [animation, setAnimation] = useState(""); // State to track animation class

  const visibleCards = 4; // Number of visible cards at a time
  const slideAmount = 3; // Number of cards to slide at a time

  const nextSlide = () => {
    setAnimation("slide-right"); // Apply slide-right animation
    setStartIndex((prevIndex) => (prevIndex + slideAmount) % cards.length);
  };

  const prevSlide = () => {
    setAnimation("slide-left"); // Apply slide-left animation
    setStartIndex((prevIndex) => (prevIndex - slideAmount + cards.length) % cards.length);
  };

  return (
    <div className="welcome-section">
      <h1 className="welcome-title">Welcome to Curio!</h1>
      <p className="welcome-description">Explore the many possibilities with Curio. Here are some features you can try:</p>
      <div className="card-slider">
        <button onClick={prevSlide} className="slider-button"><ChevronLeft /></button>
        <div className={`cards-container ${animation}`}>
          {[0, 1, 2, 3].map((offset) => {
            const card = cards[(startIndex + offset) % cards.length];
            return (
              <div key={offset} className="feature-card">
                <card.icon size={24} />
                <h3>{card.title}</h3>
                <p>{card.description}</p>
                <small>Example: {card.prompt}</small>
              </div>
            );
          })}
        </div>
        <button onClick={nextSlide} className="slider-button"><ChevronRight /></button>
      </div>
    </div>
  );
};

export default WelcomeSection;