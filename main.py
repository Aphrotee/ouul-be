#!/usr/bin/env python3

"""Entry point for the app"""


from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)