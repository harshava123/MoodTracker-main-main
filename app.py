from flask import Flask, render_template, request, jsonify, send_file
from datetime import datetime, timedelta
from textblob import TextBlob
import speech_recognition as sr
import matplotlib
matplotlib.use('Agg')  # Set the backend to non-interactive 'Agg'
import matplotlib.pyplot as plt
import io
import base64
import json
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import tempfile
import os
from db_connection import DatabaseConnection
import wave
from pydub import AudioSegment

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Add a secret key for session management

# Initialize database connection
db = DatabaseConnection()

# Emotional keywords and phrases
EMOTIONAL_KEYWORDS = {
    # Happy words - expanded list
    'happy': 1.5, 'joy': 1.5, 'excited': 1.5, 'wonderful': 1.5, 'amazing': 1.5,
    'good': 1.3, 'great': 1.3, 'nice': 1.2, 'fine': 1.2, 'okay': 1.2,
    'glad': 1.4, 'delighted': 1.4, 'cheerful': 1.4, 'content': 1.3,
    'elated': 1.6, 'ecstatic': 1.6, 'thrilled': 1.6, 'overjoyed': 1.6,
    'blessed': 1.5, 'fortunate': 1.4, 'lucky': 1.4, 'grateful': 1.5,
    'peaceful': 1.3, 'calm': 1.3, 'relaxed': 1.3, 'serene': 1.4,
    'optimistic': 1.4, 'hopeful': 1.4, 'confident': 1.4, 'proud': 1.4,
    'energetic': 1.3, 'vibrant': 1.3, 'lively': 1.3, 'enthusiastic': 1.4,
    
    # Sad words - expanded list
    'sad': -1.5, 'unhappy': -1.5, 'miserable': -1.5, 'terrible': -1.5, 'awful': -1.5,
    'bad': -1.3, 'poor': -1.3, 'upset': -1.2, 'down': -1.2, 'low': -1.2,
    'angry': -1.4, 'frustrated': -1.4, 'annoyed': -1.4, 'disappointed': -1.3,
    'depressed': -1.6, 'despondent': -1.6, 'hopeless': -1.6, 'despair': -1.6,
    'anxious': -1.4, 'worried': -1.4, 'stressed': -1.4, 'overwhelmed': -1.4,
    'exhausted': -1.3, 'tired': -1.3, 'drained': -1.3, 'weary': -1.3,
    'lonely': -1.5, 'isolated': -1.5, 'abandoned': -1.5, 'rejected': -1.5,
    'guilty': -1.4, 'ashamed': -1.4, 'embarrassed': -1.4, 'regretful': -1.4,
    'confused': -1.3, 'lost': -1.3, 'uncertain': -1.3, 'doubtful': -1.3
}

EMOTIONAL_PHRASES = {
    # Happy phrases - expanded list
    'very happy': 2.0, 'so happy': 2.0, 'really happy': 2.0,
    'feeling good': 1.3, 'doing good': 1.3, 'all good': 1.3,
    'great day': 1.5, 'wonderful day': 1.5, 'amazing day': 1.5,
    'on top of the world': 2.0, 'walking on air': 2.0, 'over the moon': 2.0,
    'could not be happier': 2.0, 'beyond happy': 2.0, 'extremely happy': 2.0,
    'feeling blessed': 1.8, 'grateful for': 1.8, 'thankful for': 1.8,
    'full of joy': 1.8, 'bursting with happiness': 1.8, 'radiating joy': 1.8,
    
    # Sad phrases - expanded list
    'very sad': -2.0, 'so sad': -2.0, 'really sad': -2.0,
    'feeling bad': -1.3, 'doing bad': -1.3, 'all bad': -1.3,
    'terrible day': -1.5, 'awful day': -1.5, 'miserable day': -1.5,
    'at my lowest': -2.0, 'rock bottom': -2.0, 'hitting rock bottom': -2.0,
    'could not be worse': -2.0, 'beyond sad': -2.0, 'extremely sad': -2.0,
    'feeling hopeless': -1.8, 'lost all hope': -1.8, 'no hope': -1.8,
    'full of despair': -1.8, 'overwhelmed with sadness': -1.8, 'drowning in sorrow': -1.8
}

