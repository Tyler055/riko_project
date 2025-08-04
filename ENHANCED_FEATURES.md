# 🎌 Enhanced Riko Features

This document describes all the new features added to Project Riko, including GUI interfaces, live microphone support, emotional voice synthesis, and 3D VRM model integration.

## 🚀 Quick Start

Use the new launcher to access all features:

```bash
cd riko_project
python launch_riko.py
```

## ✨ New Features Overview

### 1. 🎭 Emotional Voice Synthesis

- **Automatic emotion detection** from text content
- **7 different emotions**: happy, sad, angry, surprised, sleepy, flirty, tsundere
- **Anime-specific expressions**: Recognizes "nya", "baka", "senpai", etc.
- **Dynamic voice parameters**: Speed, pitch, and energy adjust based on emotion

### 2. 🎤 Live Microphone Support

- **Voice Activity Detection (VAD)** - automatically detects when you start/stop speaking
- **Continuous listening** - no need to press buttons
- **Configurable sensitivity** - adjust for your microphone and environment
- **Smart silence detection** - waits for natural speech pauses

### 3. 📱 Web Interface

- **Browser-based GUI** using Gradio
- **Real-time audio processing** - record and playback in browser
- **Conversation history** - see your chat history
- **Mobile-friendly** - works on phones and tablets

### 4. 🎌 VRM 3D Interface

- **3D character visualization** using Three.js and VRM
- **Emotion-based animations** - character expressions change with emotions
- **Speaking animations** - mouth movement during speech
- **Idle animations** - breathing and subtle movements
- **Custom VRM support** - load your own 3D anime character models

### 5. 🔧 Enhanced Chat Modes

- **Push-to-Talk** - Original mode with emotional TTS
- **Live Microphone** - Continuous listening mode
- **Text Mode** - Type-based interaction for testing

## 📋 Interface Comparison

| Feature              | Original         | Enhanced Chat          | Web Interface        | VRM Interface        |
| -------------------- | ---------------- | ---------------------- | -------------------- | -------------------- |
| Voice Input          | ✅ Push-to-talk  | ✅ Push-to-talk + Live | ✅ Browser recording | ✅ Browser recording |
| Emotional TTS        | ❌               | ✅                     | ✅                   | ✅                   |
| GUI                  | ❌ Terminal only | ❌ Terminal only       | ✅ Web browser       | ✅ Web browser       |
| 3D Character         | ❌               | ❌                     | ❌                   | ✅                   |
| Conversation History | ❌               | ❌                     | ✅                   | ✅                   |
| Mobile Support       | ❌               | ❌                     | ✅                   | ✅                   |

## 🎭 Emotion System Details

### Supported Emotions

1. **Happy** 😊 - Faster speech, higher pitch, enthusiastic
2. **Sad** 😢 - Slower speech, lower pitch, subdued
3. **Angry** 😠 - Fast speech, emphatic, intense
4. **Surprised** 😲 - Very fast speech, high pitch, excited
5. **Sleepy** 😴 - Very slow speech, low pitch, relaxed
6. **Flirty** 😘 - Smooth speech, slightly lower pitch, playful
7. **Tsundere** 😤 - Quick speech, higher pitch, defensive

### Emotion Detection

The system analyzes text for:

- **Keywords** - emotion-specific words
- **Anime expressions** - "nya", "baka", "ara ara", etc.
- **Punctuation patterns** - "!", "?", "...", etc.
- **Text formatting** - ALL CAPS for anger

### Voice Parameters

Each emotion modifies:

- **Speed** - 0.7x to 1.3x normal speed
- **Pitch** - ±0.2 semitones
- **Energy** - 0.6x to 1.4x intensity

## 🎌 VRM 3D Character System

### Features

- **Real-time emotion display** - character face changes with detected emotion
- **Speaking animation** - mouth movement synchronized with audio
- **Idle animations** - breathing, blinking, subtle movements
- **Responsive design** - works on different screen sizes

### Supported Animations

- **Facial expressions** for all 7 emotions
- **Mouth shapes** for speech (A, I, U sounds)
- **Eye animations** - blinking, winking, wide eyes
- **Head movements** - tilting, turning based on emotion

### Custom VRM Models

To use your own VRM character:

1. Obtain a VRM file (from VRoid Studio, Booth, etc.)
2. Replace the placeholder character loading code
3. Map your model's blendshapes to the emotion system

## 🔧 Technical Implementation

### Architecture

```
riko_project/
├── server/
│   ├── enhanced_main_chat.py      # Multi-mode chat system
│   └── process/
│       ├── asr_func/
│       │   └── live_microphone.py # VAD and continuous listening
│       └── tts_func/
│           └── emotion_tts.py     # Emotional voice synthesis
├── client/
│   ├── web_interface.py           # Gradio web GUI
│   └── vrm_interface.py          # 3D VRM character interface
└── launch_riko.py                # Unified launcher
```

### Dependencies

New packages added:

- `gradio>=4.0.0` - Web interface framework
- Enhanced audio processing libraries
- Three.js integration for 3D rendering

## 🚀 Usage Examples

### 1. Launch Web Interface

```bash
python launch_riko.py
# Choose option 4
```

### 2. Use Live Microphone Mode

```bash
python server/enhanced_main_chat.py --mode live
```

### 3. Test Emotions in Text Mode

```bash
python server/enhanced_main_chat.py --mode text
# Try: "I'm so happy to see you!"
# Try: "Baka! It's not like I care!"
```

### 4. Launch VRM Interface

```bash
python client/vrm_interface.py
```

## 🎯 Future Enhancements

### Planned Features

- **Custom emotion training** - Train on your own emotional voice samples
- **Real VRM model loading** - Full VRM file support with proper rigging
- **Multi-language support** - Emotions in different languages
- **Voice cloning** - Train Riko's voice on custom samples
- **Advanced animations** - Full body movement, gesture recognition
- **Mobile app** - Native iOS/Android application

### Technical Improvements

- **GPU acceleration** for real-time processing
- **WebRTC** for better audio streaming
- **WebGL optimization** for smoother 3D rendering
- **Cloud deployment** options
- **Docker containerization**

## 🐛 Troubleshooting

### Common Issues

**GPT-SoVITS Server Not Running**

```bash
cd GPT-SoVITS
python api.py
```

**Audio Not Working in Browser**

- Check microphone permissions
- Use HTTPS for microphone access
- Try different browsers (Chrome recommended)

**VRM Model Not Loading**

- Ensure VRM file is valid
- Check browser console for errors
- Try with a smaller VRM file first

**Emotion Detection Not Working**

- Check if text contains recognizable emotion keywords
- Try more explicit emotional expressions
- Test with the text mode first

### Performance Tips

- Use GPU acceleration when available
- Close other audio applications
- Use a good quality microphone for better VAD
- Reduce browser tabs for better 3D performance

## 📞 Support

For issues or questions:

1. Check the troubleshooting section above
2. Review the console output for error messages
3. Test with the simpler interfaces first (text mode)
4. Ensure all dependencies are properly installed

## 🎉 Conclusion

The enhanced Riko system now provides a complete anime AI companion experience with:

- Multiple interaction modes
- Emotional voice synthesis
- Modern web interfaces
- 3D character visualization
- Continuous voice interaction

Enjoy chatting with your enhanced Riko! 🎌✨
