# maProjects

The code is pretty messy and could probably be rewritten in half the number of lines - the 'feature requests' list changed a lot while I was writing it. it's written for python2.7. You'll need pyqtgraph, pymzml and pyqt4 (and the C++ lib behind it). The setup script should create an entry point called 'advanceXCMS' - just run that from the terminal and t should go. I think pymzml dropped support for python2.7 at some point since I wrote this - let me know if you have trouble with it as i've got the older version stashed away somewhere. There's an R script in there as well that uses XCMS to process data files. Running this script across a directory containing '.mzML' files will produce an output file which is then read into thee GUI. I can give you a quick run-down once I'm back if that's unclear
