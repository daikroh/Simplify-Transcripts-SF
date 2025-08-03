import os
import django

import openai
from dotenv import load_dotenv
from .models import AgendaItem

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def get_embedding(text, model="text-embedding-3-small"):
    response = openai.embeddings.create(input=[text], model=model)
    return response.data[0].embedding


def update_embeddings():
    agenda_items = AgendaItem.objects.filter(embeddings=[])
    for agenda_item in agenda_items:
        try:
            embeddings = get_embedding(f"{agenda_item.title} {agenda_item.summary}")

            if embeddings:
                agenda_item.embeddings = embeddings
                agenda_item.save()
                print(f"Updated record {agenda_item.agenda_id}")
        except Exception as e:
            print(f"Failed for {agenda_item.agenda_id}: {e}")


if __name__ == "__main__":
    update_embeddings()
