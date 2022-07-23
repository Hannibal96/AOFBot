#!/usr/bin/bash
tasks=`echo */`

for task in ${tasks}
do
	classes=`echo ${task}*/`
	for class in ${classes}
	do

		task_name=`echo ${class} | cut -f1 -d '/'`
		class_name=`echo ${class} | cut -f2 -d '/'`
		name=${task_name}_${class_name}

		num_class_files=`ls ${class}${name}*.png | wc -l`
		other_files=`find ${class} ! -name "${name}*.png" | grep png`
		num_other_files=`ls ${other_files} | wc -l`

		echo '*********************'
		echo ${name} 
		echo Current samples=${num_class_files}
		echo Samples to Rename=${num_other_files}
		echo '*********************'

		
		for file in ${other_files}
		do
			mv ${file} ${class}/${name}_${num_class_files}.png
			num_class_files=$((num_class_files+1))
		done

	done

done


