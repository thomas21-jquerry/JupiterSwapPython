# JupiterSwapPython
## To Run On Google Colab
1. Run
   ```
       !pip install solana
       !pip install solders
       !pip install requests
    ```
2. Copy the Code in the file
3. Paste in google collab cell
4. Change the inputs
   ```
    amount = 1.0  # Amount to swap (in SOL)
    input_token_address = "So11111111111111111111111111111111111111112"  # Replace with your from token addess currently this is solana address
    output_token_address = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v" # Replace with your to token address currently this is USDC address
    private_key_string = "REPLACE WITH YOUR PRIVATE KEY" # Your own private key in base58String
   ```
5. Run the cell to send the swap
6. Check the transaction in solscan
