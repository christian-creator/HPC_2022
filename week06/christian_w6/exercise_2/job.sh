rm -r tmp/ 
rm -r translated/
python3 administrator_collector.py -in ../../../../humantest.fsa --tmp_dir tmp --rev_dir rev_comp -out "reverse_complement.fa"
