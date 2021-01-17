import json
import genanki


def main(data):
    anki_name = f'chinese-characters.org'
    model = genanki.Model(
        hash(anki_name + 'model'),
        anki_name,
        fields=[{'name': name} for name in ['Front', 'Back', ]],
        templates=[
            {
                'name': 'Front -> Back'
            },
        ],
    )
    deck = genanki.Deck(hash(anki_name + 'deck'), anki_name)
    for url, values in data.items():
        pass

    package = genanki.Package(deck)
    package.write_to_file(f'{')


if __name__ == '__main__':
    with open('data.json') as json_file:
        data = json.load(json_file)
    main(data)
