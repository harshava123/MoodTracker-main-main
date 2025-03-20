import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import json

class DatabaseConnection:
    def __init__(self):
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'root',
            'database': 'mood_tracker'
        }
        self.create_tables()

    def get_connection(self):
        return mysql.connector.connect(**self.config)

    def create_tables(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Create mood_entries table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mood_entries (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    date DATE NOT NULL,
                    text_input TEXT,
                    voice_input TEXT,
                    sentiment_score FLOAT NOT NULL,
                    mood_category VARCHAR(50) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.commit()

        except Exception as e:
            print(f"Error creating tables: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def save_mood_entry(self, date, text_input, voice_input, sentiment_score, mood_category):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            query = '''
                INSERT INTO mood_entries (date, text_input, voice_input, sentiment_score, mood_category)
                VALUES (%s, %s, %s, %s, %s)
            '''
            values = (date, text_input, voice_input, sentiment_score, mood_category)
            
            cursor.execute(query, values)
            conn.commit()

            return cursor.lastrowid

        except Exception as e:
            print(f"Error saving mood entry: {str(e)}")
            raise e
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def get_mood_entries_by_date_range(self, start_date, end_date):
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            query = '''
                SELECT id, date, text_input, voice_input, sentiment_score, mood_category
                FROM mood_entries
                WHERE date BETWEEN %s AND %s
                ORDER BY date DESC
            '''
            cursor.execute(query, (start_date, end_date))
            entries = cursor.fetchall()

            # Convert date objects to string format
            for entry in entries:
                entry['date'] = entry['date']

            return entries

        except Exception as e:
            print(f"Error getting mood entries: {str(e)}")
            raise e
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def get_weekly_analysis(self, week_start_date):
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            # Calculate week end date
            week_end_date = week_start_date + timedelta(days=6)

            query = '''
                SELECT 
                    %s as week_start_date,
                    COUNT(CASE WHEN mood_category = 'Happy' THEN 1 END) as happy_count,
                    COUNT(CASE WHEN mood_category = 'Sad' THEN 1 END) as sad_count,
                    COUNT(CASE WHEN mood_category = 'Neutral' THEN 1 END) as neutral_count,
                    AVG(sentiment_score) as average_sentiment
                FROM mood_entries
                WHERE date BETWEEN %s AND %s
                GROUP BY YEARWEEK(date)
                HAVING COUNT(*) > 0
            '''
            cursor.execute(query, (week_start_date, week_start_date, week_end_date))
            result = cursor.fetchone()

            if result:
                result['week_start_date'] = week_start_date
                return result
            return None

        except Exception as e:
            print(f"Error getting weekly analysis: {str(e)}")
            raise e
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def get_daily_analysis(self, month_start_date):
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            # Calculate month end date
            next_month = month_start_date.replace(day=28) + timedelta(days=4)
            month_end_date = next_month - timedelta(days=next_month.day)

            query = '''
                SELECT 
                    %s as date,
                    COUNT(CASE WHEN mood_category = 'Happy' THEN 1 END) as happy_count,
                    COUNT(CASE WHEN mood_category = 'Sad' THEN 1 END) as sad_count,
                    COUNT(CASE WHEN mood_category = 'Neutral' THEN 1 END) as neutral_count,
                    AVG(sentiment_score) as average_sentiment
                FROM mood_entries
                WHERE date BETWEEN %s AND %s
                GROUP BY YEAR(date), MONTH(date)
                HAVING COUNT(*) > 0
            '''
            cursor.execute(query, (month_start_date, month_start_date, month_end_date))
            result = cursor.fetchone()

            if result:
                result['date'] = month_start_date
                return result
            return None

        except Exception as e:
            print(f"Error getting daily analysis: {str(e)}")
            raise e
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def get_recent_entries(self, limit=5):
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            query = '''
                SELECT id, date, text_input, voice_input, sentiment_score, mood_category
                FROM mood_entries
                ORDER BY date DESC, created_at DESC
                LIMIT %s
            '''
            cursor.execute(query, (limit,))
            entries = cursor.fetchall()

            # Convert date objects to string format
            for entry in entries:
                entry['date'] = entry['date']

            return entries

        except Exception as e:
            print(f"Error getting recent entries: {str(e)}")
            raise e
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def close(self):
        if hasattr(self, 'connection') and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed") 