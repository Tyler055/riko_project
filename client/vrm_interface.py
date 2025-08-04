import gradio as gr
import numpy as np
import json
import time
import threading
import queue
from pathlib import Path
import sys

# Add server path
sys.path.append(str(Path(__file__).parent.parent / "server"))

from process.asr_func.live_microphone import LiveMicrophoneRecorder
from process.llm_funcs.llm_scr import llm_response
from process.tts_func.emotion_tts import sovits_gen_emotional, EmotionalTTS
from faster_whisper import WhisperModel

class VRMInterface:
    def __init__(self):
        self.whisper_model = WhisperModel("base.en", device="cpu", compute_type="float32")
        self.emotional_tts = EmotionalTTS()
        self.live_recorder = None
        self.is_listening = False
        self.conversation_history = []
        
        # VRM animation states
        self.current_emotion = "neutral"
        self.is_speaking = False
        self.mouth_animation = 0.0
        self.eye_blink = 0.0
        
        # Animation parameters for different emotions
        self.emotion_animations = {
            'happy': {'mouth_smile': 0.8, 'eye_happy': 0.7, 'eyebrow_up': 0.3},
            'sad': {'mouth_frown': 0.6, 'eye_sad': 0.8, 'eyebrow_down': 0.5},
            'angry': {'mouth_angry': 0.7, 'eye_angry': 0.9, 'eyebrow_angry': 0.8},
            'surprised': {'mouth_o': 0.9, 'eye_wide': 1.0, 'eyebrow_up': 0.9},
            'sleepy': {'eye_sleepy': 0.8, 'mouth_small': 0.3, 'head_tilt': 0.2},
            'flirty': {'mouth_smile': 0.6, 'eye_wink': 0.5, 'head_tilt': 0.1},
            'tsundere': {'mouth_pout': 0.7, 'eye_angry': 0.4, 'head_turn': 0.3},
            'neutral': {'reset': True}
        }
    
    def get_vrm_animation_data(self, emotion: str, is_speaking: bool = False) -> dict:
        """Generate VRM animation data based on emotion and speaking state"""
        animation_data = {
            'timestamp': time.time(),
            'emotion': emotion,
            'is_speaking': is_speaking,
            'blendshapes': {}
        }
        
        # Base emotion blendshapes
        if emotion in self.emotion_animations:
            animation_data['blendshapes'].update(self.emotion_animations[emotion])
        
        # Speaking animation (mouth movement)
        if is_speaking:
            # Simulate mouth movement for speech
            mouth_intensity = 0.3 + 0.4 * np.sin(time.time() * 10)  # Oscillating mouth
            animation_data['blendshapes']['mouth_a'] = max(0, mouth_intensity)
            animation_data['blendshapes']['mouth_i'] = max(0, mouth_intensity * 0.7)
            animation_data['blendshapes']['mouth_u'] = max(0, mouth_intensity * 0.5)
        
        # Random blinking
        if np.random.random() < 0.1:  # 10% chance per frame
            animation_data['blendshapes']['eye_blink'] = 1.0
        
        return animation_data
    
    def create_vrm_viewer_html(self) -> str:
        """Create HTML for VRM model viewer using Three.js and VRM"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Riko VRM Viewer</title>
            <style>
                body { margin: 0; padding: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
                #vrm-container { width: 100%; height: 100vh; position: relative; }
                #controls { position: absolute; top: 10px; left: 10px; z-index: 100; }
                #controls button { margin: 5px; padding: 10px; background: rgba(255,255,255,0.8); border: none; border-radius: 5px; }
                #emotion-display { position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.7); color: white; padding: 10px; border-radius: 5px; }
            </style>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/@pixiv/three-vrm@0.6.7/lib/three-vrm.js"></script>
        </head>
        <body>
            <div id="vrm-container">
                <div id="controls">
                    <button onclick="loadVRMModel()">Load VRM Model</button>
                    <button onclick="toggleAnimation()">Toggle Animation</button>
                </div>
                <div id="emotion-display">
                    <div>Emotion: <span id="current-emotion">neutral</span></div>
                    <div>Speaking: <span id="speaking-status">false</span></div>
                </div>
            </div>
            
            <script>
                let scene, camera, renderer, vrm, mixer;
                let isAnimating = true;
                let currentEmotion = 'neutral';
                
                // Initialize Three.js scene
                function initScene() {
                    scene = new THREE.Scene();
                    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
                    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
                    renderer.setSize(window.innerWidth, window.innerHeight);
                    renderer.setClearColor(0x000000, 0);
                    document.getElementById('vrm-container').appendChild(renderer.domElement);
                    
                    // Lighting
                    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
                    scene.add(ambientLight);
                    
                    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
                    directionalLight.position.set(1, 1, 1);
                    scene.add(directionalLight);
                    
                    // Camera position
                    camera.position.set(0, 1.6, 3);
                    camera.lookAt(0, 1.6, 0);
                    
                    // Animation mixer
                    mixer = new THREE.AnimationMixer(scene);
                }
                
                // Load VRM model (placeholder - user needs to provide VRM file)
                async function loadVRMModel() {
                    try {
                        // This is a placeholder - in real implementation, user would upload VRM file
                        console.log('VRM model loading would happen here');
                        
                        // Create a simple placeholder character
                        createPlaceholderCharacter();
                        
                    } catch (error) {
                        console.error('Error loading VRM model:', error);
                        createPlaceholderCharacter();
                    }
                }
                
                // Create a simple placeholder character
                function createPlaceholderCharacter() {
                    // Head
                    const headGeometry = new THREE.SphereGeometry(0.15, 32, 32);
                    const headMaterial = new THREE.MeshLambertMaterial({ color: 0xffdbac });
                    const head = new THREE.Mesh(headGeometry, headMaterial);
                    head.position.set(0, 1.7, 0);
                    scene.add(head);
                    
                    // Eyes
                    const eyeGeometry = new THREE.SphereGeometry(0.02, 16, 16);
                    const eyeMaterial = new THREE.MeshLambertMaterial({ color: 0x000000 });
                    
                    const leftEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
                    leftEye.position.set(-0.05, 1.72, 0.12);
                    head.add(leftEye);
                    
                    const rightEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
                    rightEye.position.set(0.05, 1.72, 0.12);
                    head.add(rightEye);
                    
                    // Body
                    const bodyGeometry = new THREE.CylinderGeometry(0.1, 0.15, 0.6, 8);
                    const bodyMaterial = new THREE.MeshLambertMaterial({ color: 0x4a90e2 });
                    const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
                    body.position.set(0, 1.2, 0);
                    scene.add(body);
                    
                    // Store references for animation
                    window.rikoCharacter = { head, leftEye, rightEye, body };
                }
                
                // Update animation based on emotion and speaking state
                function updateAnimation(animationData) {
                    if (!window.rikoCharacter) return;
                    
                    const { head, leftEye, rightEye, body } = window.rikoCharacter;
                    const { emotion, is_speaking, blendshapes } = animationData;
                    
                    // Update emotion display
                    document.getElementById('current-emotion').textContent = emotion;
                    document.getElementById('speaking-status').textContent = is_speaking;
                    
                    // Apply emotion-based animations
                    switch(emotion) {
                        case 'happy':
                            head.rotation.z = Math.sin(Date.now() * 0.001) * 0.1;
                            break;
                        case 'sad':
                            head.rotation.x = -0.2;
                            break;
                        case 'angry':
                            head.rotation.x = 0.1;
                            body.scale.y = 1.1;
                            break;
                        case 'surprised':
                            head.scale.setScalar(1.1);
                            break;
                        default:
                            head.rotation.set(0, 0, 0);
                            head.scale.setScalar(1);
                            body.scale.setScalar(1);
                    }
                    
                    // Speaking animation
                    if (is_speaking) {
                        const mouthMovement = Math.sin(Date.now() * 0.01) * 0.05;
                        head.scale.y = 1 + mouthMovement;
                    }
                }
                
                // Animation loop
                function animate() {
                    requestAnimationFrame(animate);
                    
                    if (mixer) mixer.update(0.016);
                    
                    // Idle animations
                    if (window.rikoCharacter && isAnimating) {
                        const time = Date.now() * 0.001;
                        window.rikoCharacter.body.rotation.y = Math.sin(time * 0.5) * 0.1;
                        
                        // Breathing animation
                        window.rikoCharacter.body.scale.y = 1 + Math.sin(time * 2) * 0.02;
                    }
                    
                    renderer.render(scene, camera);
                }
                
                function toggleAnimation() {
                    isAnimating = !isAnimating;
                }
                
                // Handle window resize
                window.addEventListener('resize', () => {
                    camera.aspect = window.innerWidth / window.innerHeight;
                    camera.updateProjectionMatrix();
                    renderer.setSize(window.innerWidth, window.innerHeight);
                });
                
                // Initialize everything
                initScene();
                loadVRMModel();
                animate();
                
                // API for external control
                window.updateRikoAnimation = updateAnimation;
            </script>
        </body>
        </html>
        """
    
    def process_conversation(self, user_input: str) -> tuple:
        """Process user input and return response with animation data"""
        if not user_input.strip():
            return "", None, self.conversation_history, self.get_vrm_animation_data("neutral")
        
        # Get LLM response
        riko_response = llm_response(user_input)
        
        # Detect emotion for animation
        emotion = self.emotional_tts.detect_emotion(riko_response)
        self.current_emotion = emotion
        
        # Generate emotional TTS
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            audio_path = sovits_gen_emotional(riko_response, tmp_file.name, emotion)
        
        # Update conversation history
        self.conversation_history.append(f"You: {user_input}")
        self.conversation_history.append(f"Riko: {riko_response}")
        
        # Generate animation data
        animation_data = self.get_vrm_animation_data(emotion, is_speaking=True)
        
        return riko_response, audio_path, "\n".join(self.conversation_history[-10:]), animation_data
    
    def create_interface(self):
        """Create the VRM interface with 3D model viewer"""
        with gr.Blocks(title="Riko VRM Interface", theme=gr.themes.Soft()) as interface:
            gr.Markdown("# 🎌 Riko VRM - 3D Anime AI Assistant")
            
            with gr.Row():
                with gr.Column(scale=2):
                    # VRM Viewer
                    vrm_viewer = gr.HTML(
                        value=self.create_vrm_viewer_html(),
                        label="🎭 Riko 3D Model"
                    )
                
                with gr.Column(scale=1):
                    # Chat interface
                    with gr.Group():
                        gr.Markdown("### 💬 Chat with Riko")
                        
                        text_input = gr.Textbox(
                            label="Type your message",
                            placeholder="Say something to Riko...",
                            lines=2
                        )
                        
                        audio_input = gr.Audio(
                            sources=["microphone"],
                            type="numpy",
                            label="🎤 Or speak to Riko"
                        )
                        
                        send_btn = gr.Button("💌 Send", variant="primary")
                    
                    # Response area
                    with gr.Group():
                        riko_response = gr.Textbox(
                            label="🎌 Riko's Response",
                            interactive=False,
                            lines=3
                        )
                        
                        audio_output = gr.Audio(
                            label="🔊 Riko's Voice",
                            autoplay=True
                        )
                        
                        emotion_display = gr.Textbox(
                            label="🎭 Current Emotion",
                            interactive=False
                        )
                    
                    # Conversation history
                    conversation_history = gr.Textbox(
                        label="📜 Conversation History",
                        lines=8,
                        interactive=False
                    )
                    
                    # Animation data (hidden, for JavaScript)
                    animation_data = gr.JSON(visible=False)
            
            # Event handlers
            def handle_text_input(text):
                response, audio, history, anim_data = self.process_conversation(text)
                return "", response, audio, anim_data['emotion'], history, anim_data
            
            def handle_audio_input(audio):
                if audio is None:
                    return "", "", None, "neutral", self.conversation_history, {}
                
                # Transcribe audio
                import tempfile
                import soundfile as sf
                
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                    sf.write(tmp_file.name, audio[1], audio[0])
                    segments, _ = self.whisper_model.transcribe(tmp_file.name)
                    user_text = " ".join([segment.text for segment in segments])
                
                if user_text.strip():
                    response, audio_out, history, anim_data = self.process_conversation(user_text)
                    return "", response, audio_out, anim_data['emotion'], history, anim_data
                
                return "", "I didn't catch that, could you try again?", None, "neutral", self.conversation_history, {}
            
            # Connect events
            send_btn.click(
                fn=handle_text_input,
                inputs=[text_input],
                outputs=[text_input, riko_response, audio_output, emotion_display, conversation_history, animation_data]
            )
            
            audio_input.change(
                fn=handle_audio_input,
                inputs=[audio_input],
                outputs=[text_input, riko_response, audio_output, emotion_display, conversation_history, animation_data]
            )
            
            # JavaScript to update VRM animation
            interface.load(
                fn=None,
                js="""
                function() {
                    // Set up animation data listener
                    const animationOutput = document.querySelector('[data-testid="json"]');
                    if (animationOutput) {
                        const observer = new MutationObserver(() => {
                            try {
                                const data = JSON.parse(animationOutput.textContent);
                                if (window.updateRikoAnimation) {
                                    window.updateRikoAnimation(data);
                                }
                            } catch (e) {
                                console.log('Animation data not ready yet');
                            }
                        });
                        observer.observe(animationOutput, { childList: true, subtree: true });
                    }
                }
                """
            )
        
        return interface

def main():
    print("🎭 Loading Riko VRM Interface...")
    
    vrm_interface = VRMInterface()
    interface = vrm_interface.create_interface()
    
    print("🚀 Starting Riko VRM Interface...")
    print("🎌 Open your browser to see Riko in 3D!")
    print("💡 You can upload your own VRM model file for a custom character")
    
    interface.launch(
        server_name="0.0.0.0",
        server_port=7861,
        share=False,
        inbrowser=True
    )

if __name__ == "__main__":
    main()