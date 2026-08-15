import json

import httpx

from app.data import BIOS_JSON, batting

ENDPOINT = "https://statsapi.mlb.com/api/v1/people"


def to_bio(person: dict) -> dict:
    return {
        "batter_bam_id": person["id"],
        "number": person["primaryNumber"],
        "position": person["primaryPosition"]["abbreviation"],
        "height": person["height"],
        "weight": person["weight"],
        "birth_date": person["birthDate"],
        "debut_date": person["mlbDebutDate"],
        "throws": person["pitchHand"]["code"],
    }


def main() -> None:
    ids = batting()["batter_bam_id"].unique().sort().to_list()
    response = httpx.get(ENDPOINT, params={"personIds": ",".join(str(i) for i in ids)})
    response.raise_for_status()
    bios = [to_bio(person) for person in response.json()["people"]]
    BIOS_JSON.write_text(json.dumps(bios, indent=2) + "\n")
    print(f"wrote {len(bios)} bios to {BIOS_JSON}")


if __name__ == "__main__":
    main()
