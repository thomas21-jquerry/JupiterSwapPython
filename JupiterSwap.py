import json
import requests
from solders.transaction import Transaction
from solders.pubkey import Pubkey
from solana.rpc.api import Client
from solders.system_program import TransferParams, transfer
from solders.message import Message
from solders.keypair import Keypair




# inputs
amount = 1.0  # Amount to swap (in SOL)
input_token_address = "So11111111111111111111111111111111111111112"  # Replace with your from token addess
output_token_address = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v" # Replace with your to token address
private_key_string = "REPLACE WITH YOUR PRIVATE KEY" # Your Private Key in base58 (import it from phantom)



client = Client("https://api.devnet.solana.com")


# Create the sender Keypair from private key bytes
sender =  Keypair.from_base58_string(private_key_string)

# Generate a keypair for the sender (or load from a private key)

# Print the sender's public key
print(f"Sender public key: {sender.pubkey()}")

# Example: Swap SOL for USDC
  # Token to swap to


# Step 2: Get the swap route from Jupiter API
JUPITER_API_URL = f"https://quote-api.jup.ag/v6/quote?inputMint={input_token_address}" \
                  f"&outputMint={output_token_address}&amount={int(amount * 10**9)}&slippageBps=50"

# Fetch the best swap route from Jupiter API
response = requests.get(JUPITER_API_URL)
quote_data = response.json()

sender_balance = client.get_balance(sender.pubkey())


# Step 3: Extract transaction instructions from the quote response
route_plan = quote_data['routePlan']
if len(route_plan) == 0:
    print("No route found!")
    exit()

# The routePlan is a list of dictionaries, each containing the swap info
swap_info = route_plan[0]['swapInfo']
input_mint = swap_info['inputMint']
output_mint = swap_info['outputMint']
in_amount = int(swap_info['inAmount'])
out_amount = int(swap_info['outAmount'])
amm_key = Pubkey.from_string(swap_info['ammKey']) 
# swap_instructions = swap_info['transaction']['instructions']

# Step 4: Prepare the transaction to perform the swap

instruction = transfer((TransferParams(from_pubkey=sender.pubkey(), to_pubkey=Pubkey.from_string(output_mint), lamports=1_000_000)))




# Add the instructions to the transaction
# for instruction in swap_instructions:
#     # Ensure each instruction is properly formatted
#     instruction_data = instruction['data']  # Fetch instruction data
#     keys = instruction['keys']  # Fetch the keys for the instruction (signers, accounts)
    
#     # Add instruction to the transaction (Note: You'll need to convert this into Solana transaction format)
#     transaction.add(instruction_data)

# Step 5: Get recent blockhash from Solana
blockhash_response = client.get_latest_blockhash()
recent_blockhash = blockhash_response.value.blockhash
message = Message(instructions=[instruction], payer=sender.pubkey())
transaction = Transaction(
    from_keypairs=[sender],  # List of keypairs that will sign the transaction
    message=message,
    recent_blockhash=recent_blockhash
)


# Step 6: Sign the transaction with the sender's keypair
transaction.sign([sender],recent_blockhash)



# Step 7: Send the transaction to Solana
send_response = client.send_transaction(transaction)

# Step 8: Print the transaction signature
print(f"Swap transaction sent! Transaction signature: {send_response}")
