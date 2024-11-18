import requests
import base64
import solders
from solana.rpc.api import Client
from solders.keypair import Keypair
from solders.transaction import Transaction as SoldersTransaction
from spl.token.constants import ASSOCIATED_TOKEN_PROGRAM_ID, TOKEN_PROGRAM_ID
from solana.rpc.types import TxOpts
from solana.rpc.commitment import Confirmed
import time


TOKEN_MINT_ADDRESSES = {
    "SOL": "So11111111111111111111111111111111111111112",  # Solana native SOL token mint address
    "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC mint address
    "USDT": "Es9vMFrkEMwBBz25RPXTAhdXKHiQ6yZG6PhUJrZ17eKk",  # USDT mint address
    "BTC": "8e3a19e0190d153b68cc52cb4d9b88f84c6348c1c7d9",  # Bitcoin mint address on Solana (example)
}

# Function to get mint address from token name or return the address if it's already a token address
def get_token_mint_address(token_input):
    # Check if the input is a known token name
    if token_input in TOKEN_MINT_ADDRESSES:
        return TOKEN_MINT_ADDRESSES[token_input]
    # If the input is not a known token name, assume it is an actual token address (check length and format)
    else:
         return token_input



def get_input(prompt, default_value):
    user_input = input(prompt + f" (default: {default_value}): ")
    return user_input if user_input else default_value



# Define a function to perform the swap
def perform_swap(amount, input_token_address, output_token_address, private_key_string, user_public_key, priorityFees):
    # Initialize the Solana Client (mainnet)
    client = Client("https://go.getblock.io/6f86d5a2341e46a3a994d049101ce34a")

# Create the sender Keypair from the private key string
    sender = Keypair.from_base58_string(private_key_string)
    sender_pubkey = sender.pubkey()
    print(input_token_address, output_token_address, type(input_token_address))

    quote_url = f"https://quote-api.jup.ag/v6/quote?inputMint={input_token_address}" \
                f"&outputMint={output_token_address}&amount={int(amount * 10**9)}&slippageBps=10"

    response = requests.get(quote_url)
    quote_data = response.json()
    print(quote_data)

    # Check the quote response

    # Construct the body of the POST request for swap response
    swap_data = {
        "quoteResponse": quote_data,  # the entire quote response
        "userPublicKey": user_public_key,  # user's public key
        "wrapAndUnwrapSol": True,  # Whether to auto-wrap and unwrap SOL
        "prioritizationFeeLamports": {
            "priorityLevelWithMaxLamports": {
                "maxLamports": priorityFees,
                "global": False,
                "priorityLevel": "high"
            }
        }
    }

    # Send the POST request to Jupiter API's /swap endpoint
    swap_url = "https://quote-api.jup.ag/v6/swap"
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.request("POST",swap_url, headers=headers, json=swap_data)
    response = response.json()

    if 'swapTransaction' not in response:
        print("No swap transaction found in the response.")
        exit()

    swp = response['swapTransaction']
    swap_transaction_buf = base64.b64decode(swp)


    swap_transaction = solders.transaction.VersionedTransaction.from_bytes(base64.b64decode(swp))
    blockhash_response = client.get_latest_blockhash()
    recent_blockhash = blockhash_response.value.blockhash

    signature = sender.sign_message(solders.message.to_bytes_versioned(swap_transaction.message))
    signed_tx = solders.transaction.VersionedTransaction.populate(swap_transaction.message, [signature])
    encoded_tx = base64.b64encode(bytes(signed_tx)).decode('utf-8')
    

    # Send the transaction
    try:
        txid = client.send_transaction(signed_tx,opts=TxOpts(skip_confirmation=False, preflight_commitment=Confirmed)).value
        print("Your transaction Id is: ",txid)
        return txid
    except Exception as e:
        print(f"Transaction failed: {e}")
        return None

        

# Example usage of the function
if __name__ == "__main__":
    # Example inputs
    amount = float(get_input("Enter the amount to swap (in SOL): ", 0.00001))
    input_token_address = get_token_mint_address(get_input("Enter the input token address (e.g. SOL mint address): ", "So11111111111111111111111111111111111111112"))
    output_token_address = get_token_mint_address(get_input("Enter the output token address (e.g. USDC mint address): ", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"))
    private_key_string = get_input("Enter your private key (in base58 format): ", "Your private key")
    user_public_key = get_input("Enter your user public key: ", "your public key")
    priorityFees = int(get_input("Enter the prioritization fee (in lamports): ", 400000))
    
    # Call the perform_swap function
    transaction_id = perform_swap(amount, input_token_address, output_token_address, private_key_string, user_public_key, priorityFees)
    
    if transaction_id:
        print(f"Transaction was successful. Transaction ID: {transaction_id}")
    else:
        print("Transaction failed.")
