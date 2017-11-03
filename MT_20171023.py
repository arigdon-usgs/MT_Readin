import csv
import numpy as np
from datetime import datetime
from obspy.core import Stream, Stats, Trace, UTCDateTime

# Define list of input file names and channels
infile = ['MT00001','MT00002','MT00003','MT00004','MT00005','MT00006','MT00007','MT00008','MT00009','MT00010','MT00011','MT00012','MT00013','MT00014','MT00015']
channels = ['Hx','Hy','Ex','Ey']
station = 'BOU'

# Loop through all of the files
for j in range(0,len(infile)):

	# Define arrays and empty stream for each file
	Hx, Hy, Ex, Ey = [], [], [], []
	Time_stamps = []
	stream = Stream()
	i = 0
	# Read in Data from the individual file
	with open('BOU/' + infile[0] + '.csv','r') as f:
		for line in f:
			# Does not take in the first line that has the comments	
			if i != 0:
				if line[0:1] != '\\':
					col0, col1,col2,col3,col4 = line.split(',')
					Time_stamps.append(float(col0))
					Hx.append(float(col1))
					Hy.append(float(col2))
					Ex.append(float(col3))
					Ey.append(float(col4))

			i += 1

	# Time_stamps reference to beginning of a week
	# Set the correct year, month, and day for Time_stamps
	sttime = UTCDateTime(Time_stamps[0])
	endtime = UTCDateTime(Time_stamps[len(Time_stamps)-1])
	sttime._set_year(2017)
	endtime._set_year(2017)
	sttime._set_month(8)
	endtime._set_month(8)
	sttime._set_day(13 + UTCDateTime(Time_stamps[0]).day)
	endtime._set_day(13 + UTCDateTime(Time_stamps[len(Time_stamps)-1]).day)

	# Define stats 
	stats = Stats()
	stats.starttime = sttime
	stats.station = station
	stats.network = 'NT'
	stats.location = 'R0'
	stats.data_interval = '256Hz'
	stats.delta = .00390625
	stats.data_type = 'variation'

	# Create list of arrays and channel names and intialize counter k
	arrays = [Hx,Hy,Ex,Ey]
	k = 0

	# Loop over channels to create an obspy stream of the data
	for ar in arrays:
		stats.npts = len(ar)
		stats.channel = channels[k]
		ar = np.asarray(ar)
		trace = Trace(ar,stats)
		stream += trace
		trace = None
		k += 1

	# Create a copy of the stream and resample the copied stream to 
	# 10 Hz using the default options of the obspy function resample
	finStream = stream.copy()
	finStream.resample(10.0)

	# Create numpy arrays of the resampled data
	Hx_fin = finStream.select(channel = 'Hx')[0].data
	Hy_fin = finStream.select(channel = 'Hy')[0].data
	Ex_fin = finStream.select(channel = 'Ex')[0].data
	Ey_fin = finStream.select(channel = 'Ey')[0].data

	# Take start time from resampled stream and set a new delta
	sttime = finStream[0].stats.starttime
	delta = .1
	time = []
	# Create a timestamp array for the resampled data using python's datetime library
	for i in range(0,len(finStream[0].data)):
		time = np.append(time,datetime.utcfromtimestamp(sttime + i * delta))

	# Open the output file which I've used the same input file name
	# with '_resampled' added onto the end and placed in a new folder
	with open('Output/BOU2/'+ infile[j] + '_resampled.csv','w') as csvfile:
		# Define the title line that shows what data resides in the respective columns
		title = 'Time, Hx, Hy, Ex, Ey \n'
		csvfile.write(title)

		# create the csv writer object that delimites
		cwriter = csv.writer(csvfile, delimiter = ',', quotechar = ' ', quoting = csv.QUOTE_ALL)

		# Loop over the length of the data and use the csv writer to write the rows
		for i in range(0,len(Hx_fin)):
			row = (UTCDateTime(time[i]),Hx_fin[i],Hy_fin[i],Ex_fin[i],Ey_fin[i])
			cwriter.writerow(row)
