# LazyInterface trading assistant

Command line interface for trading on poloniex

## Instalation for linux
### Prerequisite

Have python 2.7 installed

git clone https://github.com/Tulsene/LazyInterface
cd LazyInterface
git checkout dev
python Lazy.py

### Configuration

Proposal for handling API Keys in ENV_VARS
Exemple usage on windows (on a .bat file)

```
SET API_KEY="7JDLBZMI-HPWMRUVZ-D968SXSP-RJ92NSQK"&& SET API_SECRET="f745921a6e73eef13b9f72a4ab05f0a77a311f4cfa40a5b968e0ce3229626471cf4b832627791eb1c5e4352e7770dbd684d75d78f2acf3aa8fdb9ed21b63119"&& python Lazy.py
```

Equivalent for Debian in a start.sh :

```
#!/bin/sh
export API_KEY=7JDLBZMI-HPWMRUVZ-D968SXSP-RJ92NSQK
export API_SECRET=f745921a6e73eef13b9f72a4ab05f0a77a311f4cfa40a5b968e0ce3229626471cf4b832627791eb1c5e4352e7770dbd684d75d78f2acf3aa8fdb9ed21b63119
python LazyInterface.py
```

### Startup

```sh start.sh```

## What is it?

LazyInterface is a simple interface in command line for trading on poloniex marketplace. 

You can choose the buy_pair and the sell_pair in LazyInterface.py, otherwise you'll have to set it up at every start.

Follow menus and enjoy!