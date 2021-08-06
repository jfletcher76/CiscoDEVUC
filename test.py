# testing git gg
from dotenv import load_dotenv
load_dotenv()
import os

token=os.getenv("nitradoAccess")
print(token)