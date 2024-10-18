This was inspired by a blog post in Jet Brains: Django Project Ideas. I hadn't used Django in a couple of years and I wanted to build with it again because I like the framework and Python generally. This was the description: 

>Stock exchange analysis
Build a stock market analysis platform using Django, a project that combines data science, machine learning, and the Django REST framework. It also offers more practical experience in handling lots of real-time data. 

>Import historical stock prices, run technical analyses, and generate predictions using machine learning. Create RESTful APIs for data retrieval and analysis results, and integrate external APIs for real-time market data. Implement visualization tools to display trends, predictions, and alerts.

From: https://blog.jetbrains.com/pycharm/2024/09/django-project-ideas/#stock-exchange-analysis

Thus far, I'm able to read data from a CSV, as well as bring in data from yfinance. The data is stored in a PostGreSQL database and display in a list, then data for each stock displayed on its own page. 

This is also an experiment in building with Chat GPT as a pair programmer, using the Django custom GPT. So far I've found it very helpful. 

Next steps will be: 
1) generate vizualizations
2) run technical analysis
3) generate predictions using machine learning
4) create RESTful APIs to bring in real-time data. 
5) make the interface more user friendly, possibly using Typescript. 

Because I'm only using this app for myself, for the time being it will probably remain local, though perhaps I'll eventually host it on the web, and put it behind a wall. 