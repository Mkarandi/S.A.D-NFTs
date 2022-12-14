################################################################################
# IMPORTS AND GETTERS
################################################################################
import os
import json
import openai
import imageio
import requests
from web3 import Web3
from PIL import Image
import streamlit as st
from io import BytesIO
from io import StringIO
from pathlib import Path
from streamlit_player import st_player
from transaction import send_transaction, get_balance, generate_account
from pinata import pin_file_to_ipfs, pin_json_to_ipfs, convert_data_to_json
from dotenv import load_dotenv
load_dotenv()
# Define and connect a new Web3 provider
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))

# Cache the contract on load
@st.cache(allow_output_mutation=True)
# Define the load_contract function

# Define the load_contract function
def load_contract():

    # Load the contract ABI
    with open(Path('./contracts/compiled/artregistry_abi.json')) as f:
        contract_abi = json.load(f)

    # Set the contract address (this is the address of the deployed contract)
    contract_address = os.getenv("SMART_CONTRACT_ADDRESS")

    # Get the contract
    contract = w3.eth.contract(
        address=contract_address,
        abi=contract_abi
    )

    return contract


# Load the contract
contract = load_contract()

# In this instance, we will be loading accounts from Ganache.
accounts = w3.eth.accounts
account = accounts[0]

################################################################################
# Helper functions to pin files and json to Pinata
################################################################################


def pin_artwork(artwork_name, artwork_file):
    # Pin the file to IPFS with Pinata
    ipfs_file_hash = pin_file_to_ipfs(artwork_file.getvalue())

    # Build a token metadata file for the artwork
    token_json = {
        "name": artwork_name,
        "image": ipfs_file_hash
    }
    json_data = convert_data_to_json(token_json)

    # Pin the json to IPFS with Pinata
    json_ipfs_hash = pin_json_to_ipfs(json_data)

    return json_ipfs_hash, token_json


def pin_appraisal_report(report_content):
    json_report = convert_data_to_json(report_content)
    report_ipfs_hash = pin_json_to_ipfs(json_report)
    return report_ipfs_hash
################################################################################

showcase_list = ["Images/Christmas.jpeg", "Images/Christmas_v2.jpeg", "Images/Diwali.jpeg", "Images/Kwanzaa.jpeg", "Images/eid_al-fitr.jpeg", "Images/Hanukkah.jpeg", "Images/hanukkah2.jpeg"]

