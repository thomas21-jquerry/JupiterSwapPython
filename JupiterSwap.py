
import requests
import base64
import solders
import solana
from solders.keypair import Keypair
from solana.transaction import Transaction
from solders.pubkey import Pubkey
from solders.message import Message
from solana.rpc.api import Client
from solders.system_program import TransferParams, transfer
from solders.transaction import Transaction as SoldersTransaction
from spl.token.instructions import create_associated_token_account
from solana.rpc.types import TxOpts
from spl.token.constants import ASSOCIATED_TOKEN_PROGRAM_ID, TOKEN_PROGRAM_ID
from solana.rpc.commitment import Confirmed
from solana.rpc.commitment import Processed
from solders.message import MessageV0
import time


# Inputs
amount = 0.00001  # Amount to swap (in SOL)
input_token_address = "So11111111111111111111111111111111111111112"  # SOL mint address
output_token_address = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC mint address
private_key_string = ""  # Replace with your private key
user_public_key = "" # replace with your public key

# Initialize the Solana Client (mainnet)
client = Client("https://go.getblock.io/6f86d5a2341e46a3a994d049101ce34a")

# Create the sender Keypair from the private key string
sender = Keypair.from_base58_string(private_key_string)
sender_pubkey = sender.pubkey()
print(f"Sender public key: {sender_pubkey}")

quote_url = f"https://quote-api.jup.ag/v6/quote?inputMint={input_token_address}" \
            f"&outputMint={output_token_address}&amount={int(amount * 10**9)}&slippageBps=10"
response = requests.get(quote_url)
quote_data = response.json()

# Check the quote response
print("Quote Response:", quote_data)



# Construct the body of the POST request for swap response
swap_data = {
    "quoteResponse": quote_data,  # the entire quote response
    "userPublicKey": user_public_key,  # user's public key
    "wrapAndUnwrapSol": True,  # Whether to auto-wrap and unwrap SOL
}

# Send the POST request to Jupiter API's /swap endpoint
swap_url = "https://quote-api.jup.ag/v6/swap"
headers = {
    "Content-Type": "application/json"
}

response = requests.request("POST",swap_url, headers=headers, json=swap_data)
print(response.json())
response = response.json()

if 'swapTransaction' not in response:
    print("No swap transaction found in the response.")
    exit()

swp = response['swapTransaction']
swap_transaction_buf = base64.b64decode(swp)


swap_transaction = solders.transaction.VersionedTransaction.from_bytes(base64.b64decode(swp))
blockhash_response = client.get_latest_blockhash()
recent_blockhash = blockhash_response.value.blockhash
print(f"Recent blockhash: {recent_blockhash}")


signature = sender.sign_message(solders.message.to_bytes_versioned(swap_transaction.message))
signed_tx = solders.transaction.VersionedTransaction.populate(swap_transaction.message, [signature])
encoded_tx = base64.b64encode(bytes(signed_tx)).decode('utf-8')
# txid = client.send_transaction(
#         signed_tx,opts=TxOpts(skip_confirmation=False, preflight_commitment=Confirmed)
#     ).value
# print("Your transaction Id is: ",txid)

for attempts in range(5):
    try:
        txid = client.send_transaction(signed_tx,opts=TxOpts(skip_confirmation=False, preflight_commitment=Processed)).value
        print("Your transaction Id is: ",txid)
        break
    except Exception as e:
        print(f"Attempt {attempts + 1} failed due to timeout. Retrying in {5} seconds... [ reason: ", e, "]")
        time.sleep(5)

# raise Exception("Transaction failed after multiple attempts due to timeouts.")

