import speech_recognition as sr
import tkinter as tk
from textblob import TextBlob
from tkinter import ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import tkcalendar
from db_connection import DatabaseConnection
import pandas as pd
import numpy as np
import re

class MoodAnalyzer:
    def __init__(self):
        self.db = DatabaseConnection()
        self.setup_gui()
        self.mood_data = {'Happy': 0, 'Sad': 0, 'Neutral': 0}
        self.weekly_mood = []
        self.recording = False
        self.recognizer = None
        self.audio_source = None
        
        # Define emotional keywords and their weights
        self.emotional_keywords = {
            # Happy words - simple and common
            'happy': 1.5, 'joy': 1.5, 'excited': 1.5, 'wonderful': 1.5, 'amazing': 1.5,
            'good': 1.3, 'great': 1.3, 'nice': 1.2, 'fine': 1.2, 'okay': 1.2,
            'ok': 1.2, 'alright': 1.2, 'well': 1.2, 'better': 1.3, 'best': 1.5,
            'fun': 1.3, 'enjoy': 1.3, 'enjoying': 1.3, 'enjoyed': 1.3,
            'like': 1.2, 'love': 2.0, 'loved': 2.0, 'loving': 1.8,
            'smile': 1.3, 'smiling': 1.3, 'laugh': 1.3, 'laughing': 1.3,
            'cool': 1.2, 'awesome': 1.5, 'fantastic': 1.5, 'perfect': 1.5,
            'yay': 1.5, 'yeah': 1.3, 'yes': 1.2, 'sure': 1.2,
            'wow': 1.3, 'wonderful': 1.5, 'beautiful': 1.5, 'pretty': 1.3,
            'sweet': 1.3, 'kind': 1.3, 'nice': 1.2, 'pleasant': 1.3,
            'welcome': 1.2, 'thanks': 1.2, 'thank you': 1.3, 'appreciate': 1.3,
            'wish': 1.2, 'hope': 1.2, 'want': 1.2, 'need': 1.2,
            'please': 1.2, 'sorry': -1.3, 'apologize': -1.3,
            
            # Happy words - more complex
            'delighted': 1.8, 'ecstatic': 2.0, 'elated': 1.8, 'euphoric': 2.0,
            'glad': 1.3, 'cheerful': 1.5, 'jubilant': 1.8, 'thrilled': 1.8,
            'blessed': 1.5, 'fortunate': 1.3, 'lucky': 1.3, 'grateful': 1.5,
            'peaceful': 1.3, 'content': 1.3, 'satisfied': 1.3, 'fulfilled': 1.5,
            'adored': 1.8, 'cherished': 1.8, 'energetic': 1.3, 'enthusiastic': 1.5,
            'passionate': 1.5, 'inspired': 1.5, 'proud': 1.5, 'accomplished': 1.5,
            'successful': 1.5, 'achieved': 1.5, 'confident': 1.5, 'optimistic': 1.5,
            'hopeful': 1.5, 'determined': 1.3, 'motivated': 1.3, 'focused': 1.2,
            'calm': 1.3, 'relaxed': 1.3, 'comfortable': 1.3, 'secure': 1.3,
            'free': 1.3, 'independent': 1.3, 'strong': 1.3, 'powerful': 1.3,
            
            # Sad words - simple and common
            'sad': -1.5, 'upset': -1.5, 'crying': -2.0, 'depressed': -2.0, 'terrible': -1.5,
            'bad': -1.3, 'awful': -1.5, 'horrible': -1.8, 'worst': -1.8,
            'hate': -2.0, 'hated': -2.0, 'dislike': -1.3, 'don\'t like': -1.3,
            'no': -1.2, 'nope': -1.2, 'nah': -1.2, 'not': -1.2,
            'cry': -1.8, 'crying': -2.0, 'tears': -1.8, 'tearful': -1.8,
            'angry': -1.8, 'mad': -1.8, 'annoyed': -1.3, 'bothered': -1.3,
            'tired': -1.3, 'exhausted': -1.3, 'sleepy': -1.2, 'drained': -1.3,
            'sick': -1.5, 'ill': -1.5, 'unwell': -1.5, 'poorly': -1.5,
            'scared': -1.5, 'afraid': -1.5, 'fear': -1.5, 'worried': -1.5,
            'sorry': -1.3, 'apologize': -1.3, 'regret': -1.5, 'guilty': -1.5,
            'ugh': -1.5, 'oh no': -1.5, 'oh dear': -1.5, 'oh god': -1.5,
            'darn': -1.3, 'dang': -1.3, 'drat': -1.3, 'shoot': -1.3,
            'crap': -1.5, 'damn': -1.5, 'hell': -1.5, 'shit': -1.5,
            'stupid': -1.5, 'dumb': -1.5, 'idiot': -1.8, 'fool': -1.5,
            'hate': -2.0, 'loathe': -2.0, 'despise': -2.0, 'abhor': -2.0,
            
            # Sad words - more complex
            'miserable': -2.0, 'unhappy': -1.8, 'heartbroken': -2.0, 'devastated': -2.0,
            'grief': -2.0, 'grieving': -2.0, 'mourning': -2.0, 'sorrow': -2.0,
            'furious': -2.0, 'scolded': -1.8, 'yelled': -1.8, 'frustrated': -1.5,
            'irritated': -1.3, 'agitated': -1.5, 'hurt': -1.5, 'pain': -1.5,
            'suffering': -1.8, 'distressed': -1.8, 'anxious': -1.5, 'stressed': -1.5,
            'overwhelmed': -1.8, 'disappointed': -1.5, 'let down': -1.5,
            'betrayed': -2.0, 'abandoned': -2.0, 'lonely': -1.8, 'isolated': -1.5,
            'rejected': -1.8, 'excluded': -1.5, 'burned out': -1.5,
            'desperate': -2.0, 'hopeless': -2.0, 'helpless': -1.8, 'powerless': -1.8,
            'trapped': -1.8, 'stuck': -1.5, 'confused': -1.3, 'lost': -1.5,
            'empty': -1.8, 'numb': -1.5, 'dead': -2.0, 'dying': -2.0,
            'broken': -1.8, 'shattered': -2.0, 'destroyed': -2.0, 'ruined': -1.8,
            'wasted': -1.5, 'useless': -1.5, 'worthless': -1.8, 'pointless': -1.5
        }
        
        # Define emotional phrases and their weights
        self.emotional_phrases = {
            # Happy phrases - simple and common
            'very happy': 2.0, 'so happy': 2.0, 'really happy': 2.0,
            'feeling good': 1.3, 'doing good': 1.3, 'all good': 1.3,
            'having fun': 1.5, 'lots of fun': 1.5, 'so much fun': 1.5,
            'love it': 1.8, 'love this': 1.8, 'love that': 1.8,
            'makes me happy': 1.5, 'feel happy': 1.5, 'look happy': 1.5,
            'good day': 1.3, 'great day': 1.5, 'nice day': 1.3,
            'good time': 1.3, 'great time': 1.5, 'nice time': 1.3,
            'good mood': 1.3, 'great mood': 1.5, 'nice mood': 1.3,
            'thank you': 1.3, 'thanks a lot': 1.3, 'thank you so much': 1.5,
            'you\'re welcome': 1.2, 'no problem': 1.2, 'my pleasure': 1.3,
            'good morning': 1.2, 'good afternoon': 1.2, 'good evening': 1.2,
            'good night': 1.2, 'sweet dreams': 1.3, 'take care': 1.2,
            'see you': 1.2, 'bye bye': 1.2, 'goodbye': 1.2,
            
            # Happy phrases - more complex
            'extremely happy': 2.0, 'overjoyed': 2.0, 'on top of the world': 2.0,
            'feeling great': 1.5, 'feeling amazing': 1.8, 'feeling wonderful': 1.8,
            'feeling blessed': 1.8, 'feeling grateful': 1.8, 'feeling loved': 2.0,
            'having a great day': 1.5, 'having an amazing day': 1.8,
            'could not be happier': 2.0, 'never been happier': 2.0,
            'full of joy': 1.8, 'bursting with joy': 2.0, 'over the moon': 2.0,
            'walking on air': 1.8, 'in seventh heaven': 1.8,
            'living the dream': 1.8, 'living my best life': 1.8,
            'everything is perfect': 2.0, 'life is good': 1.5,
            'feeling blessed': 1.8, 'counting my blessings': 1.8,
            'grateful for everything': 1.8, 'thankful for everything': 1.8,
            
            # Sad phrases - simple and common
            'very sad': -2.0, 'so sad': -2.0, 'really sad': -2.0,
            'feeling bad': -1.5, 'doing bad': -1.5, 'not good': -1.5,
            'no fun': -1.5, 'not fun': -1.5, 'boring': -1.3,
            'hate it': -1.8, 'hate this': -1.8, 'hate that': -1.8,
            'makes me sad': -1.5, 'feel sad': -1.5, 'look sad': -1.5,
            'bad day': -1.5, 'terrible day': -1.8, 'awful day': -1.8,
            'bad time': -1.5, 'terrible time': -1.8, 'awful time': -1.8,
            'bad mood': -1.5, 'terrible mood': -1.8, 'awful mood': -1.8,
            'oh no': -1.5, 'oh dear': -1.5, 'oh god': -1.5,
            'what a mess': -1.5, 'what a disaster': -1.8,
            'this sucks': -1.5, 'this is terrible': -1.8,
            'i can\'t': -1.5, 'i can\'t do this': -1.8,
            'leave me alone': -1.5, 'go away': -1.5,
            
            # Sad phrases - more complex
            'extremely sad': -2.0, 'feeling down': -1.5, 'feeling blue': -1.5,
            'feeling terrible': -1.8, 'feeling awful': -1.8, 'feeling miserable': -2.0,
            'feeling depressed': -2.0, 'feeling hopeless': -2.0, 'feeling helpless': -1.8,
            'having a bad day': -1.5, 'having a terrible day': -1.8,
            'at my lowest': -2.0, 'at rock bottom': -2.0, 'in a dark place': -2.0,
            'crying badly': -2.0, 'crying a lot': -2.0, 'crying my eyes out': -2.0,
            'scolded badly': -2.0, 'scolded me': -1.8, 'yelled at me': -1.8,
            'shouted at me': -1.8, 'made me cry': -2.0, 'hurt my feelings': -1.8,
            'breaking my heart': -2.0, 'tearing me apart': -2.0,
            'can\'t stop crying': -2.0, 'crying nonstop': -2.0,
            'feeling like a failure': -1.8, 'feeling worthless': -1.8,
            'at the end of my rope': -1.8, 'ready to give up': -1.8,
            'life is terrible': -2.0, 'everything is awful': -2.0,
            'nothing is working': -1.8, 'everything is going wrong': -1.8,
            'i hate my life': -2.0, 'i want to die': -2.0,
            'i can\'t take it anymore': -2.0, 'i give up': -1.8,
            'nobody cares': -1.8, 'nobody understands': -1.8,
            'i\'m all alone': -1.8, 'i feel so alone': -1.8,
            'i\'m so tired': -1.5, 'i\'m exhausted': -1.5,
            'i\'m so stressed': -1.5, 'i\'m overwhelmed': -1.8,
            'i\'m so worried': -1.5, 'i\'m so anxious': -1.5,
            'i\'m so scared': -1.5, 'i\'m so afraid': -1.5,
            'i\'m so angry': -1.8, 'i\'m so mad': -1.8,
            'i\'m so frustrated': -1.5, 'i\'m so annoyed': -1.5,
            'i\'m so disappointed': -1.5, 'i\'m so let down': -1.5,
            'i\'m so hurt': -1.5, 'i\'m so upset': -1.5,
            'i\'m so sad': -1.5, 'i\'m so unhappy': -1.8,
            'i\'m so miserable': -2.0, 'i\'m so depressed': -2.0
        }

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Mood Analyzer")
        self.root.geometry("800x600")

        # Create main container
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Input Section
        input_frame = ttk.LabelFrame(main_container, text="Input", padding="5")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Calendar
        self.cal = tkcalendar.DateEntry(input_frame, width=12, background='darkblue',
                                     foreground='white', borderwidth=2)
        self.cal.grid(row=0, column=0, padx=5, pady=5)

        # Text Input
        self.text_input = tk.Text(input_frame, height=3, width=40)
        self.text_input.grid(row=0, column=1, padx=5, pady=5)

        # Buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=0, column=2, padx=5, pady=5)

        self.voice_button = ttk.Button(button_frame, text="Record Voice", command=self.record_voice)
        self.voice_button.grid(row=0, column=0, padx=2)

        self.analyze_button = ttk.Button(button_frame, text="Analyze Text", command=self.analyze_text)
        self.analyze_button.grid(row=0, column=1, padx=2)

        # Analysis Section
        analysis_frame = ttk.LabelFrame(main_container, text="Analysis", padding="5")
        analysis_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Pie Chart
        self.fig = Figure(figsize=(6, 4))
        self.pie_chart = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, analysis_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, padx=5, pady=5)

        # Report Section
        report_frame = ttk.LabelFrame(main_container, text="Reports", padding="5")
        report_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Report Buttons
        self.date_range_button = ttk.Button(report_frame, text="Date Range Report", 
                                          command=self.show_date_range_report)
        self.date_range_button.grid(row=0, column=2, padx=5, pady=5)

        # Status Label
        self.status_label = ttk.Label(main_container, text="")
        self.status_label.grid(row=3, column=0, columnspan=2, pady=5)

    def analyze_text(self):
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter some text to analyze")
            return

        selected_date = self.cal.get_date()
        self.process_input(text, "", selected_date)

    def record_voice(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            self.status_label.config(text="Adjusting for ambient noise... Please wait...")
            self.root.update()
            recognizer.adjust_for_ambient_noise(source, duration=1)
            self.status_label.config(text="Ready! Say something about your day...")
            self.root.update()
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                text = recognizer.recognize_google(audio)
                self.status_label.config(text=f"You said: {text}")
                selected_date = self.cal.get_date()
                self.process_input("", text, selected_date)
            except sr.WaitTimeoutError:
                self.status_label.config(text="No speech detected within timeout period")
            except sr.UnknownValueError:
                self.status_label.config(text="Speech was not understood")
            except sr.RequestError as e:
                self.status_label.config(text=f"Could not request results; {e}")

    def analyze_sentiment(self, text):
        # Convert to lowercase for matching
        text = text.lower()
        
        # Get base sentiment from TextBlob
        blob = TextBlob(text)
        sentiment = blob.sentiment.polarity
        
        # Adjust sentiment based on emotional keywords
        for keyword, weight in self.emotional_keywords.items():
            if keyword in text:
                sentiment += weight
        
        # Adjust sentiment based on emotional phrases
        for phrase, weight in self.emotional_phrases.items():
            if phrase in text:
                sentiment += weight
        
        # Check for negations and intensifiers
        negations = ['not', "n't", 'never', 'no']
        intensifiers = ['very', 'really', 'extremely', 'absolutely', 'completely', 'totally']
        
        # Handle negations
        for negation in negations:
            if negation in text:
                words = text.split()
                try:
                    neg_index = words.index(negation)
                    # Look at the next few words after negation
                    for i in range(1, 4):
                        if neg_index + i < len(words):
                            word = words[neg_index + i]
                            if word in self.emotional_keywords:
                                sentiment -= 2 * self.emotional_keywords[word]
                except ValueError:
                    continue
        
        # Handle intensifiers
        for intensifier in intensifiers:
            if intensifier in text:
                words = text.split()
                try:
                    int_index = words.index(intensifier)
                    # Look at the next few words after intensifier
                    for i in range(1, 3):
                        if int_index + i < len(words):
                            word = words[int_index + i]
                            if word in self.emotional_keywords:
                                sentiment *= 1.5  # Amplify the sentiment
                except ValueError:
                    continue
        
        # Normalize sentiment to be between -1 and 1
        sentiment = max(min(sentiment, 1.0), -1.0)
        
        return sentiment

    def process_input(self, text_input, voice_input, date):
        # Analyze sentiment
        text_to_analyze = text_input if text_input else voice_input
        sentiment = self.analyze_sentiment(text_to_analyze)

        # Determine mood with adjusted thresholds
        if sentiment > 0.2:
            mood = 'Happy'
        elif sentiment < -0.2:
            mood = 'Sad'
        else:
            mood = 'Neutral'

        # Update local data
        self.mood_data[mood] += 1
        self.weekly_mood.append(mood)

        # Save to database
        self.db.save_mood_entry(date, text_input, voice_input, sentiment, mood)

        # Update GUI
        self.update_gui()
        self.status_label.config(text=f"Analysis complete! Mood: {mood} (Sentiment: {sentiment:.2f})")

    def update_gui(self):
        # Clear the previous plot
        self.pie_chart.clear()
        
        # Get the current mood data
        moods = list(self.mood_data.keys())
        values = list(self.mood_data.values())
        
        # Calculate total for percentage
        total = sum(values)
        
        # Only create pie chart if there's data
        if total > 0:
            # Create pie chart with percentages
            self.pie_chart.pie(values, 
                             labels=moods,
                             autopct=lambda pct: f'{pct:.1f}%\n({int(pct*total/100)})',
                             startangle=90)
            
            # Add a title
            self.pie_chart.set_title('Mood Distribution')
            
            # Ensure the pie chart is circular
            self.pie_chart.axis('equal')
            
            # Add a legend
            self.pie_chart.legend(moods, title="Moods", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
            
            # Adjust layout to prevent label cutoff
            self.fig.tight_layout()
        
        # Update the canvas
        self.canvas.draw()

    def show_daily_report(self):
        selected_date = self.cal.get_date()
        analysis = self.db.get_daily_analysis(selected_date)
        if analysis:
            self.show_report_window("Daily Analysis", analysis)
        else:
            messagebox.showinfo("Info", "No data available for this date")

    def show_weekly_report(self):
        selected_date = self.cal.get_date()
        week_start = selected_date - timedelta(days=selected_date.weekday())
        analysis = self.db.get_weekly_analysis(week_start)
        if analysis:
            self.show_report_window("Weekly Analysis", analysis)
        else:
            messagebox.showinfo("Info", "No data available for this week")

    def show_date_range_report(self):
        # Create a new window for date range selection
        range_window = tk.Toplevel(self.root)
        range_window.title("Select Date Range")
        range_window.geometry("300x150")

        ttk.Label(range_window, text="Start Date:").pack(pady=5)
        start_cal = tkcalendar.DateEntry(range_window, width=12, background='darkblue',
                                      foreground='white', borderwidth=2)
        start_cal.pack(pady=5)

        ttk.Label(range_window, text="End Date:").pack(pady=5)
        end_cal = tkcalendar.DateEntry(range_window, width=12, background='darkblue',
                                    foreground='white', borderwidth=2)
        end_cal.pack(pady=5)

        def generate_report():
            entries = self.db.get_mood_entries_by_date_range(start_cal.get_date(), 
                                                           end_cal.get_date())
            if entries:
                self.show_report_window("Date Range Analysis", entries)
            else:
                messagebox.showinfo("Info", "No data available for selected date range")

        ttk.Button(range_window, text="Generate Report", 
                  command=generate_report).pack(pady=10)

    def show_report_window(self, title, data):
        report_window = tk.Toplevel(self.root)
        report_window.title(title)
        report_window.geometry("600x400")

        # Create text widget for report
        report_text = tk.Text(report_window, wrap=tk.WORD, padx=10, pady=10)
        report_text.pack(fill=tk.BOTH, expand=True)

        # Format and display the data
        if isinstance(data, dict):
            report_text.insert(tk.END, f"{title}\n\n")
            for key, value in data.items():
                report_text.insert(tk.END, f"{key}: {value}\n")
        else:
            report_text.insert(tk.END, f"{title}\n\n")
            for entry in data:
                report_text.insert(tk.END, f"Date: {entry['date']}\n")
                report_text.insert(tk.END, f"Mood: {entry['mood_category']}\n")
                report_text.insert(tk.END, f"Sentiment Score: {entry['sentiment_score']}\n")
                report_text.insert(tk.END, "-" * 50 + "\n")

        report_text.config(state=tk.DISABLED)

    def run(self):
        self.root.mainloop()
        self.db.close()

if __name__ == "__main__":
    app = MoodAnalyzer()
    app.run()
