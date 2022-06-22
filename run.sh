echo "comm_size,nelem,time,std" > "time-2.txt"
for s in 4 3 2 1 0.79 0.63 0.5 0.4 0.32 0.25 0.2 0.16 0.13 0.1 0.08 0.063 0.05 0.04 0.032 0.025 0.02 
do
    echo $s
    gmsh -2 square.geo -clscale $s
    mpirun -np 2 python stommel-gpu.py
    mpirun -np 2 python stommel-gpu.py
    mpirun -np 2 python stommel-gpu.py
done