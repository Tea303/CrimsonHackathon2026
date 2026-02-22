import voice_module

def chat_with_user(user_input):
    # This is what Gemini would normally say
    ai_text = "Substitute onions with shallots or leeks." 
    
    # This calls your voice_module.py logic
    voice_module.speak(ai_text)

print("Chatbot is ready!")

# ADD THIS LINE AT THE VERY BOTTOM:
chat_with_user("test input")