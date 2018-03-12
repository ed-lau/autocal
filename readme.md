# Calcium and Sarcomere Trace Analyzer (AutoCal) v.0.2.0

AutoCal is a python program for integrating calcium imaging traces from TI50 Fura-2AM images. 

## Getting Started

To install:
	* Install Python 3.6+
		See instructions on Python website for specific instructions for your operating system
		Python 3.6 should come with the package manager PIP

    * Set up a Virtual Environment for AutoCal
		$ python3.6 -m venv ~/autocal
		$ source ~/autocal/bin/activate

	* Install the packages in the requirements.txt file
		$ pip3 install -r requirements.txt

To run:
	
	* Launch AutoCal (Usage/Help)
		$ python main.py

	* Example usage: python main.py 'data/example.xlsx' -o example_out

	* Deactivate the venv upon completion
		$ deactivate


### Prerequisites

AutoCal requires the following:

```
Python 3.6

```


## Contributing

Please contact us if you wish to contribute, and submit pull requests to us.


## Versioning

We use [SemVer](http://semver.org/) for versioning.


## Authors

* **Edward Lau, PhD** - *Code* - [ed-lau](https://github.com/ed-lau)


See also the list of [contributors](https://github.com/ed-lau/autocal/graphs/contributors) who participated in this project.


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details


## Acknowledgments

* [PurpleBooth](https://github.com/PurpleBooth) for Github Readme template.