def analyze_sentiment(text):
    # Convert to lowercase for matching
    text = text.lower()
    
    # Get base sentiment from TextBlob
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    
    # Adjust sentiment based on emotional keywords
    for keyword, weight in EMOTIONAL_KEYWORDS.items():
        if keyword in text:
            sentiment += weight
    
    # Adjust sentiment based on emotional phrases
    for phrase, weight in EMOTIONAL_PHRASES.items():
        if phrase in text:
            sentiment += weight
    
    # Special handling for common phrases
    if 'good day' in text:
        sentiment += 1.0
    elif 'bad day' in text:
        sentiment -= 1.0
    
    # Check for negations and intensifiers
    negations = ['not', "n't", 'never', 'no']
    intensifiers = ['very', 'really', 'extremely', 'absolutely', 'completely', 'totally']
    
    # Handle negations
    for negation in negations:
        if negation in text:
            words = text.split()
            try:
                neg_index = words.index(negation)
                for i in range(1, 4):
                    if neg_index + i < len(words):
                        word = words[neg_index + i]
                        if word in EMOTIONAL_KEYWORDS:
                            sentiment -= 2 * EMOTIONAL_KEYWORDS[word]
            except ValueError:
                continue
    
    # Handle intensifiers
    for intensifier in intensifiers:
        if intensifier in text:
            words = text.split()
            try:
                int_index = words.index(intensifier)
                for i in range(1, 3):
                    if int_index + i < len(words):
                        word = words[int_index + i]
                        if word in EMOTIONAL_KEYWORDS:
                            sentiment *= 1.5
            except ValueError:
                continue
    
    # Normalize sentiment to be between -1 and 1
    sentiment = max(min(sentiment, 1.0), -1.0)
    
    return sentiment

def determine_mood(sentiment):
    if sentiment > 0.3:
        return 'Happy'
    elif sentiment < -0.3:
        return 'Sad'
    else:
        return 'Neutral'

def generate_pie_chart(mood_data):
    try:
        plt.figure(figsize=(6, 6))
        colors = ['#2ecc71', '#e74c3c', '#f1c40f']  # Green for Happy, Red for Sad, Yellow for Neutral
        plt.pie(mood_data.values(), labels=mood_data.keys(), colors=colors, autopct='%1.1f%%')
        plt.title('Mood Distribution')
        
        # Save plot to base64 string
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()
        
        return base64.b64encode(image_png).decode()
    except Exception as e:
        print(f"Error generating pie chart: {str(e)}")
        return None

def generate_line_chart(entries):
    try:
        plt.figure(figsize=(10, 4))
        
        dates = []
        sentiments = []
        
        if entries and isinstance(entries[0], dict):
            if 'sentiment_score' in entries[0]:
                # Daily data
                dates = [entry['date'] for entry in entries]
                sentiments = [entry['sentiment_score'] for entry in entries]
            else:
                # Weekly/Monthly data
                dates = [entry['date'] if 'date' in entry else entry['week_start_date'] for entry in entries]
                sentiments = [entry['average_sentiment'] for entry in entries]
        
        plt.plot(dates, sentiments, marker='o')
        plt.title('Sentiment Trend')
        plt.xlabel('Date')
        plt.ylabel('Sentiment Score')
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # Save plot to base64 string
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()
        
        return base64.b64encode(image_png).decode()
    except Exception as e:
        print(f"Error generating line chart: {str(e)}")
        return None

