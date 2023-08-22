# ⚡ Breez SDK CLI Wallet ⚡

![Sample output for the `info` command](img/info.png)

This is a command-line interface that allows you to manage a lightning node and its LSP connections. It's powered by a Greenlight node and the Breez SDK and its main purpose is to serve as a end-to-end demonstration of what's possible.

The main advantage of this setup is the ability to host a Lightning Node in the cloud but without exposing the private key material to third parties.

The Breez documentation provides some code snippets [here](https://sdk-doc.breez.technology/guide/send_onchain.html). In fact this small CLI client was created to test them out, and is now made available for anyone who needs a more complete sample code.

# 🔧 Installation
Follow the steps to compile the Breez SDK python bindings [here](https://github.com/breez/breez-sdk/tree/main/libs/sdk-bindings#python).

Once done copy the following files to the root directory:

- breez_sdk.py
- libbreez_sdk_bindings.dylib

# ⚙️ Configuration
You must just create a file called `secrets.txt` in the root directory of the project that will contain the secrets. A sample is provided at `secrets.sample.txt` so you can just:

```bash
$ cp secrets.sample.txt secrets.txt
```

And fill in the required secrets. The expected format of the file is as follows:

```
phrase: <your seed phrase>
invite_code: <your greenlight invite code>
api_key: <your breez sdk api code>
```

# 🎮 Usage
Use the following commands to interact with your Greenlight node:

```
Documented commands (type help <topic>):
========================================
balance              help              lnurl_withdraw         send         
exit                 info              pay_address            swap_progress
get_deposit_address  list_refundables  pay_invoice            txs          
get_invoice          lnurl_pay         reverse_swap_progress
```