# 🎌 Riko Setup Guide

## ✅ What's Working Now

- ✅ Launcher is installed and working
- ✅ Voice recording and transcription works
- ✅ All Python dependencies are installed
- ✅ Enhanced features are ready to use

## 🔧 What You Need to Do

### 1. Get Your OpenAI API Key

1. Go to https://platform.openai.com/account/api-keys
2. Create a new API key (starts with "sk-")
3. Copy the key

### 2. Update Your Configuration

Edit `character_config.yaml` and replace:

```yaml
OPENAI_API_KEY: sk-YOURAPIKEY # Replace this with your real OpenAI API key!
```

With your real API key:

```yaml
OPENAI_API_KEY: sk-your-actual-api-key-here
```

### 3. Test Without GPT-SoVITS First

You can test the text-only features without the voice server:

```bash
cd riko_project
python launch_riko.py
# Choose option 3: Enhanced Chat (Text Mode)
```

This will let you chat with Riko via text and test the emotional responses!

### 4. For Voice Features (Optional)

If you want voice synthesis, you'll need to:

1. **Start GPT-SoVITS server manually:**

   ```bash
   cd GPT-SoVITS
   python api.py
   ```

2. **Then use the launcher:**
   ```bash
   cd ..
   python launch_riko.py
   # Choose any voice option (1, 2, 4, or 5)
   ```

## 🎯 Quick Test

1. **Update your API key** in `character_config.yaml`
2. **Run text mode:**
   ```bash
   python launch_riko.py
   # Choose option 3
   ```
3. **Try these test phrases:**
   - "I'm so happy to see you!"
   - "Baka! It's not like I care!"
   - "Wow, that's amazing!"

You should see different emotional responses!

## 🚀 Available Interfaces

1. **Enhanced Chat (Push-to-Talk)** - Original with emotions
2. **Enhanced Chat (Live Microphone)** - Continuous listening
3. **Enhanced Chat (Text Mode)** - Text-based testing ⭐ **Start here!**
4. **Web Interface** - Browser-based GUI
5. **VRM 3D Interface** - 3D anime character

## 🎭 Emotional Features

Riko now detects emotions and responds accordingly:

- **Happy** 😊 - "I'm so excited!"
- **Tsundere** 😤 - "Baka! It's not like I care!"
- **Surprised** 😲 - "What?! Really?!"
- **Sad** 😢 - "I'm feeling down..."
- **Flirty** 😘 - "You're so cute, senpai~"

## 🆘 Troubleshooting

**"Invalid API key" error:**

- Make sure you updated `character_config.yaml` with your real OpenAI API key

**GPT-SoVITS won't start:**

- That's okay! Use text mode first (option 3)
- Voice features are optional

**Import errors:**

- Make sure you're in the virtual environment: `.\win_env\Scripts\activate`

## 🎉 You're Ready!

Start with **text mode** to test all the new emotional features, then explore the other interfaces once you have your API key set up!
