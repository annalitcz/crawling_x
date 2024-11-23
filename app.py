import tweepy
from dotenv import load_dotenv
import os
import csv
import time
from flask import Flask, render_template, request, send_file, after_this_request

# Muat variabel dari file .env
load_dotenv()

# Ambil API keys dari file .env
api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

# Otorisasi dengan Tweepy
auth = tweepy.OAuthHandler(api_key, api_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# Inisialisasi Flask app
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    tweets = []
    csv_filename = None  # Untuk menyimpan nama file CSV yang dihasilkan
    if request.method == "POST":
        # Ambil kata kunci dari form
        keyword = request.form.get("keyword")
        
        # Cari tweet berdasarkan keyword
        try:
            fetched_tweets = tweepy.Cursor(api.search_tweets, q=keyword, lang="id", tweet_mode="extended").items(10)
            tweets = [{"username": tweet.user.screen_name, "tweet": tweet.full_text} for tweet in fetched_tweets]

            # Simpan hasil ke file CSV
            csv_filename = save_tweets_to_csv(keyword, tweets)
            
        except Exception as e:
            print("Error:", e)
            tweets = []

    return render_template("index.html", tweets=tweets, csv_filename=csv_filename)

def save_tweets_to_csv(keyword, tweets):
    # Menentukan nama file berdasarkan kata kunci pencarian
    filename = f"{keyword.replace(' ', '_')}_tweets.csv"
    
    # Menulis tweet ke file CSV
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["username", "tweet"])
        writer.writeheader()  # Menulis header CSV
        writer.writerows(tweets)  # Menulis data tweet

    print(f"Data berhasil disimpan di file {filename}")
    return filename

@app.route("/download/<filename>")
def download_file(filename):
    # Menggunakan Flask's send_file untuk mengirim file ke pengguna
    @after_this_request
    def remove_file(response):
        try:
            os.remove(filename)  # Menghapus file setelah diunduh
            print(f"File {filename} berhasil dihapus setelah diunduh")
        except Exception as e:
            print(f"Error menghapus file: {e}")
        return response
    
    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
