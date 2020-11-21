import subprocess
import os
from time import sleep
import progressbar

source_dir = './sites/'

processes = []

number_of_files = len(os.listdir(source_dir))

with progressbar.ProgressBar(max_value=number_of_files) as bar:
	count = 0
	bar.update(count)
	for filename in os.listdir(source_dir):
		while(len(processes) >= 25):
			pops = []
			for index, process in enumerate(processes):
				# If subprocess is not alive
				if process.poll() != None:
					pops.append(index)
				sleep(1)

			if len(pops) > 0:
				for i in sorted(pops, reverse=True):
					count += 1
					bar.update(count)
					del processes[i]

		cmd = 'scrapy runspider driver.py -a file="{}" -s LOG_ENABLED=False'.format(source_dir + filename)
		processes.append(subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE))


	for process in processes:
		process.wait()
		count += 1
		bar.update(count)

print('FINISHED EVERYTHING!!!! =D')