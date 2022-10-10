rm -r tmp/ 
rm -r translated/ 
python3 administrator.py -in ../../../humantest.fsa --tmp_dir tmp/ --out_dir translated/
python3 collector.py -in translated/ -o hum_rev_complement.fa
