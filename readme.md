Calcium and Sarcomere Trace Analyzer (AutoCal) v.0.2.0
======================================================

Requirements:
- Python3.6

Instructions

	* Install Python 3.6+
	See instructions on Python website for specific instructions for your operating system
	Python 3.6 should come with the package manager PIP

    * Set up a Virtual Environment for AutoCal
		$ python3.6 -m venv ~/autocal
		$ source ~/autocal/bin/activate

	* Install the packages in the requirements.txt file
		$ pip3 install -r requirements.txt

Running
	
	* Launch AutoCal (Usage/Help)
		$ python main.py

	* Example usage: python main.py 'data/example.xlsx' -o example_out

	* Deactivate the venv upon completion
		$ deactivate


Input files

	* AutoCal takes in standard Calcium traces from TI50 Fura-2AM imaging. 


Contact: Edward Lau
lau1@stanford.edu