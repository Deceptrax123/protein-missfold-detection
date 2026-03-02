# Misfold-Spotter Frontend

A dark-themed, animated web interface for the Protein Misfolding Detection Pipeline.

## Features

- **API Key Input**: Secure temporary API key entry (Mistral/OpenAI/Anthropic)
- **Provider Selection**: Choose between multiple AI providers
- **DNA Sequence Input**: Color-coded nucleotide input with real-time preview
- **Live DNA Visualization**: Instant preview with nucleotide color coding (A=🔴, T=🟢, C=🔵, G=🟡)
- **Analysis Button**: 3D animated button with gradient effects
- **Loading Animation**: Animated "Processing sequence and generating PDF..." with pulsing status indicator
- **Results Display**: Formatted JSON results with custom scrollbars
- **PDF Download**: Gradient button for report downloads
- **Responsive Design**: Works on desktop and mobile devices
- **Dark Scientific Theme**: Professional dark color scheme with animations

## Design Highlights

### 🌌 Animated Biological Theme
- **Deep Space Background**: Dark blue/purple gradient (#1a1a2e)
- **Floating DNA Helices**: 6 animated DNA helix structures with complex animations
- **Protein Molecules**: 6 radial gradient protein molecules with 3D rotation
- **Enhanced Animations**: Smooth, organic movement patterns
- **Subtle Glow Effects**: Gradient borders and drop shadows
- **Biological Accuracy**: DNA helix shapes using CSS clip-path

### 🎨 Color Palette
- **Primary**: #4a90e2 (Science Blue)
- **Accent**: #6c5ce7 (Purple Gradient)
- **Success**: #2ecc71 (Vibrant Green)
- **DNA Color**: #ff6b6b (Coral for nucleotides)
- **Protein Color**: #4ecdc4 (Teal for proteins)

### ✨ Interactive Elements
- **3D Buttons**: Hover effects with perspective transform
- **Gradient Backgrounds**: Smooth color transitions
- **Pulsing Indicators**: Animated status dots
- **Smooth Animations**: Fade-ins, slide-ins, and transforms
- **Custom Scrollbars**: Themed scrollbars for results

### 🎨 Animation Details

**DNA Helix Animations:**
- **6 DNA Helices**: Different sizes, positions, and animation delays
- **Complex Paths**: Multi-point movement with X/Y translation
- **Scale Variation**: Helices grow and shrink organically
- **Rotation**: Gentle spinning motion for realism
- **Gradient Background**: Coral color with transparency
- **Drop Shadows**: Soft glow effect

**Protein Molecule Animations:**
- **6 Protein Molecules**: Radial gradient spheres
- **3D Rotation**: Full 360° rotation patterns
- **Organic Movement**: Non-linear floating paths
- **Scale Pulsing**: Gentle size variations
- **Teal Color Scheme**: Scientific protein color
- **Inner Glow**: Subtle internal lighting

**Animation Characteristics:**
- **Duration**: 30-35 seconds per cycle
- **Easing**: Ease-in-out for natural movement
- **Delays**: Staggered start times (0-26s)
- **Continuous**: Infinite looping animations
- **Performance**: GPU-accelerated CSS animations

### 🔐 API Key Security
- **No Storage**: API keys are never stored, saved, or transmitted beyond the current session
- **Temporary Use**: Keys are used only for the duration of the API call
- **Environment Variables**: Keys are passed via temporary environment variables
- **Client-Side Only**: Keys remain in browser memory, not stored on server
- **Automatic Cleanup**: Keys are removed from memory after use

### 💡 Special Effects
- **Backdrop Blur**: Frosted glass effect on cards
- **CSS Clip Path**: DNA helix shapes using polygon clipping
- **Radial Gradients**: Protein molecule representations
- **Box Shadows**: Depth and dimension
- **Text Gradients**: Multi-color text effects
- **Dynamic Trail**: Real-time cursor following with physics

## Installation

1. Install the required dependencies:
```bash
pip install flask
```

2. Make sure you have all the agent dependencies installed (see main README)

## API Key Setup

The application requires an API key from one of the supported providers:

### Supported Providers
- **Mistral AI** (Default)
- **OpenAI** 
- **Anthropic**

### How to Get API Keys
1. **Mistral**: Sign up at [mistral.ai](https://mistral.ai) and get your API key
2. **OpenAI**: Sign up at [openai.com](https://openai.com) and get your API key
3. **Anthropic**: Sign up at [anthropic.com](https://anthropic.com) and get your API key

### Security Guarantees
✅ **No Storage**: Your API key is never stored on disk or in databases
✅ **No Transmission**: Your API key is never transmitted beyond the current request
✅ **Memory Only**: Your API key exists only in browser memory during your session
✅ **Automatic Cleanup**: Your API key is removed from memory after each request

## Running the Application

1. Start the backend server:
```bash
cd frontend
python server.py
```

2. Open `index.html` in your web browser
3. Enter your API key from your chosen provider
4. Select your API provider from the tabs

## How It Works

1. User enters their API key (temporary, not stored)
2. User selects their API provider (Mistral/OpenAI/Anthropic)
3. User enters a DNA sequence in the textarea
4. Clicks "Analyze Sequence" button
5. Frontend validates API key and DNA sequence
6. Frontend shows loading animation while calling backend API
7. Backend temporarily uses the API key for the current request only
8. Backend processes the sequence through all three agents
9. API key is immediately removed from memory after use
10. Results are displayed and PDF download button becomes available
11. User can download the generated PDF report

## File Structure

- `index.html`: Main frontend interface
- `server.py`: Flask backend server
- `README.md`: This file

## Backend API Endpoints

- `POST /api/analyze`: Accepts DNA sequence and returns analysis results
- `GET /api/download/<filename>`: Downloads the generated PDF report

## Requirements

- Python 3.7+
- Flask
- All agent dependencies from the main project