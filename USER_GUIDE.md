# 💬 Emergency Messaging System - USER GUIDE

**Your secure messaging system when Signal is down**

---

## 🎯 Getting Started (5 minutes)

### Step 1: Access the App
1. Go to the link provided: `http://SERVER:3000`
2. You'll see the login/register screen

### Step 2: Create Your Account
1. Click **"Register"** button
2. Enter:
   - **Username:** (something simple, others will search for this)
   - **Email:** (your email address)
   - **Password:** (8+ characters, must be strong)
3. Click **"Register"**
4. ✅ Your encryption keys are generated automatically!

### Step 3: Login
1. Click **"Login"**
2. Enter:
   - **Email:** (the email you registered with)
   - **Password:** (the password you created)
3. Click **"Login"**
4. ✅ You're in!

---

## 💬 How to Send Messages

### Find a Friend to Message

1. Click the **"Users"** tab on the right
2. See list of all online users
3. Click on a user's name
4. A chat window opens!

### Search for Specific Person

1. In the Users tab, type in the **search box**
2. Results appear as you type
3. Click on the person you want to message

### Send Your First Message

1. Type your message in the **text box** at the bottom
2. Press **Enter** or click **Send**
3. ✅ Your message is encrypted and sent!
4. The other person sees it when they check the app

---

## 👥 Understanding the Interface

### Main Chat Screen
```
┌─────────────────────────────────┐
│   CONVERSATIONS    │   USERS    │  ← Tabs
├─────────────────────────────────┤
│                                 │
│   Chat Window (messages here)   │
│                                 │
├─────────────────────────────────┤
│ Type message here... │ [Send] │  ← Message input
└─────────────────────────────────┘
```

### Messages Appearance

**Your messages (blue, right side):**
```
                    You: Hey, are you there?
                              10:30 AM
```

**Other person's messages (gray, left side):**
```
Friend: Yeah! Got your message!
10:31 AM
```

---

## 🔐 Your Encryption Keys (What's Happening Behind Scenes)

✅ **Don't worry - it's automatic!**

When you registered:
1. Your browser generated 2 encryption keys:
   - **Public Key** - shared with everyone (safe to share)
   - **Private Key** - only you have this (keeps encrypted forever)

2. When you send a message:
   - Message encrypted with recipient's public key
   - Sent to server
   - Only they can decrypt with their private key

3. When you receive a message:
   - You receive encrypted message
   - Your browser decrypts with your private key
   - You see readable message

**Result:** Server never sees your actual messages!

---

## 🔔 Notifications & Status

### Online Status
- **Green dot** = Person is online now
- **Offline/No dot** = Person is offline

### Message Status
- **Immediate send** = Sent encrypted to server
- **Visible to recipient** = Next time they check app

### Typing Indicator
- See `User is typing...` = They're composing a message

---

## 🛡️ Security Tips

### ✅ DO:
- Use a **strong password** (8+ chars, mix of letters/numbers/symbols)
- **Don't share your password** with anyone
- **Trust the blue lock icon** - means connection is encrypted
- **Verify usernames** - make sure you're messaging the right person

### ❌ DON'T:
- Share your password in messages
- Use the same password as other services
- Open links from strangers
- Trust message content without verifying sender

---

## 🆘 Common Questions

### Q: Can the server read my messages?
**A:** No! Messages are encrypted before leaving your device. Server only stores encrypted blobs.

### Q: What if I forget my password?
**A:** Sorry, there's no recovery. Create a new account with a different email.

### Q: Can someone access my messages?
**A:** Only you (with your password) and the recipient can read messages.

### Q: What happens to messages if I logout?
**A:** Messages stay on the server encrypted. You can access them by logging back in.

### Q: Can I delete messages?
**A:** Messages are permanent once sent. Think before you send!

### Q: Is this as secure as Signal?
**A:** Similar encryption (RSA-2048 + AES-256), but simpler. Good for emergencies!

---

## 📱 Using on Different Devices

### Desktop & Laptop
- Full interface
- Easy typing
- Keep app open for instant messages

### Mobile (Phone/Tablet)
- Responsive design
- Tap to message
- Notifications (if enabled)

### Switching Between Devices
1. Use same email/password on other device
2. Login
3. ✅ See all your conversations!
4. Messages sync automatically

---

## ⌨️ Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Send message | **Enter** |
| New line in message | **Shift + Enter** |
| Search users | **Ctrl+F** (or native search) |
| Focus message input | **Tab** (multiple times) |

---

## 🔄 Troubleshooting

### I can't login
- ❌ Check your email & password
- ❌ Make sure caps lock is OFF
- ❌ Try refreshing the page

### Messages not sending
- ❌ Check internet connection
- ❌ Try pressing Enter again
- ❌ Reload the page

### Can't find a user
- ❌ Make sure you spelled their username correctly
- ❌ They need to be registered first
- ❌ They might be offline

### App is slow
- ❌ Try refreshing the page
- ❌ Close other tabs/apps
- ❌ Check your internet speed

### I'm getting an error
- ❌ Note the error message
- ❌ Reload the page
- ❌ Contact admin with error details

---

## 📞 During Emergencies

### Tell Friends the Access Link
```
"Go to: http://[LINK] to message me"
```

### If Server Goes Down
- Try again in a few minutes
- Contact administrator
- Have backup communication method ready

### Rapid Onboarding (Group Emergency)
1. Share the URL
2. Tell them: Register → Search for me → Message!
3. That's it!

---

## 🎓 Advanced Features

### Search Conversations
- Check "Conversations" tab
- See all past conversations
- Click to open old conversations

### Conversation List
- Shows all your active chats
- Shows message preview
- Click to jump to that conversation

### User List
- See who's online
- Shows online status dot
- Search to find specific people

---

## 📊 Privacy & Data

### What We Store
- ✅ Encrypted messages
- ✅ User profiles (username, email)
- ✅ Online status
- ❌ Passwords (only salted hash)
- ❌ Unencrypted message content

### What We Don't Store
- Your private encryption key (only on your device)
- Your passwords (only hashed)
- Your location
- Your system information

### Data Deletion
- Contact admin to delete account
- All your data can be purged
- Messages remain on recipient's device

---

## ⚡ Emergency Use Scenarios

### When Signal is Down
1. Switch to this app immediately
2. Tell your contacts the URL
3. Everyone creates accounts
4. Resume messaging!

### When You Need Quick Communication
1. Instead of phone calls (which might overload networks)
2. Use encrypted text - faster, more reliable
3. Build up message history

### For Remote Team Coordination
1. Set up central server
2. Share URL with team
3. Create channels/groups by username searching
4. Instant team communication

---

## 🎉 You're Ready!

- ✅ Account created
- ✅ Understand encryption
- ✅ Know how to message
- ✅ Know security best practices

**Start messaging securely now!**

---

## 📞 Need Help?

If something isn't working:
1. Check the FAQ section (above)
2. Reload the page
3. Try in a different browser
4. Contact the system administrator

---

**Happy secure messaging!** 🔐💬
