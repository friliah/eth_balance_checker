# eth_balance_checker

Shows total balance of all wallets and wallets with balance for specific tokens

## Getting Started

These instructions will get you a copy of the project up and running on your local machine. At the end you will get something like this:

![table](http://i65.tinypic.com/xojzp2.png)

![wallets](http://i64.tinypic.com/bgedtx.png)


### Prerequisites

You need Python:

1. Download [Python](https://www.python.org/downloads/release/python-370/), for Windows use ```Windows x86-64 executable installer```

2. Install it 

![Python Installer](http://i63.tinypic.com/oggqbn.png)


### Installing

1. Click on green button ```Clone or download```, select ```Download ZIP```, download and extract it.

2. Open command line in extracted folder ([how to open](https://www.thewindowsclub.com/how-to-open-command-prompt-from-right-click-menu)) and write ```pip install requirements.txt```


## Using

You need to replace test wallets in ```wallets.txt``` with yours (each  address starts from new line). Then just double click on  ```eth_balance_checker.py```

### Settings

You can change some settings editing the file ```eth_balance_checker.py```. Right click on it, select ```Edit with IDLE```. then in the end of the file in the row ```main('wallets.txt',last=None, show_individual_wallet_balance = False)```. First argument changes the name of the file with wallets, second argument shows, how many rows you want to check (e.g. 10 will only check first ten wallets), setting third argument to ```True``` will show you balance of every nonempty wallet during parsing)

## Built With

* [ethplorer-py](https://github.com/guillelo11/ethplorer-py) - Simple ethplorer.io API for python
