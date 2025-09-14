# AI Business Saathi 🤖📊

A comprehensive retail analytics dashboard powered by AI that analyzes shop transactions, computes KPIs, generates insights, and provides actionable recommendations in both English and Hindi.

## ✨ Features

- **Multiple Data Input Methods**: CSV upload, manual entry, sample data, and voice input
- **Real-time Analytics**: KPIs, charts, and visualizations
- **AI-Powered Insights**: OpenAI GPT integration for business recommendations
- **Bilingual Support**: Executive summaries in English and Hindi
- **PDF Export**: Professional reports with charts and insights
- **Voice Transcription**: Audio input support via OpenAI Whisper
- **Demo Scenarios**: Pre-built datasets for quick demonstrations

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key (optional - app works with mock data if not provided)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Buildathon
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env and add your OpenAI API key
   ```

4. **Generate sample data**
   ```bash
   python scripts/generate_sample_data.py
   ```

5. **Run the application**
   ```bash
   # Option 1: Use the startup script (recommended)
   python run_app.py
   
   # Option 2: Run directly with Streamlit
   streamlit run app/streamlit_app.py
   ```

The app will open in your browser at `http://localhost:8501`

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Required for AI features
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Model selection (default: gpt-4o-mini)
OPENAI_MODEL=gpt-4o-mini
```

### Without OpenAI API Key

The app works perfectly without an API key! It will:
- Use mock AI responses for insights
- Show voice input UI but use mock transcriptions
- Demonstrate all features end-to-end

## 📊 Demo Scenarios

The app includes 4 pre-built demo scenarios:

1. **Normal Week**: Typical 7-day transaction pattern
2. **Weekend Boost**: High weekend activity scenario
3. **Slow Week**: Low transaction volume week
4. **High Value Orders**: Premium product focus

## 🎥 Demo Video Guide

### Scenario 1: Quick Analytics Demo (2 minutes)

1. **Load Sample Data**
   - Select "Sample Data" in sidebar
   - Choose "Normal Week" scenario
   - Click "Load Sample Data"

2. **View Analytics**
   - Observe KPIs in the main dashboard
   - Check the top products and daily revenue charts
   - Read AI-generated insights and recommendations

3. **Export Report**
   - Click "Generate PDF Report"
   - Download the comprehensive business report

### Scenario 2: Voice Input Demo (1 minute)

1. **Voice Input**
   - Select "Voice Input" in sidebar
   - Upload any audio file (or use provided sample)
   - Click "Transcribe Audio"
   - View the transcribed business insights

2. **Manual Data Entry**
   - Switch to "Manual Entry"
   - Add a few sample transactions
   - See real-time updates in the dashboard

## 🏗️ Project Structure

```
Buildathon/
├── app/
│   ├── __init__.py
│   ├── streamlit_app.py          # Main Streamlit application
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── openai_client.py      # OpenAI integration with fallbacks
│   │   └── prompts.py            # AI prompt templates
│   └── utils/
│       ├── __init__.py
│       └── data_utils.py         # Data processing and visualization
├── sample_data/
│   ├── shop_sample.csv           # Main sample dataset
│   ├── demo_weekend_boost.csv    # Weekend scenario
│   ├── demo_slow_week.csv        # Slow week scenario
│   └── demo_high_value.csv       # High value scenario
├── scripts/
│   └── generate_sample_data.py   # Sample data generator
├── requirements.txt              # Python dependencies
├── env.example                   # Environment variables template
├── Dockerfile                    # Container configuration
└── README.md                     # This file
```

## 🐳 Docker Deployment

### Build and Run

```bash
# Build the Docker image
docker build -t ai-business-saathi .

# Run the container
docker run -p 8501:8501 ai-business-saathi
```

### With Environment Variables

```bash
docker run -p 8501:8501 -e OPENAI_API_KEY=your_key_here ai-business-saathi
```

## 🔍 Key Features Explained

### Data Processing
- **Flexible CSV Import**: Handles various column names and formats
- **Data Normalization**: Automatically maps common retail columns
- **Missing Data Handling**: Graceful fallbacks for incomplete data

### AI Integration
- **JSON Output**: Deterministic parsing of AI responses
- **Fallback Logic**: Mock responses when API unavailable
- **Configurable Models**: Easy switching between GPT models
- **Token Optimization**: Efficient prompts to minimize costs

### Visualization
- **Interactive Charts**: Top products and revenue trends
- **Responsive Design**: Works on desktop and mobile
- **Professional Styling**: Clean, modern UI

### Export Features
- **PDF Reports**: Professional business reports
- **CSV Export**: Raw data download
- **Chart Integration**: Visual elements in PDFs

## 🛠️ Development

### Adding New Features

1. **Data Sources**: Extend `data_utils.py` for new input formats
2. **AI Prompts**: Modify `prompts.py` for different analysis types
3. **Visualizations**: Add new charts in `data_utils.py`
4. **UI Components**: Extend `streamlit_app.py` for new features

### Testing

```bash
# Run with mock data (no API key needed)
streamlit run app/streamlit_app.py

# Test different scenarios
python scripts/generate_sample_data.py
```

## 📝 API Usage

### OpenAI API Costs

- **GPT-4o-mini**: ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens
- **GPT-4**: ~$5 per 1M input tokens, ~$15 per 1M output tokens
- **Whisper**: $0.006 per minute of audio

Typical usage: <$0.01 per analysis session with gpt-4o-mini

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the demo scenarios first
2. Verify your environment setup
3. Check the console for error messages
4. Create an issue with detailed information

## 🎯 Hackathon Notes

This prototype is designed for hackathon demonstrations with:
- **Zero Infrastructure**: Single-file Streamlit app
- **Robust Fallbacks**: Works without external APIs
- **Demo-Ready**: Pre-built scenarios for judges
- **Production Quality**: Clean code, error handling, documentation
- **Quick Setup**: 5-minute installation and demo

Perfect for showcasing AI integration, data visualization, and business intelligence capabilities!
