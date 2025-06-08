import requests
from twilio.rest import Client
import os
import random


"""
This project automates a daily WhatsApp message that sends you a quick and insightful briefing every morning — including:
📈 Real-time stock updates
💼 Top remote data engineering or other related job opportunities
The goal is to deliver high-leverage, life-changing information directly to your phone, every day at the same time — fully automated.
This can be for students, professionals, or anyone who wants to stay updated on stocks and job opportunities in the tech industry.
"""

"CONFIG"
###
#For THE API KEY, TWILIO SID, AUTH TOKEN, FROM AND TO WHATSAPP NUMBERS
#You can get the API KEY from https://www.alphavantage.co/support/#api-key
#You can get the TWILIO SID and AUTH TOKEN from https://www.twilio.com/console
#You can get the FROM and TO WHATSAPP numbers from https://www.twilio.com/console/whatsapp/sandbox
#You can set the environment variables in Github SECRETIONS or in your local environment
###

API_KEY = os.getenv("API_KEY")
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH")
FROM_WHATSAPP = os.getenv("FROM_WHATSAPP")
TO_WHATSAPP = os.getenv("TO_WHATSAPP")




#EXTRACTED AND TRANSFORMED INFO FROM STOCKS AND JOBS
#LOAD INFO TO WHATSAPP MESSAGE

"""
Fetches and summarizes stock data for a list of tickers using Alpha Vantage API.
Returns a formatted string with price, change, and percent change for each ticker.
Handles API/network errors and missing data gracefully.
"""
 
def get_daily_stock_summary(tickers, api_key):
    
    message_lines = []
    
    #we will extract info from tickers/companies that we want see
    for ticker in tickers:
        url = (
            f"https://www.alphavantage.co/query"
            f"?function=GLOBAL_QUOTE&symbol={ticker}&apikey={api_key}"
        )
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses
            data = response.json()
        except requests.RequestException as e:
            message_lines.append(f"{ticker}: error fetching data({e})")
            continue
        except ValueError:
            message_lines.append(f"{ticker}: error parsing data")
            continue
        
        if "Global Quote" in data and "05. price" in data["Global Quote"]:
            try:
                price = float(data["Global Quote"]["05. price"])
                change = float(data["Global Quote"]["09. change"])
                pct_change = float(data["Global Quote"]["10. change percent"].strip('%'))     
                line = f"{ticker}:${price:.2f} ({change:.2f}, {pct_change:.2f}%)"
                message_lines.append(line)
            except (KeyError, ValueError):
                message_lines.append(f"{ticker}: data format error")
        else:
            message_lines.append(f"{ticker}: data unavailable ❌")
            
    return "\n".join(message_lines)
    


"""
Fetches and filters jobs using Alpha remotive API.
Returns a formatted string with job title, company, and link/url for each job.
Handles API errors and missing data gracefully.
"""

def get_daily_remote_data_jobs():
    
    # List of random search terms for remote jobs 
    random_searches = [
        "data", "developer", "designer", 
        "content writer", "software engineer",
        "data analyst",
    ]
    
    #Extract data from remotive.com
    url = "https://remotive.com/api/remote-jobs?search={}".format(random.choice(random_searches))
    
    print(f"this is the one {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        jobs = response.json().get('jobs',[])
    except requests.RequestException as e:
        return f"error fetching jobs: {e}"
    except ValueError:
        return "Error parsing job data"
    
    if not jobs:
        return "No jobs or internships was found for your search."
    
    #Transform data to title,company and url. the only info we need
    message_lines = []
    for job in jobs[:3]:
        title = job.get('title', 'No title')
        company = job.get('company_name', 'No company name')
        url = job.get('url', 'No URL')
        
        message_lines.append(f"{title} @ {company}\n{url}")
    
    return "\n\n".join(message_lines)



"""
Generates a daily briefing message with stock updates and remote job listings.
Returns a formatted string with greetings, stock updates, and job listings.
"""

def daily_briefing():
    stocks = get_daily_stock_summary(["AAPL","TSLA","MSFT"],API_KEY)
    jobs = get_daily_remote_data_jobs()
    
    
    message = (
        f"Welcome to the Daily Briefing Bot!. "
        f"This is your daily briefing with stock updates and remote job listings."
        f"🌞 A blissful Day!\n\n"
        f"📈 Stock Updates:\n{stocks}\n\n"
        f"💼 Top Remote Jobs:\n{jobs}\n\n"
        f"🔥 Have a Wonderful day!"   
    )
    return message

"""
This script loads stock data, remote jobs, and sends a daily briefing via WhatsApp using Twilio.
"""
def send_daily_message(body,account_sid, auth_token, from_whatsapp, to_whatsapp):
    client = Client(account_sid,auth_token)
    message = client.messages.create(
        body=body,
        from_=f"whatsapp:{from_whatsapp}",
        to = f"whatsapp:{to_whatsapp}"
    )
    print(f"message sent! SID: {message.sid}")
    
    
    
def main():
    # Generate the daily briefing message
    brief = daily_briefing()
    # Send the daily message via WhatsApp
    send_daily_message(brief, TWILIO_SID, TWILIO_AUTH, FROM_WHATSAPP, TO_WHATSAPP)
    
if __name__ == "__main__":
    main()