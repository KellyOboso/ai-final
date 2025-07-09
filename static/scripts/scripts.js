// Global variable to hold the ID of the current active conversation
let currentConversationId = null;

// Function to load chat history from local storage
function loadChatHistory() {
    const chatHistory = JSON.parse(localStorage.getItem('mentalHealthChatHistory') || '[]');
    const chatbox = $("#chatbox");
    chatbox.empty(); // Clear existing messages

    // Logic specifically for the home page (index.html)
    if (window.location.pathname === '/') {
        if (chatHistory.length === 0) {
            // If no history exists, display the initial bot message from HTML
            const initialBotMessageElement = $(".container #chatbox").find(".bottext span").first();
            if (initialBotMessageElement.length > 0) {
                const initialBotMessageText = initialBotMessageElement.text();
                // Check if the initial bot message has already been saved as a conversation starter
                if (!localStorage.getItem('initialBotMessageSaved')) {
                    // Generate a new conversation ID for this first interaction
                    currentConversationId = Date.now().toString();
                    saveMessage("bot", initialBotMessageText, currentConversationId, true); // Save as new conversation
                    localStorage.setItem('initialBotMessageSaved', 'true');
                } else {
                    // If initial message was saved, ensure currentConversationId points to the latest one
                    if (chatHistory.length > 0) {
                        currentConversationId = chatHistory[chatHistory.length - 1].id;
                    } else {
                        // Fallback if somehow initial message saved but history is empty
                        currentConversationId = Date.now().toString();
                    }
                }
            }
        } else {
            // If history exists, display messages from the last conversation
            const lastConversation = chatHistory[chatHistory.length - 1];
            currentConversationId = lastConversation.id; // Set current conversation ID
            lastConversation.messages.forEach(msg => {
                const messageHtml = `<p class="${msg.sender}text"><span>${msg.text}</span></p>`;
                chatbox.append(messageHtml);
            });
        }
    }
    // Scroll to the bottom after loading history, only if on the home page
    // Use a small timeout to ensure DOM has rendered before scrolling
    if (chatbox.length > 0) {
        setTimeout(() => {
            chatbox.scrollTop(chatbox[0].scrollHeight);
        }, 50); // Small delay
    }
}

// Function to save a message to local storage
// Now requires a conversationId to explicitly add to a specific conversation
function saveMessage(sender, text, convId, isNewConversation = false) {
    let chatHistory = JSON.parse(localStorage.getItem('mentalHealthChatHistory') || '[]');
    let targetConversation = chatHistory.find(conv => conv.id === convId);

    if (!targetConversation) {
        // If conversation doesn't exist (e.g., first message in a new session) or isNewConversation is true
        targetConversation = {
            id: convId,
            timestamp: new Date().toISOString(),
            messages: []
        };
        chatHistory.push(targetConversation);
    }

    targetConversation.messages.push({ sender: sender, text: text });
    localStorage.setItem('mentalHealthChatHistory', JSON.stringify(chatHistory));
}

// Function to simulate typing animation
function typeMessage(element, text, delay = 20) {
    let i = 0;
    return new Promise(resolve => {
        function typeChar() {
            if (i < text.length) {
                element.append(text.charAt(i));
                i++;
                setTimeout(typeChar, delay);
            } else {
                resolve();
            }
        }
        typeChar();
    });
}

// Function to handle bot response and update UI/history
function getBotResponse() {
    var rawText = $("#textInput").val();
    if (rawText.trim() === "") {
        return; // Don't send empty messages
    }

    // If no currentConversationId, generate one (for the very first user message)
    if (!currentConversationId) {
        currentConversationId = Date.now().toString();
    }

    const chatbox = $("#chatbox");

    // Display user message
    var userHtml = '<p class="usertext"><span>' + rawText + '</span></p>';
    $("#textInput").val(""); // Clear input field
    chatbox.append(userHtml);
    // Scroll to bottom after user message
    chatbox.scrollTop(chatbox[0].scrollHeight);


    // Save user message to local storage (add to current conversation)
    saveMessage("user", rawText, currentConversationId);

    // Add a typing indicator
    var typingIndicatorHtml = '<p class="bottext typing-indicator"><span>Typing...</span></p>';
    chatbox.append(typingIndicatorHtml);
    // Scroll to bottom after typing indicator
    chatbox.scrollTop(chatbox[0].scrollHeight);


    // Get bot response from Flask backend, passing the currentConversationId
    $.get("/get", { msg: rawText, conversation_id: currentConversationId }).done(function(data) {
        // Remove typing indicator
        $(".typing-indicator").remove();

        var botMessageElement = $('<p class="bottext"><span></span></p>');
        chatbox.append(botMessageElement);

        typeMessage(botMessageElement.find('span'), data).then(() => {
            // Scroll after bot message typing is complete
            chatbox.scrollTop(chatbox[0].scrollHeight);
            // Save bot message to local storage AFTER typing animation is complete
            saveMessage("bot", data, currentConversationId);
        });

    }).fail(function(jqXHR, textStatus, errorThrown) {
        // Remove typing indicator on error
        $(".typing-indicator").remove();

        console.error("Error getting bot response:", textStatus, errorThrown);
        var errorHtml = '<p class="bottext"><span>I\'m sorry, I\'m having trouble connecting right now. Please try again later.</span></p>';
        chatbox.append(errorHtml);
        // Scroll after error message is added
        chatbox.scrollTop(chatbox[0].scrollHeight);
        saveMessage("bot", "I'm sorry, I\'m having trouble connecting right now. Please try again later.", currentConversationId);
    });
}

