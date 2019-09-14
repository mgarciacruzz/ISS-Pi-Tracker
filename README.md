# ISS Trracker

This is a small python program that keeps track of some of the International Space Station (ISS) statistics.
The code is meant to run in a raspberry pi using the circuit shown below:

![Circuit Diagram](/images/circuit.png)

The tracker provide 4 main screens:

1- Summary - shows the current location of the ISS and the next time it will pass by your location
2- People - shows the current crew members
3 Times - shows the next times that will pass by your location
4- Main menu - allows the navigation between other screns

The final product looks like this:


![Main Menu Screen](/images/MainMenu.jpeg)

![People Screen](/images/People.jpeg)

![Times Screen](/images/Times.jpeg)

![Summary Screen](/images/Summary.jpeg)

## Getting Started

This project uses the PiOled 132x28 screen. Connect it as directed in the Adafruit website.

Assemble the circuit as shown above.

## Built With

* [Python3](https://www.python.org/download/releases/3.0/) - Language
* [RPI.GPIO](https://pypi.org/project/RPi.GPIO/) - Raspberry gpio python library
* [Pillow](https://pillow.readthedocs.io/en/stable/) - Imaging library

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Manuel Garcia** - *Initial work* - [Mgarciacruzz](https://github.com/mgarciacruzz)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
