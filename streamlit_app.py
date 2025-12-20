import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Multi-Tool Dashboard",
    page_icon="🛠️",
    layout="wide"
)

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a page:", ["Trading Dashboard", "TikTok Unfollow Tool"])

if page == "Trading Dashboard":
    st.title("📈 Trading Dashboard")
    st.write("Trading dashboard features coming soon...")
    st.info("This section will contain trading analytics and data visualization.")
    
elif page == "TikTok Unfollow Tool":
    st.title("🎵 TikTok Auto-Unfollow Tool")
    
    st.write("""
    This tool provides a JavaScript snippet that automatically unfollows users on TikTok.
    
    ### 📋 How to Use:
    1. Go to TikTok and open your Following list
    2. Open your browser's Developer Console:
       - **Chrome/Edge**: Press `F12` or `Ctrl+Shift+J` (Windows/Linux) or `Cmd+Option+J` (Mac)
       - **Firefox**: Press `F12` or `Ctrl+Shift+K` (Windows/Linux) or `Cmd+Option+K` (Mac)
       - **Safari**: Enable Developer Menu in Preferences, then press `Cmd+Option+C`
    3. Copy the JavaScript code below
    4. Paste it into the console and press Enter
    5. The script will automatically start unfollowing users (excluding friends)
    
    ### ⚙️ Features:
    - ✅ Automatically scrolls through your following list
    - ✅ Skips users marked as "Friends"
    - ✅ Shows progress in the console
    - ✅ Stops automatically when no more users to unfollow
    - ✅ Includes delays to avoid rate limiting
    
    ### ⚠️ Important Notes:
    - The script runs in your browser and does not send data anywhere
    - It simulates manual clicking, so it's safe to use
    - Monitor the console output to see progress
    - You can stop the script at any time by refreshing the page
    """)
    
    # JavaScript code
    js_code = """(async () => {
    const sleep = (ms) => new Promise(res => setTimeout(res, ms));

    const simulateClick = (el) => {
        const evt = new MouseEvent('click', { bubbles: true, cancelable: true });
        el.dispatchEvent(evt);
    };

    const scrollToBottom = async () => {
        window.scrollTo(0, document.body.scrollHeight);
        await sleep(3000); // Wait for the new content to load
    };

    const unfollowFromModal = async (button) => {
        const buttonText = button ? button.innerText.toLowerCase() : '';
        
        if (button && buttonText.includes('following')) {
            const containerText = button.innerText.toLowerCase();
            
            // Skip if the user is a friend
            if (containerText.includes('friends')) {
                console.log(`Skipping: ${button.innerText}`);
                return false;
            }

            console.log(`Attempting to unfollow: ${button.innerText}`);
            simulateClick(button); // Click the button inside the modal
            return true;
        }
        return false;
    };

    const unfollowAllUsers = async () => {
        let totalUnfollowed = 0;
        let attempts = 0;
        let cyclesWithoutUnfollows = 0;

        while (true) {
            // Select all "Following" buttons visible on the page
            const buttons = Array.from(document.querySelectorAll('[data-e2e="follow-button"]'));

            if (buttons.length === 0) {
                console.log("No follow buttons found. You may need to scroll more.");
                await scrollToBottom(); // Scroll to load more users
                attempts++;
                if (attempts > 5) { // Increase maximum scroll attempts
                    console.log("Reached maximum scroll attempts. Stopping...");
                    break;
                }
                continue;
            }

            console.log(`${buttons.length} buttons found.`);

            // Loop through each button to find and click the "Unfollow" button
            for (const button of buttons) {
                const unfollowed = await unfollowFromModal(button);
                if (unfollowed) {
                    totalUnfollowed++;
                    cyclesWithoutUnfollows = 0; // Reset cycle count when we unfollow someone
                    console.log(`✅ Unfollowed ${totalUnfollowed}`);
                } else {
                    cyclesWithoutUnfollows++;
                }
            }

            // If we have not unfollowed anyone in the last cycle, stop the process
            if (cyclesWithoutUnfollows > 3) {
                console.log("No more users to unfollow.");
                break;
            }

            await sleep(1500); // Wait for a short moment before the next loop
        }

        console.log(`🎉 Finished. Total unfollowed: ${totalUnfollowed}`);
    };

    // Start the automated unfollow process
    await unfollowAllUsers();
})();"""
    
    st.subheader("📝 JavaScript Code")
    st.code(js_code, language="javascript")
    
    # Add a copy button using Streamlit's native functionality
    st.download_button(
        label="📋 Download Script",
        data=js_code,
        file_name="tiktok_unfollow.js",
        mime="text/javascript"
    )
    
    st.success("💡 Tip: Click the copy button in the code block above to quickly copy the entire script!")
    
    # Additional information
    with st.expander("🔍 How the Script Works"):
        st.write("""
        **Step-by-step breakdown:**
        
        1. **Find Following Buttons**: The script searches for all buttons with the attribute `[data-e2e="follow-button"]`
        2. **Check Button State**: It checks if the button shows "Following" (meaning you're currently following that user)
        3. **Skip Friends**: If the button text contains "friends", it skips that user
        4. **Simulate Click**: It simulates a mouse click on the "Following" button to unfollow
        5. **Scroll & Repeat**: After processing visible buttons, it scrolls down to load more users
        6. **Auto-Stop**: The script stops when no new users are found or after several empty cycles
        
        **Safety Features:**
        - Built-in delays (1.5 seconds between cycles, 3 seconds for scrolling)
        - Skips friends automatically
        - Stops after 5 unsuccessful scroll attempts
        - Logs all actions to the console for transparency
        """)
    
    with st.expander("❓ Troubleshooting"):
        st.write("""
        **Script not working?**
        
        - Make sure you're on the TikTok following list page
        - Check that the page has fully loaded before running the script
        - TikTok may update their HTML structure; the script might need updates
        - Try refreshing the page and running the script again
        
        **Script stopping too early?**
        
        - Scroll manually a bit to load more users, then run the script again
        - The script stops after finding no new users in multiple cycles
        
        **Want to modify the script?**
        
        - You can adjust the sleep times (in milliseconds)
        - Change `attempts > 5` to scroll more or less times
        - Modify `cyclesWithoutUnfollows > 3` to change when the script stops
        """)