// Function to hide the loader
function hideLoader() {
    const loaderWrapper = document.getElementById('loader-wrapper');
    if (loaderWrapper) {
        loaderWrapper.style.opacity = '0';
        loaderWrapper.style.visibility = 'hidden';
    }
}

// Function to clear all chat history permanently (client-side and server-side)
function clearAllHistory() {
    console.log("Attempting to clear all chat history permanently.");

    fetch('/clear_all_conversations', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log("Server-side history cleared successfully.");
            localStorage.removeItem('mentalHealthChatHistory');
            localStorage.removeItem('initialBotMessageSaved'); // Also clear this flag
            location.reload(); // Reload the page to show empty history
        } else {
            console.error("Failed to clear server-side history:", data.message);
            // Even if server-side fails, clear client-side for immediate user experience
            localStorage.removeItem('mentalHealthChatHistory');
            localStorage.removeItem('initialBotMessageSaved');
            location.reload();
        }
    })
    .catch(error => {
        console.error("Error clearing server-side history:", error);
        // Clear client-side history even if fetch fails
        localStorage.removeItem('mentalHealthChatHistory');
        localStorage.removeItem('initialBotMessageSaved');
        location.reload();
    });
}

// Function to delete a single conversation permanently (client-side and server-side)
function deleteConversation(conversationId) {
    console.log(`Attempting to delete conversation with ID: ${conversationId}`);

    fetch('/delete_conversation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ filename: conversationId }) // Send filename to backend
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log(`Server-side conversation ${conversationId} deleted successfully.`);
            let chatHistory = JSON.parse(localStorage.getItem('mentalHealthChatHistory') || '[]');
            const updatedHistory = chatHistory.filter(conv => conv.id !== conversationId);
            localStorage.setItem('mentalHealthChatHistory', JSON.stringify(updatedHistory));
            location.reload(); // Reload the page to reflect changes
        } else {
            console.error(`Failed to delete server-side conversation ${conversationId}:`, data.message);
            // Even if server-side fails, remove from client-side for immediate user experience
            let chatHistory = JSON.parse(localStorage.getItem('mentalHealthChatHistory') || '[]');
            const updatedHistory = chatHistory.filter(conv => conv.id !== conversationId);
            localStorage.setItem('mentalHealthChatHistory', JSON.stringify(updatedHistory));
            location.reload();
        }
    })
    .catch(error => {
        console.error(`Error deleting server-side conversation ${conversationId}:`, error);
        // Remove from client-side history even if fetch fails
        let chatHistory = JSON.parse(localStorage.getItem('mentalHealthChatHistory') || '[]');
        const updatedHistory = chatHistory.filter(conv => conv.id !== conversationId);
        localStorage.setItem('mentalHealthChatHistory', JSON.stringify(updatedHistory));
        location.reload();
    });
}


// Event listeners for input and button
$(document).ready(function() {
    // Load chat history when the page loads
    loadChatHistory();

    // Only attach input/send button listeners if on the home page
    if (window.location.pathname === '/') {
        if ($("#textInput").length && $("#buttonInput").length) {
            $("#textInput").keypress(function(e) {
                if (e.which == 13) { // Enter key
                    getBotResponse();
                }
            });

            $("#buttonInput").click(function() {
                getBotResponse();
            }
            );
        }
    }

    // Attach event listener for "Clear All History" button if it exists (on history page)
    if (document.getElementById('clearHistoryBtn')) {
        document.getElementById('clearHistoryBtn').addEventListener('click', function() {
            clearAllHistory();
        });
    }

    // Attach event listeners for individual delete buttons if they exist (on history page)
    document.querySelectorAll('.delete-single-conversation-btn').forEach(button => {
        button.addEventListener('click', function() {
            const conversationIdToDelete = this.dataset.conversationId;
            deleteConversation(conversationIdToDelete);
        });
    });
});

// Hide the loader once the window has fully loaded
window.onload = function() {
    hideLoader();
};