def generate_text_report(entries, start_date, end_date, report_type):
    try:
        # Create a temporary file
        report_path = f'temp_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"Mood Analysis Report ({report_type})\n")
            f.write(f"Period: {start_date} to {end_date}\n\n")
            
            # Calculate summary statistics
            total_entries = len(entries)
            mood_counts = {'Happy': 0, 'Sad': 0, 'Neutral': 0}
            total_sentiment = 0
            
            for entry in entries:
                if report_type == 'daily':
                    mood_counts[entry['mood_category']] += 1
                    total_sentiment += entry['sentiment_score']
                else:
                    mood_counts['Happy'] += entry['happy_count']
                    mood_counts['Sad'] += entry['sad_count']
                    mood_counts['Neutral'] += entry['neutral_count']
                    total_sentiment += entry['average_sentiment']
            
            avg_sentiment = total_sentiment / total_entries if total_entries > 0 else 0
            
            # Write summary
            f.write("Summary:\n")
            f.write(f"Total Entries: {total_entries}\n")
            f.write(f"Average Sentiment: {avg_sentiment:.2f}\n")
            f.write("Mood Distribution:\n")
            for mood, count in mood_counts.items():
                f.write(f"  {mood}: {count}\n")
            f.write("\n")
            
            # Write detailed entries
            f.write("Detailed Entries:\n")
            for entry in entries:
                if report_type == 'daily':
                    f.write(f"\nDate: {entry['date']}\n")
                    f.write(f"Mood: {entry['mood_category']}\n")
                    f.write(f"Sentiment Score: {entry['sentiment_score']:.2f}\n")
                    f.write(f"Text Input: {entry['text_input'] or 'None'}\n")
                    f.write(f"Voice Input: {entry['voice_input'] or 'None'}\n")
                else:
                    period_date = entry['date'] if 'date' in entry else entry['week_start_date']
                    f.write(f"\nPeriod Starting: {period_date}\n")
                    f.write(f"Happy Count: {entry['happy_count']}\n")
                    f.write(f"Sad Count: {entry['sad_count']}\n")
                    f.write(f"Neutral Count: {entry['neutral_count']}\n")
                    f.write(f"Average Sentiment: {entry['average_sentiment']:.2f}\n")
        
        return report_path
    except Exception as e:
        print(f"Error generating text report: {str(e)}")
        raise e

@app.route('/')
def index():
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('index.html', today=today)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        if not data:
            print("No data received in analyze route")
            return jsonify({'error': 'No data received'}), 400
            
        text = data.get('text')
        date_str = data.get('date')
        
        print(f"Received text: {text}")
        print(f"Received date: {date_str}")
        
        if not text:
            print("No text provided in analyze route")
            return jsonify({'error': 'No text provided'}), 400
            
        if not date_str:
            print("No date provided in analyze route")
            return jsonify({'error': 'No date provided'}), 400
            
        # Convert date string to datetime object
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError as e:
            print(f"Invalid date format: {date_str}")
            return jsonify({'error': 'Invalid date format'}), 400
        
        # Analyze sentiment
        try:
            sentiment = analyze_sentiment(text)
            print(f"Calculated sentiment: {sentiment}")
        except Exception as e:
            print(f"Error in sentiment analysis: {str(e)}")
            return jsonify({'error': 'Error analyzing sentiment'}), 500
            
        mood = determine_mood(sentiment)
        print(f"Determined mood: {mood}")
        
        # Save to database
        try:
            db.save_mood_entry(date, text, None, sentiment, mood)
            print("Successfully saved entry to database")
        except Exception as e:
            print(f"Database error: {str(e)}")
            return jsonify({'error': 'Error saving to database'}), 500
        
        # Generate mood distribution chart
        try:
            # Get entries from the last 30 days
            entries = db.get_mood_entries_by_date_range(
                date - timedelta(days=30),
                date + timedelta(days=1)  # Include today
            )
            
            # Count moods
            mood_data = {'Happy': 0, 'Sad': 0, 'Neutral': 0}
            for entry in entries:
                if entry['mood_category'] in mood_data:
                    mood_data[entry['mood_category']] += 1
            
            print("Mood distribution:", mood_data)
            
            # Clear any existing plots
            plt.clf()
            plt.close('all')
            
            # Generate fresh pie chart
            plot_url = generate_pie_chart(mood_data)
            print(f"Generated plot URL: {'Success' if plot_url else 'None'}")
            
            if plot_url:
                plot_url = f'data:image/png;base64,{plot_url}'
            
        except Exception as e:
            print(f"Error generating chart: {str(e)}")
            plot_url = None
        
        response_data = {
            'mood': mood,
            'sentiment': sentiment,
            'plot_url': plot_url,
            'mood_data': mood_data  # Include mood data for debugging
        }
        print(f"Sending response with plot: {'Yes' if plot_url else 'No'}")
        print(f"Final mood distribution: {mood_data}")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Unexpected error in analyze route: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/record-voice', methods=['POST'])
