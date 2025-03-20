# MoodTracker
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/findkeys/MoodTracker)](https://github.com/your-username/bot-front-web-app/stargazers)

## MoodTracker Live Demo



**Note:** Scroll all the way down to access the projects

A web application that helps you track your mood through text and voice input, providing sentiment analysis and visualizations of your emotional patterns over time.

## Features

- Text-based mood analysis
- Voice input support with speech-to-text conversion
- Sentiment analysis using TextBlob
- Interactive visualizations (pie charts and line graphs)
- Historical mood tracking and reporting
- Modern, responsive UI with Bootstrap 5

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- A modern web browser with JavaScript enabled
- Microphone (for voice input feature)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/MoodTracker.git
cd MoodTracker
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Flask application:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. You can now:
   - Enter text to analyze your mood
   - Use voice input by clicking the microphone button
   - View your mood analysis results
   - Generate reports with historical data
   - Track your emotional patterns over time

## Project Structure

```
MoodTracker/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── templates/         # HTML templates
│   ├── base.html      # Base template with common elements
│   ├── index.html     # Main page with input and analysis
│   └── reports.html   # Reports page with visualizations
└── static/           # Static files (CSS, JS, images)
```

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Flask web framework
- TextBlob for sentiment analysis
- SpeechRecognition for voice input
- Bootstrap for the UI components
- Font Awesome for icons

---
[![Discord](https://img.shields.io/badge/Discord-%235865F2.svg?style=for-the-badge&logo=discord&logoColor=white)](https://discord.com/users/887532157747212370)
[![X](https://img.shields.io/badge/X-%23000000.svg?style=for-the-badge&logo=X&logoColor=white)](https://twitter.com/codewithriza)

