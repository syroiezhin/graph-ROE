# <p id="UP">Do you want to create a bot to analyze the crypto market?</p>

> Please note that I do not advertise or advise buying cryptocurrency, this review is written for informational purposes, and not to promote investing in a digital currency that has no growth prospects, except for speculating on investors' investments.

## <p align="center">Give thanks:&ensp;&ensp; 5168 7450 1701 5535 &ensp;&ensp;<a href="https://en.privatbank.ua/all-ways-to-receive-send-an-international-transfer"><img src="https://upload.wikimedia.org/wikipedia/uk/f/ff/%D0%9B%D0%BE%D0%B3%D0%BE%D1%82%D0%B8%D0%BF_%D0%9F%D1%80%D0%B8%D0%B2%D0%B0%D1%8224.png" width = "25" alt="Privat Bank UA"> </a></p>

### In this review, I will not focus on how program, made by me on the basis of ready-made packages, work. I want to make it clear how to run this package using anaconda on your macbook in order to receive signals from the program, and at your discretion to carry out any additional manipulations to improve this program. I see no prospects in this matter and there is no point in improving the program, as I did it out of curiosity, and gain experience in these arithmetic and design packages.

- [X] First of all, I recommend downloading [Anaconda 2.2.0](https://anaconda.cloud/installers).
- [X] Don't forget to download [VSCode 1.70.0](https://code.visualstudio.com/Download).
- [X] Download latest [Python 3.10.6](https://www.python.org/downloads/macos/)
- [X] Now let's do two important things before downloading the libraries:

1. Go to __the Anaconda__ application in the __Environment__ section and create a new environment

https://user-images.githubusercontent.com/86792918/183673558-62e5e7b8-0597-4cc5-8663-075f9d3a4405.mp4
> Need to create a new __interpreter__ with the newest __Python 3.10.4__ for __Anaconda__.

2. Now we need to include the new __interpreter__ in VSCode

https://user-images.githubusercontent.com/86792918/183674185-38935789-5ac1-444e-8b14-856b8d48e8f4.mp4
> Open the `GROE.py` project in __VSCode__, then in the lower right corner click on the __Python version__ _(in my case it is 3.9.12)_, then in the window that appears, find the newly created __interpreter__ _(in my case the name of __conda 3.10.4__)_.
- [X] Great, now we __download all the libraries__ used through the __VSCode terminal__:
```
conda install -c plotly plotly
conda install streamlit
pip install tradingview_ta
pip install requests
pip install pandas
pip install time
```
> If any errors occur, try to solve them by searching the Internet for a solution. Perhaps something has changed, or you haven't downloaded the pip installer.

- [X] To start the program, it remains to do the last three points:
1. First of all, you need to clone my repository on __your github account__. After cloning run the project folder via __VSCode__.

![Click Open-with-Github-Desktop button](https://github.com/syroiezhin/graph-ROE/blob/main/image/github.png "Click Open-with-Github-Desktop button")

2. Next, login to the __Streamlit__ site with a __github account__ and create _the first application_ on the [share.streamlit.io](https://share.streamlit.io/) site, referring to __your github__ clone of your project.

![Click New-app button in Streamlit site](https://github.com/syroiezhin/graph-ROE/blob/main/image/streamlit.png "Click New-app button in Streamlit site")

> .. or click __Paste-GitHub-URL__ button, and enter the URL to my repository.

3. Returning to the __VSCode__, you need to run the program `GROE.py` in the upper right corner, and then in the terminal _(after reading the appeal)_, copy the command to run, pasting it in the terminal.
```
  Warning: to view this Streamlit app on a browser, run it with the following command:

    streamlit run /Users/v.syroiezhin/Desktop/github/graph-ROE/GROE.py [ARGUMENTS]
```
> In my case, I will send the command `streamlit run /Users/../graph-ROE/GROE.py` in the terminal to launch the page.

#### If everything worked out for you, then the page in the browser will start by itself, and you will see the working program. I hope you like the result and I hope you found what you were looking for. I tried to make it as good as possible, and I count on your support. Read about me under the photo [on the main page](https://github.com/syroiezhin).

[⇪](#UP)