def main_page():

    st.title("NFT SHOWCASE")
    st.markdown(
        """
        <style>
        h1 {
            font-size: 80px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.image(["Images/output1.png", "Images/output2.png"], width=220)
    st.image(showcase_list, width=220)

def page2():

    st.markdown("# A.I. Holiday")
    st.markdown(
        """
        <style>
        h1 {
            font-size: 80px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    text = st.text_input("What image would you like to create and tokenize?")

    ok = st.button("GO!")

    if ok:
        openai.api_key = ""

        nft_image = openai.Image.create(
            prompt=text,
            n=1,
            size="1024x1024"
)

        nft_image_link = nft_image["data"][0]["url"]

    # Read the image from the URL
        url = nft_image_link
        img = imageio.imread(url)

    # Save the image to a file or stream in PNG format
        imageio.imwrite('Images/output1.png', img)

    st.image('Images/output1.png', width=400)
    st.markdown("## Decentralize your Art")
    artwork_name = st.text_input("Name the Art")
    artist_name = st.text_input("Name the Artist")
    token_account = st.selectbox("Select the address you would like to save the Non-Fungible Token to:", options=accounts)
    token_details = st.text_input("Artwork Details", value="Genesis Event for Art")
    # Use the Streamlit `file_uploader` function create the list of digital image file types(jpg, jpeg, or png) that will be uploaded to Pinata.
    file = st.file_uploader("Upload Artwork", type=["jpg", "jpeg", "png"])

    if st.button("Decentralize Artwork"):
        # Use the `pin_artwork` helper function to pin the file to IPFS
        artwork_ipfs_hash, token_json = pin_artwork(artwork_name, file)

        artwork_uri = f"ipfs://{artwork_ipfs_hash}"

        tx_hash = contract.functions.registerArtwork(
            token_account,
            artwork_name,
            artist_name,
            artwork_uri,
            token_json['image']
        ).transact({'from': account, 'gas': 1000000})
        receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        st.write("Transaction receipt mined:")
        st.write(dict(receipt))
        st.write("You can view the pinned metadata file with the following IPFS Gateway Link")
        st.markdown(f"[Artwork IPFS Gateway Link](https://ipfs.io/ipfs/{artwork_ipfs_hash})")
        st.markdown(f"[Artwork IPFS Image Link](https://ipfs.io/ipfs/{token_json['image']})")

    st.markdown("---")
    ################################################################################
    # Use Pinata to bridge the gap to uploading files to IPFS
    ################################################################################

    # st.markdown("## Decentralize your Creation")
    # artwork_name = st.text_input("Name the Art")
    # artist_name = st.text_input("Name the Artist")

    # Use the Streamlit `file_uploader` function create the list of digital image file types(jpg, jpeg, or png) that will be uploaded to Pinata.
    # file = st.file_uploader("Upload Artwork", type=["jpg", "jpeg", "png"])

    # token_account = st.selectbox("Select the address you would like to save the Non-Fungible Token to:", options=accounts)
    # token_details = st.text_input("Artwork Details", value="Genesis Event for Non-Fungible Token")

    # if st.button("Decentralize Artwork"):
    #     # Use the `pin_artwork` helper function to pin the file to IPFS
    #     artwork_ipfs_hash, token_json = pin_artwork(artwork_name, file)

    #     artwork_uri = f"ipfs://{artwork_ipfs_hash}"

    #     tx_hash = contract.functions.registerArtwork(
    #         token_account,
    #         artwork_name,
    #         artist_name,
    #         artwork_uri,
    #         token_json['image']
    #     ).transact({'from': account, 'gas': 1000000})
    #     receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    #     st.write("Transaction receipt mined:")
    #     st.write(dict(receipt))
    #     st.write("You can view the pinned metadata file with the following IPFS Gateway Link")
    #     st.markdown(f"[Artwork IPFS Gateway Link](https://ipfs.io/ipfs/{artwork_ipfs_hash})")
    #     st.markdown(f"[Artwork IPFS Image Link](https://ipfs.io/ipfs/{token_json['image']})")

    # st.markdown("---")

################################################################################
# Display NFT
################################################################################

    # st.markdown(f"### Display Token Identification Details")
    # token_id = st.number_input("Enter the Token ID to display", value=0, step=1)
    # token_uri = st.text_input("Paste Artwork IPFS Image Link")

    # if st.button("Display Token Details"):
    #     st.write(f"The Non-Fungible Token was distributed to {token_account}")
    #     st.write(f"The Non-Fungible Token's tokenURI is {token_uri}")

    
def page3():

    st.markdown("# Kila La Heri")
    st.markdown(
        """
        <style>
        h1 {
            font-size: 80px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    art_database = {
    "Christmas": [
        "Christmas ",
        "0xaC8eB8B2ed5C4a0fC41a84Ee4950F417f67029F0",
        0.5,
        "Images/Christmas.jpeg",
    ],
    "Christmas V2": [
        "Christmas_v2 ",
        "0xaC8eB8B2ed5C4a0fC41a84Ee4950F417f67029F0",
        0.7,
        "Images/Christmas_v2.jpeg",
    ],
    "Diwali": [
        "Diwali ",
        "0xaC8eB8B2ed5C4a0fC41a84Ee4950F417f67029F0",
        0.75,
        "Images/Diwali.jpeg",
    ],
    "Hanukkah": [
        "Hanukkah ",
        "0xaC8eB8B2ed5C4a0fC41a84Ee4950F417f67029F0",
        0.5,
        "Images/Hanukkah.jpeg",
    ],
    "Kawanza": [
        "Kawanza ",
        "0xaC8eB8B2ed5C4a0fC41a84Ee4950F417f67029F0",
        0.9,
        "Images/hanukkah2.jpeg",
    ],
    "Eid Al-Fitr": [
        "Eid Al-Fitr ",
        "0xaC8eB8B2ed5C4a0fC41a84Ee4950F417f67029F0",
        0.9,
        "Images/eid_al-fitr.jpeg",
    ],}
 
    # A list of the the art names
    art_list = ["Christmas", "Christmas V2", "Diwali", "Hanukkah", "Kawanza","Eid Al-Fitr" ]
    name_and_pricing = ["Christmas @ 0.5 Ether", "Christmas V2 @ 0.7 Ether", "Diwali @ 0.75 Ether", "Hanukkah @ 0.5 Ether", "Kawanza @ 0.9 Ether","Eid Al-Fitr @ 0.9 Ether"]
    
    def get_art():
        """Display the database of the art information."""
        db_list = list(art_database.values())
        for art in range(len(art_list)):
            st.image(db_list[art][3], caption= name_and_pricing[art], width=400, output_format="auto")
            st.text(" \n")
        
    st.sidebar.markdown("## Ethereum Address and Amount")
    
    account = generate_account()
    
    st.sidebar.write(account.address)
    
    st.sidebar.write(get_balance(w3, account.address))

    st.sidebar.markdown("## Select Gallery Item for Purchase")
    
    Art = st.sidebar.selectbox("Select from the gallery ", art_list)
    
    units = st.sidebar.number_input('How many would you like to purchase?', min_value=1, step=1)
    
    art = art_database[Art][0]

    price = art_database[Art][2]

    st.sidebar.write(art ,"digital art is valued at ", price, "ETH")
    
    # Fetch the ethereum address from Art Database
    art_address = art_database[Art][1]
    st.sidebar.write(art_address)
    
    cost = units * price

    if st.sidebar.button("Send Transaction"):
        
        transaction_hash = send_transaction(w3, account, art_address, cost)
    
    # Markdown for the transaction hash
        st.sidebar.markdown("#### Validated Transaction Hash")

    # Write the returned transaction hash to the screen
        st.sidebar.write(transaction_hash)

    # Celebrate your successful payment
        st.balloons()
    st_player("https://youtu.be/rM-Ey_Be07U")
    get_art()
    

def page4():

    st.markdown("# The Final Countdown :rocket:")
    st.markdown(
        """
        <style>
        h1 {
            font-size: 80px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    text = st.text_input("What image would you like to create and tokenize?")

    ok = st.button("GO!")

    if ok:
        openai.api_key = ""

        nft_image = openai.Image.create(
            prompt=text,
            n=1,
            size="1024x1024"
)

        nft_image_link = nft_image["data"][0]["url"]

    # Read the image from the URL
        url = nft_image_link
        img = imageio.imread(url)

    # Save the image to a file or stream in PNG format
        imageio.imwrite('Images/output2.png', img)

    st.image('Images/output2.png', width=400)
    

page_names_to_funcs = {
    "NFT SHOWCASE": main_page,
    "A.I. Holiday": page2,
    "Kila La Heri": page3,
    "The Final Countdown": page4,
}


st.sidebar.title("S.A.D. NFTs")

selected_page = st.sidebar.selectbox("Select a page", page_names_to_funcs.keys())

page_names_to_funcs[selected_page]()

# Add a button for users to click to refresh the page
if st.sidebar.button("Refresh"):
    pass
# Add simple black background for easy viewing
st.markdown(
    """
    <style>
    .stApp {
        background-image: url('https://www.solidbackgrounds.com/images/3840x2160/3840x2160-black-solid-color-background.jpg');
        background-size: cover;
        background-repeat: no-repeat;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Display a placeholder message
st.text("Displaying items in the {} category".format(selected_page))