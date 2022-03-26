import json

if __name__ == '__main__':
    with open ('resources/reconstruction.json') as fd:
        reconstruction = json.load(fd)
        print(reconstruction)