def record_voice():
    try:
        # Get the transcribed text directly from the request
        data = request.json
        if not data or 'text' not in data:
            print("No text received")
            return jsonify({'error': 'No text received'}), 400
            
        text = data['text']
        print(f"Received transcribed text: {text}")
        
        if not text:
            return jsonify({'error': 'Empty text received'}), 400
        
        # Analyze the transcribed text
        sentiment = analyze_sentiment(text)
        mood = determine_mood(sentiment)
        
        print(f"Sentiment: {sentiment}, Mood: {mood}")
        
        # Save to database with voice input
        date = datetime.now().date()
        db.save_mood_entry(date, None, text, sentiment, mood)
        print("Successfully saved to database")
        
        # Get mood distribution for visualization
        entries = db.get_mood_entries_by_date_range(
            date - timedelta(days=30),
            date + timedelta(days=1)  # Include today
        )
        
        # Count moods
        mood_data = {'Happy': 0, 'Sad': 0, 'Neutral': 0}
        for entry in entries:
            if entry['mood_category'] in mood_data:
                mood_data[entry['mood_category']] += 1
        
        print("Mood distribution:", mood_data)
        
        # Generate pie chart
        plt.clf()
        plt.close('all')
        plot_url = generate_pie_chart(mood_data)
        
        return jsonify({
            'text': text,
            'mood': mood,
            'sentiment': sentiment,
            'plot_url': f'data:image/png;base64,{plot_url}' if plot_url else None,
            'mood_data': mood_data
        })
                    
    except Exception as e:
        print(f"Error in voice recording route: {str(e)}")
        return jsonify({'error': 'Error processing voice input. Please try again.'}), 500

@app.route('/reports')
def reports():
    # Get date range for the form
    today = datetime.now().date()
    thirty_days_ago = today - timedelta(days=30)
    return render_template('reports.html', 
                         today=today.strftime('%Y-%m-%d'),
                         thirty_days_ago=thirty_days_ago.strftime('%Y-%m-%d'))

