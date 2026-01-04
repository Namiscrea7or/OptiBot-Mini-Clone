import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

ARTICLES_DIR = "articles"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def create_vector_store():
    vs = client.vector_stores.create(
        name="optibot-support-docs"
    )
    print(f"Vector Store ID: {vs.id}")
    return vs.id


def upload_articles(vector_store_id):
    files = [
        os.path.join(ARTICLES_DIR, f)
        for f in os.listdir(ARTICLES_DIR)
        if f.endswith(".md")
    ]

    print(f"Uploading {len(files)} markdown files...")

    uploaded = 0
    for path in files:
        with open(path, "rb") as f:
            file = client.files.create(
                file=f,
                purpose="assistants"
            )

        client.vector_stores.files.create(
            vector_store_id=vector_store_id,
            file_id=file.id
        )

        uploaded += 1

    print(f"Uploaded files: {uploaded}")


if __name__ == "__main__":
    vector_store_id = os.getenv("VECTOR_STORE_ID")

    if not vector_store_id:
        vector_store_id = create_vector_store()
        print("⚠️ Please save VECTOR_STORE_ID to .env and rerun.")
    else:
        upload_articles(vector_store_id)