@app.route('/generate-report', methods=['POST'])
def generate_report():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data received'}), 400
            
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        report_type = data.get('report_type', 'daily')  # daily, weekly, or monthly
        
        if not start_date or not end_date:
            return jsonify({'error': 'Missing date parameters'}), 400
            
        # Convert string dates to datetime objects
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        print(f"Generating {report_type} report between {start_date} and {end_date}")
        
        # Get entries based on report type
        entries = []
        if report_type == 'daily':
            entries = db.get_mood_entries_by_date_range(start_date, end_date)
        elif report_type == 'weekly':
            # Get weekly analysis for each week in the range
            current_date = start_date
            while current_date <= end_date:
                week_start = current_date - timedelta(days=current_date.weekday())
                weekly_data = db.get_weekly_analysis(week_start)
                if weekly_data:
                    entries.append(weekly_data)
                current_date += timedelta(days=7)
        elif report_type == 'monthly':
            # Get monthly analysis
            current_date = start_date
            while current_date <= end_date:
                month_start = current_date.replace(day=1)
                daily_data = db.get_daily_analysis(month_start)
                if daily_data:
                    entries.append(daily_data)
                current_date = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1)
        
        if not entries:
            return jsonify({'error': 'No entries found for the selected date range'}), 404
        
        # Calculate mood distribution
        mood_data = {'Happy': 0, 'Sad': 0, 'Neutral': 0}
        total_sentiment = 0
        
        for entry in entries:
            if report_type == 'daily':
                mood_data[entry['mood_category']] += 1
                total_sentiment += entry['sentiment_score']
            else:
                mood_data['Happy'] += entry['happy_count']
                mood_data['Sad'] += entry['sad_count']
                mood_data['Neutral'] += entry['neutral_count']
                total_sentiment += entry['average_sentiment']
        
        # Calculate average sentiment
        avg_sentiment = total_sentiment / len(entries) if entries else 0
        
        # Generate charts
        mood_distribution = generate_pie_chart(mood_data)
        sentiment_trend = generate_line_chart(entries)
        
        # Format entries for response
        formatted_entries = []
        for entry in entries:
            if report_type == 'daily':
                formatted_entries.append({
                    'date': entry['date'].strftime('%Y-%m-%d'),
                    'mood': entry['mood_category'],
                    'sentiment': round(entry['sentiment_score'], 2),
                    'text': entry['text_input'] or entry['voice_input'] or 'No input'
                })
            else:
                formatted_entries.append({
                    'date': entry['date'].strftime('%Y-%m-%d') if 'date' in entry else entry['week_start_date'].strftime('%Y-%m-%d'),
                    'happy_count': entry['happy_count'],
                    'sad_count': entry['sad_count'],
                    'neutral_count': entry['neutral_count'],
                    'average_sentiment': round(entry['average_sentiment'], 2)
                })
        
        return jsonify({
            'mood_distribution': f'data:image/png;base64,{mood_distribution}' if mood_distribution else None,
            'sentiment_trend': f'data:image/png;base64,{sentiment_trend}' if sentiment_trend else None,
            'entries': formatted_entries,
            'summary': {
                'total_entries': len(entries),
                'mood_distribution': mood_data,
                'average_sentiment': round(avg_sentiment, 2)
            }
        })
        
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/download-report', methods=['POST'])
def download_report():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data received'}), 400
            
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        report_type = data.get('report_type', 'daily')
        
        if not start_date or not end_date:
            return jsonify({'error': 'Missing date parameters'}), 400
        
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Get entries based on report type
        entries = []
        if report_type == 'daily':
            entries = db.get_mood_entries_by_date_range(start_date, end_date)
        elif report_type == 'weekly':
            current_date = start_date
            while current_date <= end_date:
                week_start = current_date - timedelta(days=current_date.weekday())
                weekly_data = db.get_weekly_analysis(week_start)
                if weekly_data:
                    entries.append(weekly_data)
                current_date += timedelta(days=7)
        elif report_type == 'monthly':
            current_date = start_date
            while current_date <= end_date:
                month_start = current_date.replace(day=1)
                daily_data = db.get_daily_analysis(month_start)
                if daily_data:
                    entries.append(daily_data)
                current_date = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1)
        
        if not entries:
            return jsonify({'error': 'No entries found for the selected date range'}), 404
        
        report_path = generate_text_report(entries, start_date, end_date, report_type)
        
        return send_file(
            report_path,
            as_attachment=True,
            download_name=f'mood_report_{report_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt',
            mimetype='text/plain'
        )
        
    except Exception as e:
        print(f"Error generating text report: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up temporary files
        try:
            if 'report_path' in locals():
                os.remove(report_path)
        except Exception as e:
            print(f"Error cleaning up temporary files: {str(e)}")

@app.route('/get-recent-entries')
def get_recent_entries():
    try:
        # Get entries from the last 30 days
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        entries = db.get_mood_entries_by_date_range(start_date, end_date)
        
        # Sort by date descending and limit to 5 entries
        entries.sort(key=lambda x: x['date'], reverse=True)
        entries = entries[:5]
        
        return jsonify({
            'entries': [{
                'id': entry['id'],
                'date': entry['date'].strftime('%Y-%m-%d'),
                'text_input': entry['text_input'],
                'voice_input': entry['voice_input'],
                'mood_category': entry['mood_category'],
                'sentiment_score': entry['sentiment_score']
            } for entry in entries]
        })
    except Exception as e:
        print(f"Error fetching recent entries: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 